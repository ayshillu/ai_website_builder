# db.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["ai_website_builder"]
users_collection = db["users"]
websites_collection = db["websites_collection"]