import tweepy
from datetime import datetime
import json

# Twitter API credentials (use API v2 bearer token)
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAPglxQEAAAAAikdB0K0EQwX2KovpHuRdbU6KX2M%3DZczJhc6xnl5cZ4TI01FXPFLHbUBXjwDkPcKVneFlciO04Ot5BK"

# Cryptocurrency-related keywords
CRYPTO_KEYWORDS = ['Bitcoin', 'Ethereum', 'crypto', 'blockchain', 'BTC', 'ETH', 'USDT']

# Authenticate with Twitter API v2
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# Function to fetch tweets
def fetch_crypto_tweets():
    query = " OR ".join(CRYPTO_KEYWORDS)  # Combine keywords with OR operator
    max_results = 30  # Define the number of tweets to fetch (adjust as needed)

    try:
        # Search for recent tweets
        response = client.search_recent_tweets(
            query=query,
            max_results=max_results,
            tweet_fields=["id", "text", "created_at", "public_metrics"],
        )

        if not response.data:
            print("No tweets found.")
            return []

        all_tweets = []

        for tweet in response.data:
            try:
                timestamp = int(tweet.created_at.timestamp())  # Convert datetime to Unix timestamp
                crypto_counts = extract_related_coins(tweet.text)

                # Skip tweets without crypto-related content
                if not crypto_counts:
                    continue

                # Generate tweet URL
                source_url = f"https://twitter.com/user/status/{tweet.id}"

                tweet_data = {
                    "title": tweet.text[:50] + "...",  # Use first 50 characters of the tweet as title
                    "headline": tweet.text,
                    "timestamp": timestamp,
                    "crypto_counts": crypto_counts,
                    "source_url": source_url  # Add tweet link
                }

                # Print fetched tweet data
                print(f"Tweet fetched:")
                print(f"  Title: {tweet_data['title']}")
                print(f"  Headline: {tweet_data['headline'][:100]}...")
                print(f"  Timestamp: {tweet_data['timestamp']}")
                print(f"  Crypto Counts: {tweet_data['crypto_counts']}")
                print(f"  Source URL: {tweet_data['source_url']}")
                print("-" * 50)

                all_tweets.append(tweet_data)
            except Exception as e:
                print(f"Error processing tweet: {e}")

        # Save all tweets to a JSON file
        save_to_json(all_tweets, "crypto_tweets.json")

    except Exception as e:
        print(f"Error fetching tweets: {e}")

# Function to tag related coins
def extract_related_coins(text):
    nameMapping = {
        'Bitcoin': 'BTC',
        'Ethereum': 'ETH',
        'Tether': 'USDT',
        'BNB': 'BNB',
        'Solana': 'SOL',
        'USDC': 'USDC',
        'XRP': 'XRP',
        'Dogecoin': 'DOGE',
        'TRON': 'TRX',
        'Toncoin': 'TON',
        'Cardano': 'ADA',
        'Shiba Inu': 'SHIB',
        'Avalanche': 'AVAX',
        'Bitcoin Cash': 'BCH',
        'Chainlink': 'LINK',
        'Polkadot': 'DOT',
        'UNUS SED LEO': 'LEO',
        'Sui': 'SUI',
        'Dai': 'DAI',
        'Litecoin': 'LTC',
    }
    related_coins = {}
    for name, symbol in nameMapping.items():
        if name.lower() in text.lower() or symbol.lower() in text.lower():
            related_coins[symbol] = related_coins.get(symbol, 0) + 1
    return related_coins

# Function to save data to JSON
def save_to_json(data, filename):
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving to JSON: {e}")

# Run the fetcher
if __name__ == "__main__":
    fetch_crypto_tweets()
