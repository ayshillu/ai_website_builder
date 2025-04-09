
# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi

# uri = "mongodb+srv://ayshaabdulfaizal:mydatabase@ai-builder.fqbgu3d.mongodb.net/?retryWrites=true&w=majority&appName=ai-builder"

# # Create a new client and connect to the server
# client = MongoClient(uri, server_api=ServerApi('1'))

# # Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)

from pymongo import MongoClient

# Connect to MongoDB Atlas
client = MongoClient('mongodb+srv://ayshaabdulfaizal:mydatabase@ai-builder.fqbgu3d.mongodb.net/?retryWrites=true&w=majority&appName=ai-builder')


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
