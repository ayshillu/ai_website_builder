from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import redirect, render
from .models import User,Website
from .serializers import UserSerializer
import bcrypt
import jwt
import os
from .utils import generate_content  # Import your OpenAI logic from utils.py
from .models import Website
from bson import ObjectId

from django.http import JsonResponse, HttpResponse
from pymongo import MongoClient



# MongoDB connection setup
client = MongoClient('mongodb+srv://ayshaabdulfaizal:mydatabase@ai-builder.fqbgu3d.mongodb.net/?retryWrites=true&w=majority&appName=ai-builder')  # Replace with your MongoDB URI
db = client['ai_builder_db']  # Replace with your database name
collection = db['website_collection']  # Replace with your collection name

def index(request):
    return render(request, 'index.html')

def details(request):
    if request.method == 'POST':
        # Extract form data from HTML form submission
        business_name = request.POST.get('business_type')
        location = request.POST.get('industry')
        description = request.POST.get('description')
        business_type = request.POST.get('business_category')
        user_email = request.POST.get('user_email')

        # Optionally generate some dummy or static content for now
        from .utils import generate_content
        content = generate_content(business_name, location)

        # Insert into MongoDB
        collection.insert_one({
            'user_email': user_email,
            'business_name': business_name,
            'location': location,
            'description': description,
            'business_type': business_type,
            'content': content
        })

        # Also save in Django DB if required
        Website.objects.create(
            user_email=user_email,
            business_name=business_name,
            location=location,
            description=description,
            business_type=business_type,
            content=content
        )

        return HttpResponse("✅ Website data saved successfully!")

    return render(request, 'details.html')




def create(request):
    return render(request, 'create_website.html')

@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"msg": "User registered"})
    return Response(serializer.errors, status=400)

@api_view(['POST'])
def login(request):
    email = request.data['email']
    password = request.data['password']

    try:
        user = User.objects.get(email=email)
        if bcrypt.checkpw(password.encode(), user.password.encode()):
            token = jwt.encode({'email': user.email}, os.getenv("SECRET_KEY"), algorithm='HS256')
            return Response({'token': token})
    except:
        pass
    return Response({"msg": "Invalid credentials"}, status=401)


@api_view(['POST'])
def generate_website(request):
    try:
        token = request.headers.get('Authorization').split()[1]
        email = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=['HS256'])['email']

        business_name = request.data['business_type']  # "Name of your Business"
        location = request.data['industry']            # "Business Location"
        description = request.data['description']      # Description
        business_type = request.data['business_category']  # "Type of Business"

        if not all([business_name, location, description, business_type, email]):
            return Response({"error": "All fields are required."}, status=400)

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
        collection.insert_one({
            'user_email': email,
            'business_name': business_name,
            'location': location,
            'description': description,
            'business_type': business_type,
            'content': content
        })

        return Response({
            "id": str(website.id),
            "content": content,
            "business_name": business_name,
            "location": location,
            "description": description,
            "business_type": business_type
        })

    except Exception as e:
        return Response({"error": str(e)}, status=400)
    
    

@api_view(['GET'])
def get_websites(request):
    token = request.headers.get('Authorization').split()[1]
    email = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=['HS256'])['email']
    websites = Website.objects.filter(user_email=email)
    return Response([{"id": w.id, "content": w.content} for w in websites])

@api_view(['PUT'])
def update_website(request, website_id):
    content = request.data['content']
    Website.objects.filter(id=website_id).update(content=content)
    return Response({"msg": "Website updated"})

@api_view(['DELETE'])
def delete_website(request, website_id):
    Website.objects.filter(id=website_id).delete()
    return Response({"msg": "Website deleted"})
