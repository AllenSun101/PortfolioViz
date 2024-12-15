from flask import Flask, jsonify, request
from flask_cors import CORS
import processing

app = Flask(__name__)
CORS(app)

# Configuration
app.config['DEBUG'] = True  # Enable debug mode for development

# Routes
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Flask backend!"})

@app.route('/get_traded_tickers', methods=['GET'])
def get_traded_tickers():
    file = processing.join_files(["Allen Innovation Active Fund - 2022.csv", "Allen Innovation Active Fund - 2023.csv", 
           "Allen Innovation Active Fund - 2024.csv"])
    return {"tickers": processing.get_all_traded_tickers(file).tolist()}

# Presplit Adjustments
# Current Portfolio Table & Backend Clean Up
@app.route('/get_shares_over_time', methods=['GET'])
def get_shares_over_time():
    ticker = request.args.get("ticker")
    print(ticker)

    file = processing.join_files(["Allen Innovation Active Fund - 2022.csv", "Allen Innovation Active Fund - 2023.csv", 
           "Allen Innovation Active Fund - 2024.csv"])
    return {"data": processing.stock_shares_over_time(file, ticker)}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
