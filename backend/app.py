from flask import Flask, jsonify, request
from flask_cors import CORS
import processing
import pandas as pd

app = Flask(__name__)
CORS(app)

# Configuration
app.config['DEBUG'] = True  # Enable debug mode for development

# Routes
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Flask backend!"})

@app.route('/get_date', methods=['GET'])
def get_date():
    file = processing.join_files(["Allen Innovation Active Fund - 2022.csv", "Allen Innovation Active Fund - 2023.csv", 
           "Allen Innovation Active Fund - 2024.csv"])
    date = file.iloc[-1]["Date"]

    return {"date": date}

@app.route('/get_traded_tickers', methods=['GET'])
def get_traded_tickers():
    file = processing.join_files(["Allen Innovation Active Fund - 2022.csv", "Allen Innovation Active Fund - 2023.csv", 
           "Allen Innovation Active Fund - 2024.csv"])
    return {"tickers": processing.get_all_traded_tickers(file).tolist()}

# Presplit Adjustments for stock and portfolio
@app.route('/get_shares_over_time', methods=['GET'])
def get_shares_over_time():
    ticker = request.args.get("ticker")
    print(ticker)

    file = processing.join_files(["Allen Innovation Active Fund - 2022.csv", "Allen Innovation Active Fund - 2023.csv", 
           "Allen Innovation Active Fund - 2024.csv"])
    return {"data": processing.stock_shares_over_time(file, ticker)}

@app.route('/get_portfolio', methods=['GET'])
def get_portfolio():
    file = processing.join_files(["Allen Innovation Active Fund - 2022.csv", "Allen Innovation Active Fund - 2023.csv", 
           "Allen Innovation Active Fund - 2024.csv"])
    date = file.iloc[-1]["Date"]
    date = pd.to_datetime(date, format='%m/%d/%y').tz_localize('America/New_York')
    portfolio = processing.holdings_by_date(file)[date]
    total_invested = 0
    for stock in portfolio:
        total_invested += portfolio[stock]["Total_Value"]
    for stock in portfolio:
        portfolio[stock]["Percentage_of_Fund"] = f"{round(portfolio[stock]['Total_Value'] / total_invested * 100, 2)}%"

    output = []
    for stock in portfolio:
        output.append({
            "Stock": stock,
            "Price": f"${portfolio[stock]['Price']}",
            "Shares": portfolio[stock]["Shares"],
            "Total_Value": portfolio[stock]["Total_Value"],
            "Percentage_of_Fund": portfolio[stock]["Percentage_of_Fund"]
        })
    
    sorted_output = sorted(output, key=lambda x: x["Total_Value"], reverse=True)
    return {"data": sorted_output}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
