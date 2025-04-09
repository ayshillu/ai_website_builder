import openai
import os
from pymongo import MongoClient
from django.conf import settings

# MongoDB setup
client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB_NAME]

# Now you can access collections like:
content_collection = db["website_collection"]  


def generate_content(business_type, industry):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    prompt = f"Generate a website for a {business_type} in the {industry} industry. Include hero text, about, and services."

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=300
    )
    return response.choices[0].text.strip()
