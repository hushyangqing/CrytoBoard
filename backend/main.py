from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import requests
import json
import time

app = Flask(__name__)
CORS(app)
coinMarketkey='cd4615ad-0703-4d8d-8d23-5562769f50f6'
# mongodb connection
uri = "mongodb+srv://qyang:13868543625@cluster0.2n4bw.mongodb.net/?retryWrites=true&w=majority&appName=cluster0"
app.config['MONGO_URI'] = uri
try:
    mongo = PyMongo(app)
except Exception as e:
    print("MongoDB connection error:", e)
scheduler = BackgroundScheduler()

crytoCurrency = {'BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'USDC', 'XRP', 'DOGE', 'TRX', 'TON', 'ADA', 'SHIB', 'AVAX', 'BCH', 'LINK', 'DOT', 'LEO', 'SUI', 'DAI', 'LTC'}
nameMapping = {'Bitcoin':'BTC',
               'Ethereum':'ETH',
               'Tether': 'USDT',
               'BNB':'BNB',
               'Solana': 'SOL',
               'USDC':'USDC',
               'XRP':'XRP',
               'Dogecoin':'DOGE',
               'TRON':'TRX',
               'Toncoin':'TON',
               'Cardano':'ADA',
               'Shiba Inu':'SHIB',
               'Avalanche': 'AVAX',
               'Bitcoin Cash': 'BCH',
               'Chainlink':'LINK',
               'Polkadot':'DOT',
               'UNUS SED LEO':'LEO',
               'Sui':'SUI',
               'Dai':'DAI',
               'Litecoin':'LTC'}

crypto_history = {}

start_time = datetime.now()

def fetch_and_store_price():
    global start_time, crypto_history

    # For testing, run this only for 10 minutes
    if datetime.now() > start_time + timedelta(minutes=10):
        scheduler.remove_job('price_fetch_job')
        # After 10 minutes, store history and reset
        store_history()
        return

    # Fetch cryptocurrency data from CoinMarketCap API
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
        'start': '1',
        'limit': '10',
        'convert': 'USD'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': coinMarketkey
    }
    response = requests.get(url, headers=headers, params=parameters)
    
    if response.status_code != 200:
        print("Failed to fetch data from API.")
        return
    
    data = response.json()
    price_collection = mongo.cx['info']['price']
    history_collection = mongo.cx['info']['history_price']

    for crypto in data['data']:
        symbol = crypto['symbol']
        if symbol in crytoCurrency:
            latest_price = {
                "symbol": symbol,
                "name": crypto['name'],
                "slug": crypto['slug'],
                "price": crypto['quote']['USD']['price'],
                "last_updated": crypto['quote']['USD']['last_updated']
            }
            price_collection.update_one(
                {"symbol": symbol},
                {"$set": latest_price},
                upsert=True
            )
            if symbol not in crypto_history:
                crypto_history[symbol] = [] 
            crypto_history[symbol].append({
                "price": latest_price["price"],
                "timestamp": latest_price["last_updated"]
            })

def store_history():
    history_collection = mongo.cx['info']['history_price']
    for symbol, history in crypto_history.items():
        history_collection.update_one(
            {"symbol": symbol},
            {"$set": {"history": history}},
            upsert=True
        )
    print("Historical price data stored in MongoDB.")
    crypto_history.clear() 

scheduler.add_job(fetch_and_store_price, 'interval', minutes=5, id='price_fetch_job')
scheduler.start()

if __name__ == '__main__':
    #fetch_and_store_price() unmark it in real case
    app.run(debug=True)