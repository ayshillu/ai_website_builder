from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import redirect, render, get_object_or_404
from .models import User, Website
import bcrypt
import jwt
import os
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
import random
import uuid
import json
from datetime import datetime
from django.urls import reverse
import logging
import pymongo

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'index.html')

def details(request):
    if request.method == 'POST':
        business_type = request.POST.get('business_type')
        industry = request.POST.get('industry')
        user_email = request.session.get('user_email', 'guest@example.com')  # Get email from session
        business_name = request.POST.get('business_name')
        location = request.POST.get('location')
        description = request.POST.get('description')

        # Generate content using a direct JSON structure
        try:
            messages.info(request, "🔄 Generating website content... Please wait.")
            
            # Check if API key is available
            api_key = os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                messages.error(request, "⚠️ Google API Key not found. Please check your environment variables.")
                return render(request, 'details.html', {
                    'user_email': user_email,
                    'error': 'API key missing',
                    'form_data': {
                        'business_type': business_type,
                        'industry': industry,
                        'business_name': business_name,
                        'location': location,
                        'description': description
                    }
                })
            
            # Generate content using a direct JSON structure
            content = {
                "name": business_name,
                "theme": {
                    "primary_color": "#6366f1",
                    "secondary_color": "#4f46e5",
                    "text_color": "#333333",
                    "background_color": "#ffffff"
                },
                "pages": [
                    {
                        "name": "Home",
                        "sections": [
                            {
                                "type": "hero",
                                "title": business_name,
                                "subtitle": f"Your premier {business_type.lower()} in {location}",
                                "cta": {
                                    "text": "Contact Us",
                                    "link": "#contact"
                                }
                            },
                            {
                                "type": "about",
                                "id": "about",
                                "title": "About Us",
                                "content": f"{description} We pride ourselves on delivering exceptional service and creating memorable experiences for all our customers. Our commitment to quality and innovation has made us a trusted name in {location}."
                            },
                            {
                                "type": "services",
                                "title": "Our Services",
                                "items": [
                                    {
                                        "title": f"{business_type} Service 1",
                                        "description": "Detailed description of our primary service offering, tailored to meet your specific needs."
                                    },
                                    {
                                        "title": f"{business_type} Service 2",
                                        "description": "Comprehensive explanation of our secondary service, designed to enhance your experience."
                                    },
                                    {
                                        "title": f"{business_type} Service 3",
                                        "description": "Information about our tertiary service offering, providing additional value to our customers."
                                    }
                                ]
                            },
                            {
                                "type": "testimonials",
                                "title": "Testimonials",
                                "items": [
                                    {
                                        "quote": "The service here is simply amazing! The staff are always friendly and helpful. Highly recommend!",
                                        "author": "John D.",
                                        "position": "Customer"
                                    },
                                    {
                                        "quote": f"Best {business_type.lower()} I've experienced in {location}! Will definitely be coming back.",
                                        "author": "Sarah M.",
                                        "position": "Customer"
                                    }
                                ]
                            },
                            {
                                "type": "contact",
                                "title": "Contact Us",
                                "address": f"{business_name}, {location}",
                                "phone": "+1 (555) 123-4567",
                                "email": "contact@example.com"
                            }
                        ]
                    }
                ],
                "footer": {
                    "copyright": f" {datetime.now().year} {business_name}. All rights reserved."
                }
            }
            
            # Prepare website data
            website_data = {
                'user_email': user_email,
                'business_name': business_name,
                'location': location,
                'description': description,
                'business_type': business_type,
                'industry': industry,
                'content': json.dumps(content),
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            # Save to MongoDB
            mongo_id = save_website_data(website_data)
            
            # Also save using Django ORM for backward compatibility
            website = Website.objects.create(
                user_email=user_email,
                business_name=business_name,
                location=location,
                description=description,
                business_type=business_type,
                industry=industry,
                content=json.dumps(content)
            )

            # Add success message
            messages.success(request, "✅ Website generated successfully! Your unique website has been created.")
            
            # Store MongoDB ID in session for reference
            if mongo_id:
                request.session['mongo_website_id'] = mongo_id
                messages.info(request, "📊 Data also stored in MongoDB.")
                # Redirect to view the website using MongoDB ID
                return redirect('view_website', website_id=mongo_id)
            else:
                # Fallback to Django ORM if MongoDB storage failed
                messages.warning(request, "⚠️ MongoDB storage failed. Using Django database instead.")
                # Redirect to view the created website using Django ID
                return redirect('view_website', website_id=website.id)
            
        except Exception as e:
            # More specific error message for Google AI API issues
            error_message = str(e)
            if "API key" in error_message.lower():
                messages.error(request, f"⚠️ Google AI API Key issue: {error_message}. Please check your GOOGLE_API_KEY in .env file.")
            else:
                messages.error(request, f"⚠️ There was an issue with the AI generation: {error_message}")
            
            # Return the form with the entered data so user doesn't lose their input
            return render(request, 'details.html', {
                'user_email': user_email,
                'error': error_message,
                'form_data': {
                    'business_type': business_type,
                    'industry': industry,
                    'business_name': business_name,
                    'location': location,
                    'description': description
                }
            })
        
    return render(request, 'details.html', {'user_email': request.session.get('user_email')})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            if bcrypt.checkpw(password.encode(), user.password.encode()):
                # Create JWT token with a string secret key
                secret_key = os.getenv("SECRET_KEY", "django-insecure-dummy-key-for-development")
                if not isinstance(secret_key, str):
                    secret_key = str(secret_key)
                
                token = jwt.encode({'email': user.email}, secret_key, algorithm='HS256')
                
                # Set token in session or cookie
                request.session['auth_token'] = token
                request.session['user_email'] = user.email
                
                # Redirect to home or dashboard
                return redirect('home')
            else:
                return render(request, 'login.html', {'error': 'Invalid credentials'})
        except User.DoesNotExist:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'login.html')

def signup_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Check if passwords match
        if password != confirm_password:
            return render(request, 'signup.html', {'error': 'Passwords do not match'})
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'error': 'Email already registered'})
        
        # Hash the password
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        
        # Create user
        User.objects.create(email=email, password=hashed.decode())
        
        return render(request, 'signup.html', {'success': 'Account created successfully! You can now log in.'})
    
    return render(request, 'signup.html')

def logout_view(request):
    # Clear session
    if 'auth_token' in request.session:
        del request.session['auth_token']
    if 'user_email' in request.session:
        del request.session['user_email']
    
    return redirect('home')

@api_view(['POST'])
def signup(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    # Hash the password
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    
    # Create user using Django ORM
    User.objects.create(email=email, password=hashed.decode())
    return Response({"msg": "User registered"})

@api_view(['POST'])
def login(request):
    email = request.data['email']
    password = request.data['password']

    try:
        user = User.objects.get(email=email)
        if bcrypt.checkpw(password.encode(), user.password.encode()):
            # Get a valid string secret key
            secret_key = os.getenv("SECRET_KEY", "django-insecure-dummy-key-for-development")
            if not isinstance(secret_key, str):
                secret_key = str(secret_key)
                
            token = jwt.encode({'email': user.email}, secret_key, algorithm='HS256')
            return Response({'token': token})
    except User.DoesNotExist:
        pass
    
    return Response({"msg": "Invalid credentials"}, status=401)

@api_view(['POST'])
def generate_website(request):
    try:
        # Get a valid string secret key
        secret_key = os.getenv("SECRET_KEY", "django-insecure-dummy-key-for-development")
        if not isinstance(secret_key, str):
            secret_key = str(secret_key)
            
        token = request.headers.get('Authorization').split()[1]
        email = jwt.decode(token, secret_key, algorithm='HS256')['email']

        business = request.data['business_type']
        industry = request.data['industry']
        content = {
            "name": request.data.get('business_name', ''),
            "theme": {
                "primary_color": "#6366f1",
                "secondary_color": "#4f46e5",
                "text_color": "#333333",
                "background_color": "#ffffff"
            },
            "pages": [
                {
                    "name": "Home",
                    "sections": [
                        {
                            "type": "hero",
                            "title": request.data.get('business_name', ''),
                            "subtitle": f"Your premier {business.lower()} in {request.data.get('location', '')}",
                            "cta": {
                                "text": "Contact Us",
                                "link": "#contact"
                            }
                        },
                        {
                            "type": "about",
                            "id": "about",
                            "title": "About Us",
                            "content": f"{request.data.get('description', '')} We pride ourselves on delivering exceptional service and creating memorable experiences for all our customers. Our commitment to quality and innovation has made us a trusted name in {request.data.get('location', '')}."
                        },
                        {
                            "type": "services",
                            "title": "Our Services",
                            "items": [
                                {
                                    "title": f"{business} Service 1",
                                    "description": "Detailed description of our primary service offering, tailored to meet your specific needs."
                                },
                                {
                                    "title": f"{business} Service 2",
                                    "description": "Comprehensive explanation of our secondary service, designed to enhance your experience."
                                },
                                {
                                    "title": f"{business} Service 3",
                                    "description": "Information about our tertiary service offering, providing additional value to our customers."
                                }
                            ]
                        },
                        {
                            "type": "testimonials",
                            "title": "Testimonials",
                            "items": [
                                {
                                    "quote": "The service here is simply amazing! The staff are always friendly and helpful. Highly recommend!",
                                    "author": "John D.",
                                    "position": "Customer"
                                },
                                {
                                    "quote": f"Best {business.lower()} I've experienced in {request.data.get('location', '')}! Will definitely be coming back.",
                                    "author": "Sarah M.",
                                    "position": "Customer"
                                }
                            ]
                        },
                        {
                            "type": "contact",
                            "title": "Contact Us",
                            "address": f"{request.data.get('business_name', '')}, {request.data.get('location', '')}",
                            "phone": "+1 (555) 123-4567",
                            "email": "contact@example.com"
                        }
                    ]
                }
            ],
            "footer": {
                "copyright": f" {datetime.now().year} {request.data.get('business_name', '')}. All rights reserved."
            }
        }

        website = Website.objects.create(
            user_email=email,
            business_name=request.data.get('business_name', ''),
            location=request.data.get('location', ''),
            description=request.data.get('description', ''),
            business_type=business,
            industry=industry,
            content=json.dumps(content)
        )

        return Response({
            "id": website.id,
            "content": content,
            "business_type": business,
            "industry": industry
        })   
    
    except Exception as e:
        return Response({"error": str(e)}, status=400)

@api_view(['GET'])
def get_websites(request):
    try:
        # Get a valid string secret key
        secret_key = os.getenv("SECRET_KEY", "django-insecure-dummy-key-for-development")
        if not isinstance(secret_key, str):
            secret_key = str(secret_key)
            
        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header or ' ' not in auth_header:
            return Response({"error": "Invalid Authorization header"}, status=401)
            
        token = auth_header.split()[1]
        
        # Decode JWT token to get user email
        try:
            decoded = jwt.decode(token, secret_key, algorithms=['HS256'])
            email = decoded['email']
        except jwt.PyJWTError as e:
            return Response({"error": f"Invalid token: {str(e)}"}, status=401)
        
        # Get websites from MongoDB
        mongo_websites = get_all_websites(user_id=email)
        
        # If MongoDB returned data, use it
        if mongo_websites:
            print(f"Retrieved {len(mongo_websites)} websites from MongoDB for user {email}")
            return Response(mongo_websites)
        
        # If MongoDB is not available or returned no data, fall back to Django ORM
        print(f"No MongoDB data found for user {email}, falling back to Django ORM")
        websites = Website.objects.filter(user_email=email)
        
        if not websites.exists():
            print(f"No websites found in Django ORM for user {email}")
            return Response([])
            
        websites_data = [{
            'id': website.id,
            'business_name': website.business_name,
            'location': website.location,
            'description': website.description,
            'business_type': website.business_type,
            'industry': website.industry,
            'content': json.loads(website.content)
        } for website in websites]
        
        print(f"Retrieved {len(websites_data)} websites from Django ORM for user {email}")
        return Response(websites_data)
    except Exception as e:
        print(f"Error in get_websites: {str(e)}")
        return Response({"error": str(e)}, status=401)

@api_view(['PUT'])
def update_website(request, website_id):
    try:
        # Update in Django ORM
        website = get_object_or_404(Website, id=website_id)
        website.content = json.dumps(request.data.get('content', json.loads(website.content)))
        website.save()
        
        # Also update in MongoDB if we have the ID
        mongo_id = request.session.get('mongo_website_id')
        if mongo_id:
            update_mongo_website(mongo_id, {'content': request.data.get('content')})
            
        return Response({"msg": "Website updated"})
    except Exception as e:
        return Response({"error": str(e)}, status=400)

@api_view(['DELETE'])
def delete_website(request, website_id):
    try:
        # Delete from Django ORM
        website = get_object_or_404(Website, id=website_id)
        website.delete()
        
        # Also delete from MongoDB if we have the ID
        mongo_id = request.session.get('mongo_website_id')
        if mongo_id:
            delete_mongo_website(mongo_id)
            if 'mongo_website_id' in request.session:
                del request.session['mongo_website_id']
                
        return Response({"msg": "Website deleted"})
    except Exception as e:
        return Response({"error": str(e)}, status=400)

def view_website(request, website_id):
    # Add debug logging
    logger.info(f"Viewing website with ID: {website_id}")
    
    if not website_id:
        logger.error("No website_id provided")
        messages.error(request, "No website ID provided")
        return redirect('home')
    
    # First try to get from MongoDB using the website_id
    try:
        mongo_website = get_website_by_id(website_id)
        logger.info(f"MongoDB lookup result: {'Found' if mongo_website else 'Not found'}")
        
        if mongo_website:
            # If found in MongoDB, use that data
            logger.info(f"Using MongoDB data for website: {website_id}")
            website_content = mongo_website.get('content', {})
            
            # Print the content type for debugging
            content_type = type(website_content).__name__
            logger.info(f"Content type: {content_type}")
            
            # Create a Django model instance for template rendering
            website = Website(
                id=website_id,
                user_email=mongo_website.get('user_email', ''),
                business_name=mongo_website.get('business_name', ''),
                location=mongo_website.get('location', ''),
                description=mongo_website.get('description', ''),
                business_type=mongo_website.get('business_type', ''),
                industry=mongo_website.get('industry', ''),
                content=json.dumps(website_content) if isinstance(website_content, dict) else website_content
            )
            messages.info(request, "📊 Website data retrieved from MongoDB.")
            
            # Store the MongoDB ID in session for future use
            request.session['mongo_website_id'] = website_id
            
            # Log the template context for debugging
            logger.info(f"Rendering template with MongoDB data: business_name={website.business_name}")
            
            return render(request, 'view_website.html', {
                'website': website,
                'mongo_data': mongo_website,
                'is_mongo': True
            })
    except Exception as e:
        logger.error(f"Error retrieving website from MongoDB: {str(e)}")
        messages.warning(request, f"⚠️ Error retrieving from MongoDB: {str(e)}")
    
    # If not found in MongoDB or error occurred, try Django ORM
    try:
        logger.info(f"Falling back to Django ORM for website: {website_id}")
        website = get_object_or_404(Website, id=website_id)
        logger.info(f"Found website in Django ORM: {website.business_name}")
        return render(request, 'view_website.html', {'website': website})
    except Exception as e:
        logger.error(f"Error retrieving website from Django ORM: {str(e)}")
        messages.error(request, f"❌ Website not found: {str(e)}")
        return redirect('home')

def view_generated_website(request, website_id=None):
    """
    View the AI-generated website layout.
    If website_id is provided, show that specific website.
    Otherwise, show the most recent website.
    """
    # Check if user is logged in
    user_email = request.session.get('user_email', None)
    
    # Connect to MongoDB
    MONGO_URI = os.getenv('MONGO_URI')
    if not MONGO_URI:
        messages.error(request, "MongoDB connection string not found")
        return redirect('details')
    
    try:
        # Connect to MongoDB
        mongo_client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        mongo_db = mongo_client["ai_builder_db"]
        collection = mongo_db["websites_collection"]
        
        # Add debug logging
        print(f"MongoDB connection successful. Looking for website_id: {website_id}")
        
        if website_id:
            # Get specific website from MongoDB
            from bson.objectid import ObjectId
            try:
                # Try to convert to ObjectId if it's a valid MongoDB ID
                object_id = ObjectId(website_id)
                website_data = collection.find_one({"_id": object_id})
                print(f"Searched for ObjectId: {object_id}, Found: {bool(website_data)}")
            except Exception as e:
                print(f"Error converting to ObjectId: {str(e)}")
                # If not a valid ObjectId, try as a string ID
                website_data = collection.find_one({"_id": website_id})
                print(f"Searched for string ID: {website_id}, Found: {bool(website_data)}")
                
            if not website_data:
                # If still not found, try to list recent documents to see what's available
                print("Website not found. Listing recent documents:")
                recent_docs = list(collection.find().sort("created_at", -1).limit(3))
                for doc in recent_docs:
                    print(f"  - ID: {doc['_id']}, Name: {doc.get('business_name', 'N/A')}")
                
                messages.error(request, "Website not found.")
                return redirect('home')
        else:
            # Get the most recent website from MongoDB
            if user_email:
                cursor = collection.find({"user_email": user_email}).sort("created_at", -1).limit(1)
                print(f"Searching for most recent website by user: {user_email}")
            else:
                cursor = collection.find().sort("created_at", -1).limit(1)
                print("Searching for most recent website (any user)")
                
            websites = list(cursor)
            
            if not websites:
                print("No websites found in the collection")
                messages.error(request, "No websites found. Please generate a website first.")
                return redirect('home')
            
            website_data = websites[0]
            print(f"Found most recent website with ID: {website_data['_id']}")
        
        # Convert MongoDB ObjectId to string for JSON serialization
        if '_id' in website_data and isinstance(website_data['_id'], ObjectId):
            website_data['_id'] = str(website_data['_id'])
        
        # Extract the content (website layout)
        website_layout = website_data.get('content', {})
        
        # Debug the content structure
        print(f"Content type: {type(website_layout).__name__}")
        if isinstance(website_layout, dict):
            print(f"Content keys: {list(website_layout.keys())}")
            
        # Add more detailed debugging
        print(f"All website_data keys: {list(website_data.keys())}")
        print(f"Business name: {website_data.get('business_name')}")
        print(f"Created at: {website_data.get('created_at')}")
        
        context = {
            'website': website_data,  # Include the full website data
            'mongo_data': website_data,
            'website_layout': website_layout,  # Add the layout directly to context
            'is_mongo': True,
            'user_email': user_email,
        }
        
        return render(request, 'view_website.html', context)
    
    except Exception as e:
        print(f"Error in view_generated_website: {str(e)}")
        messages.error(request, f"Error connecting to MongoDB: {str(e)}")
        return redirect('home')

def mongodb_diagnostic(request):
    """
    View to diagnose MongoDB connection and data storage.
    """
    # Get MongoDB diagnostic information
    mongo_info = verify_mongodb_connection()
    
    # Get Django ORM website count for comparison
    django_website_count = Website.objects.count()
    
    # Prepare context
    context = {
        'mongo_info': mongo_info,
        'django_website_count': django_website_count,
        'user_email': request.session.get('user_email', None)
    }
    
    # If user is logged in, get their websites from both sources
    if context['user_email']:
        # Get MongoDB websites
        mongo_websites = get_all_websites(user_id=context['user_email'])
        context['mongo_user_websites'] = mongo_websites
        context['mongo_user_website_count'] = len(mongo_websites)
        
        # Get Django ORM websites
        django_websites = Website.objects.filter(user_email=context['user_email'])
        context['django_user_website_count'] = django_websites.count()
    
    return render(request, 'mongodb_diagnostic.html', context)

def generate_website_layout(request):
    """
    Generate a complete HTML website based on user inputs and store it in MongoDB.
    """
    if request.method == 'POST':
        if request.headers.get('Content-Type') == 'application/json':
            data = json.loads(request.body)
            business_name = data.get('business_name', '')
            business_type = data.get('business_type', '')
            industry = data.get('industry', '')
            location = data.get('location', '')
            description = data.get('description', '')
        else:
            business_name = request.POST.get('business_name', '')
            business_type = request.POST.get('business_type', '')
            industry = request.POST.get('industry', '')
            location = request.POST.get('location', '')
            description = request.POST.get('description', '')
        
        # Check for required fields
        if not all([business_name, business_type, industry, location, description]):
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({
                    "success": False,
                    "message": "All fields are required."
                }, status=400)
            else:
                messages.error(request, "All fields are required.")
                return redirect('details')
        
        # Get user email from session if available, otherwise use guest
        user_email = request.session.get('user_email', 'guest@example.com')
        
        # Create a basic JSON structure for the website content
        content = {
            "name": business_name,
            "theme": {
                "primary_color": "#6366f1",
                "secondary_color": "#4f46e5",
                "text_color": "#333333",
                "background_color": "#ffffff"
            },
            "pages": [
                {
                    "name": "Home",
                    "sections": [
                        {
                            "type": "hero",
                            "title": business_name,
                            "subtitle": f"Your premier {business_type.lower()} in {location}",
                            "cta": {
                                "text": "Contact Us",
                                "link": "#contact"
                            }
                        },
                        {
                            "type": "about",
                            "id": "about",
                            "title": "About Us",
                            "content": f"{description} We pride ourselves on delivering exceptional service and creating memorable experiences for all our customers. Our commitment to quality and innovation has made us a trusted name in {location}."
                        },
                        {
                            "type": "services",
                            "title": "Our Services",
                            "items": [
                                {
                                    "title": f"{business_type} Service 1",
                                    "description": "Detailed description of our primary service offering, tailored to meet your specific needs."
                                },
                                {
                                    "title": f"{business_type} Service 2",
                                    "description": "Comprehensive explanation of our secondary service, designed to enhance your experience."
                                },
                                {
                                    "title": f"{business_type} Service 3",
                                    "description": "Information about our tertiary service offering, providing additional value to our customers."
                                }
                            ]
                        },
                        {
                            "type": "testimonials",
                            "title": "Testimonials",
                            "items": [
                                {
                                    "quote": "The service here is simply amazing! The staff are always friendly and helpful. Highly recommend!",
                                    "author": "John D.",
                                    "position": "Customer"
                                },
                                {
                                    "quote": f"Best {business_type.lower()} I've experienced in {location}! Will definitely be coming back.",
                                    "author": "Sarah M.",
                                    "position": "Customer"
                                }
                            ]
                        },
                        {
                            "type": "contact",
                            "title": "Contact Us",
                            "address": f"{business_name}, {location}",
                            "phone": "+1 (555) 123-4567",
                            "email": "contact@example.com"
                        }
                    ]
                }
            ],
            "footer": {
                "copyright": f" {datetime.now().year} {business_name}. All rights reserved."
            }
        }
        
        # Prepare website data for MongoDB
        website_data = {
            'user_email': user_email,
            'business_name': business_name,
            'location': location,
            'description': description,
            'business_type': business_type,
            'industry': industry,
            'content': content,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        # Save to MongoDB
        MONGO_URI = os.getenv('MONGO_URI')
        if not MONGO_URI:
            print("Error: MONGO_URI environment variable not set")
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({"success": False, "message": "MongoDB connection string not found"}, status=500)
            else:
                messages.error(request, "MongoDB connection string not found")
                return redirect('details')
        
        mongo_client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        mongo_db = mongo_client["ai_builder_db"]
        collection = mongo_db["websites_collection"]
        
        result = collection.insert_one(website_data)
        mongo_id = str(result.inserted_id)
        print(f"Website data inserted with ID: {mongo_id}")
        
        # Also save in Django ORM for backward compatibility
        try:
            website = Website.objects.create(
                user_email=user_email,
                business_name=business_name,
                location=location,
                description=description,
                business_type=business_type,
                industry=industry,
                content=json.dumps(content)  # Convert content to string for Django ORM
            )
            django_id = website.id
        except Exception as e:
            django_id = None
            logger.error(f"Error saving to Django ORM: {str(e)}")
        
        # Return success response
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({
                "success": True,
                "message": "Website data saved successfully.",
                "mongo_id": str(mongo_id),
                "django_id": django_id
            })
        else:
            messages.success(request, "Website generated successfully!")
            return redirect('view_generated_website_by_id', website_id=mongo_id)
    else:
        return render(request, 'details.html')
