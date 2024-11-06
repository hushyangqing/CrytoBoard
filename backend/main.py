from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import requests
import json
import time
import numpy as np 
from collections import defaultdict, Counter

app = Flask(__name__)
CORS(app)
coinMarketkey='cd4615ad-0703-4d8d-8d23-5562769f50f6'
# mongodb connection
uri = "mongodb+srv://qyang:13868543625Wu@cluster0.2n4bw.mongodb.net/?retryWrites=true&w=majority&appName=cluster0"
app.config['MONGO_URI'] = uri
try:
    mongo = PyMongo(app)
except Exception as e:
    print("MongoDB connection error:", e)
#scheduler = BackgroundScheduler()

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
top10Crypto = ['BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'USDC', 'XRP', 'DOGE', 'TRX', 'TON']
start_time = datetime.now()

###Price###
def fetch_and_store_price():
    global start_time, crypto_history, top10Crypto

    # For testing, run this only for 10 minutes
    if datetime.now() > start_time + timedelta(minutes=10):
        scheduler.remove_job('price_fetch_job')
        # After 10 minutes, store history and reset
        store_history()
        return

    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
        'start': '1',
        'limit': '20',
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
    top10Crypto = [crypto['symbol'] for crypto in data['data'][:10]]
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

#scheduler.add_job(fetch_and_store_price, 'interval', minutes=5, id='price_fetch_job')
#scheduler.start()

###API Endpoints###
@app.route('/currentPrice/<symbol>', methods=['GET'])
def get_price(symbol):
    price_collection = mongo.cx['info']['price']
    result = price_collection.find_one({"symbol": symbol.upper()})
    if result:
        result["_id"] = str(result["_id"])
        return jsonify(result)
    else:
        return jsonify({"price": -1}), 404
    
@app.route('/top10_current_prices', methods=['GET'])
def get_all_current_prices():
    price_collection = mongo.cx['info']['price']
    prices = price_collection.find({"symbol": {"$in": top10Crypto}})
    return jsonify([{"symbol": price["symbol"], "price": price["price"]} for price in prices])

@app.route('/historyPrice/<symbol>', methods=['GET'])
def get_history(symbol):
    history_collection = mongo.cx['info']['history_price']
    result = history_collection.find_one({"symbol": symbol.upper()})
    if result and "history" in result:
        return jsonify(result["history"])
    else:
        return jsonify({"error": "No historical data found for this symbol"}), 404

@app.route('/top10_historyPrice', methods=['GET'])
def get_all_history_top10():
    history_collection = mongo.cx['info']['history_price']
    history_data = history_collection.find({"symbol": {"$in": top10Crypto}})
    all_history = {doc["symbol"]: doc["history"] for doc in history_data}
    return jsonify(all_history)

@app.route('/top10_symbols', methods=['GET'])
def get_top10_symbols():
    return jsonify(top10Crypto)


###Statistics###
newsSource = ["BBC", "NYTimes"]
socialMedias=["X"]

def calculate_growth_rate(today_count, yesterday_count):
    if yesterday_count == 0:
        return None if today_count == 0 else float('inf')  
    return ((today_count - yesterday_count) / yesterday_count)

def get_cryptocurrency_counts(collection, start_time, end_time):
    query = {
        "timestamp": {"$gte": start_time, "$lt": end_time}
    }
    documents = list(collection.find(query))
    document_count = len(documents)
    print(f"Documents found in range {start_time} to {end_time}: {document_count}")
    crypto_counts = defaultdict(int)
    for doc in documents:
        for coin in doc.get("relatedCoins", []):
            for symbol, count in coin.items():
                crypto_counts[symbol] += 1
    return crypto_counts

def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    if norm_vec1 == 0 or norm_vec2 == 0:
        return 0
    return dot_product / (norm_vec1 * norm_vec2)
###API Endpoints###
@app.route('/statistics/growth_rate', methods=['GET'])
def get_growth_rate():
    end_time = int(datetime.now().timestamp())
    start_today = end_time - 86400  # 24 hours ago
    start_yesterday = end_time - 2 * 86400  # 48 hours ago

    today_counts = defaultdict(int)
    yesterday_counts = defaultdict(int)

    for source in newsSource:
        collection = mongo.cx['News'][source]
        today_counts_source = get_cryptocurrency_counts(collection, start_today, end_time)
        yesterday_counts_source = get_cryptocurrency_counts(collection, start_yesterday, start_today)

        for symbol, count in today_counts_source.items():
            today_counts[symbol] += count
        for symbol, count in yesterday_counts_source.items():
            yesterday_counts[symbol] += count

    for source in socialMedias:
        collection = mongo.cx['SocialMedia'][source]
        today_counts_source = get_cryptocurrency_counts(collection, start_today, end_time)
        yesterday_counts_source = get_cryptocurrency_counts(collection, start_yesterday, start_today)

        for symbol, count in today_counts_source.items():
            today_counts[symbol] += count
        for symbol, count in yesterday_counts_source.items():
            yesterday_counts[symbol] += count
    
    growth_rates = []
    for symbol in top10Crypto:
        today_count = today_counts[symbol]
        yesterday_count = yesterday_counts[symbol]
        growth_rate = calculate_growth_rate(today_count, yesterday_count)
        growth_rates.append({symbol: growth_rate})

    return jsonify(growth_rates)

@app.route('/statistics/growth_rate_news/<news>', methods=['GET'])
def get_growth_rate_news(news):
    if news not in newsSource:
        return jsonify({"error": "Invalid news source"}), 400
    
    end_time = int(datetime.now().timestamp())
    start_today = end_time - 86400  # 24 hours ago
    start_yesterday = end_time - 2 * 86400

    collection = mongo.cx["News"][news]
    today_counts = get_cryptocurrency_counts(collection, start_today, end_time)
    yesterday_counts = get_cryptocurrency_counts(collection, start_yesterday, start_today)

    growth_rates = []
    for symbol in top10Crypto:
        today_count = today_counts[symbol]
        yesterday_count = yesterday_counts[symbol]
        growth_rate = calculate_growth_rate(today_count, yesterday_count)
        growth_rates.append({symbol: growth_rate})

    return jsonify(growth_rates)

@app.route('/statistics/growth_rate_socialMedia/<media>', methods=['GET'])
def get_growth_rate_socialMedia(media):
    if media not in socialMedias:
        return jsonify({"error": "Invalid socialMedia source"}), 400
    
    end_time = int(datetime.now().timestamp())
    start_today = end_time - 86400  # 24 hours ago
    start_yesterday = end_time - 2 * 86400

    collection = mongo.cx["SocialMedia"][media]
    today_counts = get_cryptocurrency_counts(collection, start_today, end_time)
    yesterday_counts = get_cryptocurrency_counts(collection, start_yesterday, start_today)

    growth_rates = []
    for symbol in top10Crypto:
        today_count = today_counts[symbol]
        yesterday_count = yesterday_counts[symbol]
        growth_rate = calculate_growth_rate(today_count, yesterday_count)
        growth_rates.append({symbol: growth_rate})

    return jsonify(growth_rates)

@app.route('/statistics/bestMedia', methods=['GET'])
def get_best_media():
    end_time = int(datetime.now().timestamp())
    start_time = end_time - 86400 
    social_media_collection = mongo.cx["SocialMedia"][socialMedias[0]]
    social_counts = get_cryptocurrency_counts(social_media_collection, start_time, end_time)
    social_vector = [social_counts.get(symbol, 0) for symbol in top10Crypto]

    best_similarity = 0
    best_source = None

    for source in newsSource:
        news_collection = mongo.cx["News"][source]
        news_counts = get_cryptocurrency_counts(news_collection, start_time, end_time)
        news_vector = [news_counts.get(symbol, 0) for symbol in top10Crypto]

        similarity = cosine_similarity(social_vector, news_vector)
        if similarity > best_similarity:
            best_similarity = similarity
            best_source = source
    
    if best_source:
        news_collection = mongo.cx["News"][best_source]
        articles = list(news_collection.find(
            {"timestamp": {"$gte": start_time, "$lt": end_time}},
            {"_id": 0, "headline": 1, "url": 1}
        ))

        return jsonify({
            "best_source": best_source,
            "similarity_score": best_similarity,
            "articles": articles
        })
    else:
        return jsonify({"error": "No matching news source found"}), 404

###Chart###
def get_article_count_and_word_frequency(collection, start_time, end_time):
    query = {
        "timestamp": {"$gte": start_time, "$lt": end_time}
    }
    documents = list(collection.find(query))
    document_count = len(documents)
    print(f"Documents found in range {start_time} to {end_time}: {document_count}")
    article_count = defaultdict(int)
    word_frequency = Counter()

    for doc in documents:
        for coin in doc.get("relatedCoins", []):
            for symbol, count in coin.items():
                if symbol in top10Crypto:
                    article_count[symbol] += 1 
                    word_frequency[symbol] += count
    
    return article_count, word_frequency

@app.route('/chart_data', methods=['GET'])
def get_chart_data():
    start_time_str = request.args.get("start_time")
    end_time_str = request.args.get("end_time")

    if start_time_str and end_time_str:
        try:
            start_time = int(datetime.fromisoformat(start_time_str).timestamp())
            end_time = int(datetime.fromisoformat(end_time_str).timestamp())
        except ValueError:
            return jsonify({"error": "Invalid date format. Use ISO format: YYYY-MM-DDTHH:MM:SS"}), 400
    else:
        end_time = int(datetime.now().timestamp())
        start_time = end_time - 86400 

    chart_data = []

    for source in newsSource:
        collection = mongo.cx["News"][source]
        article_count, word_frequency = get_article_count_and_word_frequency(collection, start_time, end_time)

        # Structure the data
        source_data = {
            source: {
                "numberOfArticle": [{symbol: count} for symbol, count in article_count.items()],
                "wordFrequency": dict(word_frequency)
            }
        }
        chart_data.append(source_data)
    for source in socialMedias:
        collection = mongo.cx["SocialMedia"][source]
        article_count, word_frequency = get_article_count_and_word_frequency(collection, start_time, end_time)

        # Structure the data
        source_data = {
            source: {
                "numberOfArticle": [{symbol: count} for symbol, count in article_count.items()],
                "wordFrequency": dict(word_frequency)
            }
        }
        chart_data.append(source_data)
    return jsonify(chart_data)

###News Search###
@app.route('/news/search', methods=['GET'])
def search_news():
    crypto_name = request.args.get('crypto_name')
    start_time_str = request.args.get('start_time')
    end_time_str = request.args.get('end_time')

    if not crypto_name:
        return jsonify({"error": "Please provide a cryptocurrency name"}), 400
    crypto_name_lower = crypto_name.strip().lower()
    crypto_symbol = None

    for name, symbol in nameMapping.items():
        if name.lower() == crypto_name_lower or symbol.lower()==crypto_name_lower:
            crypto_symbol = symbol
            break
    if not crypto_symbol:
        return jsonify({"error": "Cryptocurrency not found"}), 404
    
    if start_time_str and end_time_str:
        try:
            start_time = int(datetime.fromisoformat(start_time_str).timestamp())
            end_time = int(datetime.fromisoformat(end_time_str).timestamp())
        except ValueError:
            return jsonify({"error": "Invalid date format. Use ISO format: YYYY-MM-DDTHH:MM:SS"}), 400
    else:
        end_time = int(datetime.now().timestamp())
        start_time = end_time - 86400 

    results = []
    for source in newsSource:
        collection = mongo.cx["News"][source]
        articles = list(collection.find(
            {   "timestamp": {"$gte": start_time, "$lt": end_time},
                "relatedCoins": {"$elemMatch": {crypto_symbol: {"$exists": True}}}
            },
            {"_id": 0, "headline": 1, "url": 1, "timestamp": 1}
        ))

        for article in articles:
            article['source'] = source  
            results.append(article)

    results.sort(key=lambda x: x['timestamp'], reverse=True)
    if not results:
        return jsonify({"message": f"No articles found for {crypto_name}"}), 404

    return jsonify(results)

if __name__ == '__main__':
    #fetch_and_store_price()
    app.run(debug=True)