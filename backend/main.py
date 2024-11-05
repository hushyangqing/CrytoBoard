from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import requests
import json

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
scheduler.start()

crytoCurrency = {'BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'USDC', 'XRP', 'DOGE', 'TRX', 'TON'}
nameMapping = {'Bitcoin':'BTC',
               'Ethereum':'ETH',
               'Tether': 'USDT',
               'BNB':'BNB',
               'Solana': 'SOL',
               'USDC':'USDC',
               'XRP':'XRP',
               'Dogecoin':'DOGE',
               'TRON':'TRX',
               'Toncoin':'TON'}

def update_bitcoin_price(): 
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
    'start':'1',
    'limit':'10',
    'convert':'USD'
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
    collection = mongo.cx['info']['price']
    for crypto in data['data']:
        crypto_entry = {
            "id": crypto['id'],
            "name": crypto['name'],
            "symbol": crypto['symbol'],
            "slug": crypto['slug'],
            "price": crypto['quote']['USD']['price'],
            "last_updated": crypto['quote']['USD']['last_updated']
        }
        collection.update_one(
            {"symbol": crypto['symbol']},
            {"$set": crypto_entry},
            upsert=True
        )

    print("Cryptocurrency data updated.")

scheduler.add_job(update_bitcoin_price, 'interval', days=1)

if __name__ == '__main__':
    update_bitcoin_price()
    app.run(debug=True)