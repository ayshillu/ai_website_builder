"""
MongoDB utility functions for the AI Web Builder application.
This module provides helper functions to interact with MongoDB Atlas.
"""
from django.conf import settings
from bson import ObjectId
import json
from datetime import datetime
from pymongo import MongoClient
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get MongoDB connection from settings or environment
MONGO_URI = getattr(settings, 'MONGO_URI', os.getenv('MONGO_URI'))
logger.info(f"MongoDB URI: {MONGO_URI[:20]}...") # Log partial URI for security

# Database name to use
DB_NAME = "ai_builder_db"
COLLECTION_NAME = "websites_collection"

# Initialize MongoDB client
try:
    logger.info(f"Attempting to connect to MongoDB Atlas with database: {DB_NAME} and collection: {COLLECTION_NAME}...")
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Verify connection with a ping
    mongo_client.admin.command('ping')
    # Explicitly specify the database name
    mongo_db = mongo_client[DB_NAME]
    db_name = mongo_db.name
    logger.info(f"MongoDB Atlas connection successful. Database: {db_name}")
    print(f"MongoDB Atlas connection successful. Database: {db_name}")
except Exception as e:
    logger.error(f"MongoDB Atlas connection error: {e}")
    print(f"MongoDB Atlas connection error: {e}")
    mongo_db = None

def get_collection(collection_name=None):
    """
    Get a MongoDB collection by name.
    
    Args:
        collection_name (str, optional): Name of the collection. If None, uses default COLLECTION_NAME
        
    Returns:
        Collection object or None if MongoDB is not connected
    """
    if mongo_db is None:
        logger.error(f"Cannot get collection: MongoDB not connected")
        return None
    
    # Use the default collection name if none is provided
    if collection_name is None:
        collection_name = COLLECTION_NAME
        
    logger.info(f"Accessing collection: {collection_name}")
    return mongo_db[collection_name]

def save_website_data(website_data):
    """
    Save website data to MongoDB Atlas.
    
    Args:
        website_data (dict): Website data to save
        
    Returns:
        str: ID of the inserted document or None if failed
    """
    collection = get_collection()
    if collection is None:
        logger.error("Cannot save website data: MongoDB collection not available")
        return None
    
    # Add timestamp if not present
    if 'created_at' not in website_data:
        website_data['created_at'] = datetime.now()
    if 'updated_at' not in website_data:
        website_data['updated_at'] = datetime.now()
    
    # Log the data being saved (excluding large content)
    log_data = {k: v for k, v in website_data.items() if k != 'content'}
    logger.info(f"Saving website data: {log_data}")
    
    # Insert the document
    try:
        # Log MongoDB collection details
        logger.info(f"Using collection: {collection.name} in database: {collection.database.name}")
        
        result = collection.insert_one(website_data)
        logger.info(f"Website data inserted: {result.inserted_id}")
        if result.inserted_id:
            return str(result.inserted_id)
        return None
    except Exception as e:
        logger.error(f"Error saving website data: {e}")
        # Print the error for immediate visibility
        print(f"MongoDB Error: {e}")
        return None

def get_website_by_id(website_id):
    """
    Get website data by ID from MongoDB Atlas.
    
    Args:
        website_id (str): Website ID
        
    Returns:
        dict: Website data or None if not found
    """
    collection = get_collection()
    if collection is None:
        return None
    
    try:
        # Convert string ID to ObjectId
        object_id = ObjectId(website_id)
        website = collection.find_one({'_id': object_id})
        
        # Convert ObjectId to string for JSON serialization
        if website and '_id' in website:
            website['_id'] = str(website['_id'])
        
        logger.info(f"Website data retrieved: {website_id}")
        return website
    except Exception as e:
        logger.error(f"Error retrieving website: {e}")
        return None

def update_website(website_id, update_data):
    """
    Update website data in MongoDB Atlas.
    
    Args:
        website_id (str): Website ID
        update_data (dict): Data to update
        
    Returns:
        bool: True if update was successful, False otherwise
    """
    collection = get_collection()
    if collection is None:
        return False
    
    try:
        # Add updated timestamp
        update_data['updated_at'] = datetime.now()
        
        # Convert string ID to ObjectId
        object_id = ObjectId(website_id)
        result = collection.update_one(
            {'_id': object_id},
            {'$set': update_data}
        )
        
        logger.info(f"Website data updated: {website_id}")
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Error updating website: {e}")
        return False

def get_all_websites(user_id=None, limit=20, skip=0):
    """
    Get all websites from MongoDB Atlas, optionally filtered by user_id.
    
    Args:
        user_id (str, optional): User ID to filter by
        limit (int, optional): Maximum number of results to return
        skip (int, optional): Number of results to skip
        
    Returns:
        list: List of website data
    """
    collection = get_collection()
    if collection is None:
        logger.error("Cannot get websites: MongoDB collection not available")
        return []
    
    query = {}
    if user_id:
        logger.info(f"Filtering websites by user_email: {user_id}")
        query['user_email'] = user_id
    
    try:
        # Log the query being executed
        logger.info(f"Executing MongoDB query: {query}")
        
        # First check if any documents match the query
        count = collection.count_documents(query)
        logger.info(f"Found {count} documents matching the query")
        
        if count == 0:
            logger.warning(f"No websites found for user: {user_id}")
            return []
            
        # Execute the query with sorting and pagination
        cursor = collection.find(query).sort('created_at', -1).skip(skip).limit(limit)
        websites = list(cursor)
        
        # Convert ObjectId to string for JSON serialization
        for website in websites:
            if '_id' in website:
                website['_id'] = str(website['_id'])
        
        logger.info(f"Successfully retrieved {len(websites)} websites")
        return websites
    except Exception as e:
        logger.error(f"Error retrieving websites: {e}")
        return []

def delete_website(website_id):
    """
    Delete a website by ID from MongoDB Atlas.
    
    Args:
        website_id (str): Website ID
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    collection = get_collection()
    if collection is None:
        return False
    
    try:
        # Convert string ID to ObjectId
        object_id = ObjectId(website_id)
        result = collection.delete_one({'_id': object_id})
        
        logger.info(f"Website deleted: {website_id}")
        return result.deleted_count > 0
    except Exception as e:
        logger.error(f"Error deleting website: {e}")
        return False

def verify_mongodb_connection():
    """
    Verify MongoDB connection and return diagnostic information.
    
    Returns:
        dict: Diagnostic information about the MongoDB connection
    """
    result = {
        'connected': False,
        'database_name': None,
        'collections': [],
        'connection_string': MONGO_URI[:20] + '...' if MONGO_URI else 'Not configured',
        'error': None,
        'website_count': 0
    }
    
    try:
        # Check if we're connected
        if mongo_db is None:
            result['error'] = "MongoDB client is not initialized"
            return result
            
        # Get database info
        result['connected'] = True
        result['database_name'] = mongo_db.name
        
        # Get collections
        result['collections'] = mongo_db.list_collection_names()
        
        # Count websites
        if COLLECTION_NAME in result['collections']:
            result['website_count'] = mongo_db[COLLECTION_NAME].count_documents({})
            
            # Get a sample website if any exist
            if result['website_count'] > 0:
                sample = mongo_db[COLLECTION_NAME].find_one()
                if sample and '_id' in sample:
                    sample['_id'] = str(sample['_id'])
                result['sample_website'] = sample
                
        return result
    except Exception as e:
        result['error'] = str(e)
        return result
