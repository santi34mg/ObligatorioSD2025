from pymongo import MongoClient
import os

client = MongoClient(os.getenv("MONGO_URL", "mongodb://mongo:27017"))
db = client["umshare"]
collection = db["materials"]

def insert_metadata(data):
    collection.insert_one(data)
