from pymongo import MongoClient

client = MongoClient("mongodb://mongo:27017/")
db = client["budget_db"]
incomes_collection = db["incomes"]
costs_collection = db["costs"]
