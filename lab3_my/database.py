from pymongo import MongoClient, ASCENDING

MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "foodapp"

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

categories = db["categories"]
dishes = db["dishes"]
orders = db["orders"]

dishes.create_index([("name", ASCENDING)])
categories.create_index([("name", ASCENDING)], unique=True)
