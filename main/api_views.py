from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Website
from .utils import generate_content
import jwt
import os
from pymongo import MongoClient

class WebsiteCreateAPIView(APIView):
    def post(self, request):
        try:
            token = request.headers.get('Authorization').split()[1]
            decoded_token = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=['HS256'])
            email = decoded_token['email']

            business_name = request.data.get('business_type')  # name of business
            location = request.data.get('industry')  # business location
            description = request.data.get('description')
            business_type = request.data.get('business_category')

            # Check for required fields
            if not all([business_name, location, description, business_type, email]):
                return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

            content = generate_content(business_name, location)

            # Save in Django DB
            website = Website.objects.create(
                user_email=email,
                business_name=business_name,
                location=location,
                description=description,
                business_type=business_type,
                content=content
            )

            # Save in MongoDB
            client = MongoClient('mongodb+srv://ayshaabdulfaizal:mydatabase@ai-builder.fqbgu3d.mongodb.net/?retryWrites=true&w=majority&appName=ai-builder')
            db = client['ai_builder']
            collection = db['business_details']

            collection.insert_one({
                'user_email': email,
                'business_name': business_name,
                'location': location,
                'description': description,
                'business_type': business_type,
                'content': content,
            })

            return Response({
                "id": str(website.id),
                "business_name": business_name,
                "location": location,
                "description": description,
                "business_type": business_type,
                "content": content
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
