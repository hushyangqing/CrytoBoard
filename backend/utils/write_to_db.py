from pymongo import MongoClient
import json

# MongoDB connection URI
uri = "mongodb+srv://qyang:13868543625Wu@cluster0.2n4bw.mongodb.net/?retryWrites=true&w=majority&appName=cluster0"
client = MongoClient(uri)

db = client["News"]
db2 = client["SocialMedia"]
collection1 = db["Fox"]  # Change this if needed
collection2 = db["NYTimes"]
collection3 = db2["X"]
# Load the JSON data
# with open("crypto_articles_analysis.json", "r") as file:
#     data1 = json.load(file)

# with open("nyt_crypto_articles_filtered.json", "r", encoding="utf-8") as file:
#     data2 = json.load(file)

with open("crypto_tweets.json", "r", encoding="utf-8") as file:
    data3 = json.load(file)

# Insert data into the collection
# result1 = collection1.insert_many(data1)
# result2 = collection2.insert_many(data2)
result3 = collection3.insert_many(data3)

# Confirm insertion
# print(f"Inserted {len(result1.inserted_ids)} documents into the collection.")
# print(f"Inserted {len(result2.inserted_ids)} documents into the collection.")
print(f"Inserted {len(result3.inserted_ids)} documents into the collection.")