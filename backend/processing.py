import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# {"2022-02-22": {"STOCK": {Shares: 10, Price: ClosingPrice, Value: Value}}}

def get_all_traded_tickers(file):
    file['Ticker'] = file['Ticker'].replace('FB', 'META')
    return file['Ticker'].unique()


def process_dataset(file):
    events_history = {}
    price_history = {}

    file['Ticker'] = file['Ticker'].replace('FB', 'META')

    # Get list of unique stocks, append split and dividend history
    all_stocks = file['Ticker'].unique()
    
    for index, stock in enumerate(all_stocks):
        stock_data = yf.Ticker(stock)
        actions = stock_data.actions

        # only need actions after 2020
        actions = pd.DataFrame(actions, index=pd.to_datetime(actions.index))
        recent_actions = actions[actions.index > '2020-01-01 00:00:00']

        events_history[stock] = recent_actions

        price_data = yf.download(stock, start="2020-01-01")
        closing_prices = price_data['Close']
        price_history[stock] = closing_prices    

    return file, events_history, price_history


def holdings_by_date(file):
    file, events_history, price_history = process_dataset(file)

    portfolio_history = {}

    date = file.iloc[0]["Date"]
    date = pd.to_datetime(date, format='%m/%d/%y').tz_localize('America/New_York')

    for index, row in file.iterrows():
        row_date = pd.to_datetime(row["Date"], format='%m/%d/%y').tz_localize('America/New_York')
        if row_date != date:
            portfolio_history[row_date] = {k: v for k, v in portfolio_history[date].items() if v["Shares"] != 0}

            # Attach prices and total value
            for holding_ticker in portfolio_history[row_date]:
                # Handle Delisted
                if holding_ticker == "TWTR":
                    portfolio_history[row_date][holding_ticker]["Price"] = 0
                    portfolio_history[row_date][holding_ticker]["Total_Value"] = 0
                else:
                    portfolio_history[row_date][holding_ticker]["Price"] = round(price_history[holding_ticker][
                        row_date.strftime("%Y-%m-%d")], 2)
                    portfolio_history[row_date][holding_ticker]["Total_Value"] = round(portfolio_history[
                        row_date][holding_ticker]["Price"] * portfolio_history[row_date][holding_ticker]["Shares"], 2)

            # Handle GE/GEV spinoff
            if row_date.strftime("%Y-%m-%d") == "2024-04-02":
                portfolio_history[row_date]["GEV"] = {"Shares": int(portfolio_history[row_date]["GE"]["Shares"] / 4)}

            # Check for splits and dividends in days since last
            for holding_ticker in portfolio_history[row_date]:
                events = events_history[holding_ticker]
                date_between = date + timedelta(days=1)
                while date_between <= row_date:
                    if date_between in events.index:
                        split_info = events.loc[date_between]
                        if split_info['Stock Splits'] > 0:
                            portfolio_history[row_date][holding_ticker]["Shares"] *= int(split_info['Stock Splits'])
                    date_between += timedelta(days=1)

            date = row_date

        # Add/subtract from unresolved to account for cost basis and current profit/loss
        ticker = row["Ticker"].strip()
        if row["Buy/Sell"] == "BUY":
            if row_date not in portfolio_history:
                portfolio_history[row_date] = {ticker : {"Shares": row["Shares"]}}

                # Handle Delisted
                if ticker == "TWTR":
                    portfolio_history[row_date][ticker]["Price"] = 0
                    portfolio_history[row_date][ticker]["Total_Value"] = 0
                else:
                    portfolio_history[row_date][ticker]["Price"] = round(price_history[ticker][
                        row_date.strftime("%Y-%m-%d")], 2)
                    portfolio_history[row_date][ticker]["Total_Value"] = round(portfolio_history[
                        row_date][ticker]["Price"] * portfolio_history[row_date][ticker]["Shares"], 2)
            elif ticker not in portfolio_history[row_date]:
                portfolio_history[row_date][ticker] = {"Shares": row["Shares"]}
                # Handle Delisted
                if ticker == "TWTR":
                    portfolio_history[row_date][ticker]["Price"] = 0
                    portfolio_history[row_date][ticker]["Total_Value"] = 0
                else:
                    portfolio_history[row_date][ticker]["Price"] = round(price_history[ticker][
                        row_date.strftime("%Y-%m-%d")], 2)
                    portfolio_history[row_date][ticker]["Total_Value"] = round(portfolio_history[
                        row_date][ticker]["Price"] * portfolio_history[row_date][ticker]["Shares"], 2)
            else:
                portfolio_history[row_date][ticker]["Shares"] += row["Shares"]
                # Handle Delisted
                if ticker == "TWTR":
                    portfolio_history[row_date][ticker]["Total_Value"] = 0
                else:
                    portfolio_history[row_date][ticker]["Total_Value"] = round(portfolio_history[
                        row_date][ticker]["Price"] * portfolio_history[row_date][ticker]["Shares"], 2)
        else:
            portfolio_history[row_date][ticker]["Shares"] -= row["Shares"]
            # Handle Delisted
            if ticker == "TWTR":
                portfolio_history[row_date][ticker]["Total_Value"] = 0
            else:
                portfolio_history[row_date][ticker]["Total_Value"] = round(portfolio_history[
                    row_date][ticker]["Price"] * portfolio_history[row_date][ticker]["Shares"], 2)

    return portfolio_history


def join_files(files):
    spreadsheet = pd.DataFrame()
    for file in files:
        df = pd.read_csv(file)
        spreadsheet = pd.concat([spreadsheet, df], ignore_index=True)
    
    return spreadsheet


def stock_shares_over_time(file, ticker):
    file['Ticker'] = file['Ticker'].replace('FB', 'META')

    stock_data = yf.Ticker(ticker)
    actions = stock_data.actions

    # only need actions after 2020
    actions = pd.DataFrame(actions, index=pd.to_datetime(actions.index))
    recent_actions = actions[actions.index > '2020-01-01 00:00:00']

    date = file.iloc[0]["Date"]
    date = pd.to_datetime(date, format='%m/%d/%y').tz_localize('America/New_York')

    shares = {}

    for index, row in file.iterrows():
        row_date = pd.to_datetime(row["Date"], format='%m/%d/%y').tz_localize('America/New_York')
        if row_date != date:
            if date not in shares:
                shares[row_date] = 0
            else:
                shares[row_date] = shares[date]

            # Handle GE/GEV spinoff
            if ticker == "GEV" and row_date.strftime("%Y-%m-%d") == "2024-04-02":
                portfolio_history = holdings_by_date(file)
                if portfolio_history[row_date]["GE"] is not None:
                    shares[row_date] = int(portfolio_history[row_date]["GE"]["Shares"] / 4)

            # Check for splits in days since last
            date_between = date + timedelta(days=1)
            while date_between <= row_date:
                if date_between in recent_actions.index:
                    split_info = recent_actions.loc[date_between]
                    if split_info['Stock Splits'] > 0:
                        shares[row_date] *= int(split_info['Stock Splits'])
                date_between += timedelta(days=1)

            date = row_date

        row_ticker = row["Ticker"].strip()
        if row_ticker == ticker:
            if row["Buy/Sell"] == "BUY":
                if row_date not in shares:
                    shares[row_date] = row["Shares"]
                else:
                    shares[row_date] += row["Shares"]
            else:
                shares[row_date] -= row["Shares"]

    data = yf.download(ticker, start="2020-01-01")
    closing_prices = data['Close']
    shares_over_time = []
    for date in shares:
        current_shares = shares[date]
        price = closing_prices[date.strftime("%Y-%m-%d")]
        shares_over_time.append({"Date": date.strftime("%Y-%m-%d"), "Shares": current_shares, "Price": round(price, 2)})
    
    return shares_over_time

#file = join_files(["Allen Innovation Active Fund - 2022.csv", "Allen Innovation Active Fund - 2023.csv", 
#           "Allen Innovation Active Fund - 2024.csv"])
#print(holdings_by_date(file))
