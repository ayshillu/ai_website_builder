# This file is temporarily disabled to prevent MongoDB connection errors

"""
from pymongo import MongoClient

# Connect to MongoDB Atlas
client = MongoClient('mongodb+srv://username:password@cluster.mongodb.net/')

# Access your database and collection
db = client['ai_builder_db']
collection = db['websites_collection']

# Example data that would come from the frontend form
form_data = {
    "business_name": "Growthzi Café",
    "location": "Kochi",
    "description": "A cozy coffee shop serving freshly brewed artisan coffee with homemade snacks.",
    "type": "Food & Beverage"
}

# Insert into MongoDB
inserted_document = collection.insert_one(form_data)

print(f"Inserted Document ID: {inserted_document.inserted_id}")

# Close connection
client.close()
"""

# For testing without MongoDB
def test_connection():
    print("MongoDB connection is disabled.")
    return True
