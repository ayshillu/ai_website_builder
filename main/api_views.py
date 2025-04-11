from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Website
import jwt
import os
from datetime import datetime
from pymongo import MongoClient
import pymongo

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client["ai_builder_db"]

class WebsiteCreateAPIView(APIView):
    def post(self, request):
        try:
            # Get token from header
            token = request.headers.get('Authorization').split()[1]
            decoded_token = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=['HS256'])
            email = decoded_token['email']
            
            # Get data from request
            business_name = request.data.get('business_name', '')
            business_type = request.data.get('business_type', '')
            industry = request.data.get('industry', '')
            location = request.data.get('location', '')
            description = request.data.get('description', '')
            
            # Check for required fields
            if not all([business_name, location, description, business_type, email]):
                return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

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
                                "content": description
                            },
                            {
                                "type": "services",
                                "title": "Our Services",
                                "items": [
                                    {
                                        "title": f"{business_type} Service 1",
                                        "description": "Our primary service offering"
                                    },
                                    {
                                        "title": f"{business_type} Service 2",
                                        "description": "Our secondary service offering"
                                    },
                                    {
                                        "title": f"{business_type} Service 3",
                                        "description": "Our tertiary service offering"
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
                'user_email': email,
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
            mongo_id = db.websites_collection.insert_one(website_data).inserted_id
            
            if not mongo_id:
                return Response({"error": "Failed to save website data to MongoDB."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Also save in Django ORM
            try:
                website = Website.objects.create(
                    user_email=email,
                    business_name=business_name,
                    location=location,
                    description=description,
                    business_type=business_type,
                    industry=industry,
                    content=str(content)  # Convert content to string for Django ORM
                )
                django_id = website.id
            except Exception as e:
                django_id = None
            
            # Return success response with IDs
            return Response({
                "success": True,
                "message": "Website data saved successfully.",
                "mongo_id": str(mongo_id),
                "django_id": django_id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

class WebsiteListAPIView(APIView):
    def get(self, request):
        try:
            token = request.headers.get('Authorization').split()[1]
            decoded_token = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=['HS256'])
            email = decoded_token['email']
            
            # Get websites from MongoDB
            websites = list(db.websites_collection.find({"user_email": email}))
            
            # Convert ObjectId to string
            for website in websites:
                website['_id'] = str(website['_id'])
            
            return Response(websites)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class WebsiteFormAPIView(APIView):
    def post(self, request):
        try:
            # Get data from request
            business_name = request.data.get('business_name', '')
            business_type = request.data.get('business_type', '')
            industry = request.data.get('industry', '')
            location = request.data.get('location', '')
            description = request.data.get('description', '')
            
            # Print debug information
            print(f"Received form data: business_name={business_name}, business_type={business_type}, industry={industry}")
            print(f"Request data type: {type(request.data)}")
            print(f"Request data: {request.data}")
            
            # Check for required fields
            if not all([business_name, location, description, business_type]):
                print(f"Missing required fields: business_name={bool(business_name)}, location={bool(location)}, description={bool(description)}, business_type={bool(business_type)}")
                return Response({
                    "success": False,
                    "message": "All fields are required."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get user email from session if available, otherwise use guest
            user_email = request.session.get('user_email', 'guest@example.com')
            
            # Generate a color theme based on business type/industry
            primary_color, secondary_color = self.get_theme_colors(business_type, industry)
            
            # Create a basic JSON structure for the website content
            content = {
                "name": business_name,
                "theme": {
                    "primary_color": primary_color,
                    "secondary_color": secondary_color,
                    "text_color": "#f8fafc",
                    "background_color": "#0f172a",
                    "accent_color": "#a5b4fc"
                },
                "header": {
                    "logo_text": business_name,
                    "navigation": [
                        {"text": "Home", "link": "#"},
                        {"text": "About", "link": "#about"},
                        {"text": "Services", "link": "#services"},
                        {"text": "Testimonials", "link": "#testimonials"},
                        {"text": "Contact", "link": "#contact"}
                    ]
                },
                "pages": [
                    {
                        "name": "Home",
                        "sections": [
                            {
                                "type": "hero",
                                "id": "home",
                                "title": business_name,
                                "subtitle": f"Your premier {business_type.lower()} in {location}",
                                "background_image": self.get_background_image(business_type, industry),
                                "cta": {
                                    "text": "Get Started",
                                    "link": "#contact"
                                }
                            },
                            {
                                "type": "about",
                                "id": "about",
                                "title": "About Us",
                                "content": description,
                                "image": self.get_about_image(business_type, industry)
                            },
                            {
                                "type": "services",
                                "id": "services",
                                "title": "Our Services",
                                "items": self.generate_services(business_type, industry)
                            },
                            {
                                "type": "testimonials",
                                "id": "testimonials",
                                "title": "What Our Clients Say",
                                "items": self.generate_testimonials(business_type, location)
                            },
                            {
                                "type": "contact",
                                "id": "contact",
                                "title": "Contact Us",
                                "address": f"{business_name}, {location}",
                                "email": "contact@example.com",
                                "phone": "+1 (555) 123-4567",
                                "map_embed": f"https://maps.google.com/maps?q={location.replace(' ', '+')}&output=embed"
                            }
                        ]
                    }
                ],
                "footer": {
                    "copyright": f" {datetime.now().year} {business_name}. All rights reserved.",
                    "social_links": [
                        {"platform": "Facebook", "icon": "fab fa-facebook", "link": "#"},
                        {"platform": "Twitter", "icon": "fab fa-twitter", "link": "#"},
                        {"platform": "Instagram", "icon": "fab fa-instagram", "link": "#"},
                        {"platform": "LinkedIn", "icon": "fab fa-linkedin", "link": "#"}
                    ],
                    "columns": [
                        {
                            "title": "Quick Links",
                            "links": [
                                {"text": "Home", "link": "#"},
                                {"text": "About", "link": "#about"},
                                {"text": "Services", "link": "#services"},
                                {"text": "Contact", "link": "#contact"}
                            ]
                        },
                        {
                            "title": "Services",
                            "links": self.generate_service_links(business_type, industry)
                        },
                        {
                            "title": "Contact Info",
                            "content": f"<p>{business_name}</p><p>{location}</p><p>Phone: +1 (555) 123-4567</p><p>Email: contact@example.com</p>"
                        }
                    ]
                }
            }
            
            # Create the website data dictionary
            website_data = {
                "business_name": business_name,
                "business_type": business_type,
                "industry": industry,
                "location": location,
                "description": description,
                "user_email": user_email,
                "content": content,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # Print debug information before saving to MongoDB
            print(f"Attempting to save to MongoDB: {website_data.keys()}")
            
            # Connect to MongoDB
            MONGO_URI = os.getenv('MONGO_URI')
            if not MONGO_URI:
                print("MongoDB URI not found in environment variables")
                return Response({
                    "success": False,
                    "message": "Database configuration error."
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            try:
                # Connect to MongoDB with a timeout
                mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
                # Test the connection
                mongo_client.server_info()
                db = mongo_client["ai_builder_db"]
                print(f"MongoDB connection successful, inserting into websites_collection")
                
                # Insert the data into MongoDB
                mongo_result = db.websites_collection.insert_one(website_data)
                mongo_id = str(mongo_result.inserted_id)
                
                print(f"Data saved to MongoDB with ID: {mongo_id}")
                
                # Verify the data was saved
                saved_data = db.websites_collection.find_one({"_id": mongo_result.inserted_id})
                if saved_data:
                    print(f"Verified data saved with keys: {list(saved_data.keys())}")
                else:
                    print("Warning: Could not verify saved data")
                
                # Return success response with the MongoDB ID
                return Response({
                    "success": True,
                    "message": "Website generated successfully!",
                    "website_id": mongo_id,
                    "mongo_id": mongo_id  # Add this for backward compatibility
                }, status=status.HTTP_201_CREATED)
                
            except pymongo.errors.ConnectionFailure as e:
                print(f"MongoDB connection failure: {str(e)}")
                return Response({
                    "success": False,
                    "message": f"Database connection error: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                print(f"MongoDB error: {str(e)}")
                return Response({
                    "success": False,
                    "message": f"Database error: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            print(f"Error in WebsiteFormAPIView.post: {str(e)}")
            return Response({
                "success": False,
                "message": f"An error occurred: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_theme_colors(self, business_type, industry):
        """Generate a color theme based on business type and industry"""
        # Default colors
        primary = "#6366f1"
        secondary = "#4f46e5"
        
        # Map business types to color schemes
        business_colors = {
            "Restaurant": ("#e11d48", "#be123c"),  # Red
            "Cafe": ("#d97706", "#b45309"),  # Amber
            "Bakery": ("#f59e0b", "#d97706"),  # Amber
            "Technology": ("#3b82f6", "#2563eb"),  # Blue
            "Healthcare": ("#06b6d4", "#0891b2"),  # Cyan
            "Education": ("#8b5cf6", "#7c3aed"),  # Violet
            "Fitness": ("#10b981", "#059669"),  # Emerald
            "Legal": ("#1e40af", "#1e3a8a"),  # Dark Blue
            "Real Estate": ("#0f766e", "#115e59"),  # Teal
            "Construction": ("#f97316", "#ea580c"),  # Orange
            "Retail": ("#ec4899", "#db2777"),  # Pink
            "Consulting": ("#6366f1", "#4f46e5"),  # Indigo
            "Marketing": ("#84cc16", "#65a30d"),  # Lime
            "Financial": ("#064e3b", "#065f46"),  # Green
            "Automotive": ("#dc2626", "#b91c1c"),  # Red
            "Salon": ("#d946ef", "#c026d3"),  # Fuchsia
            "Spa": ("#8b5cf6", "#7c3aed"),  # Violet
            "Travel": ("#0ea5e9", "#0284c7"),  # Sky
        }
        
        # Check if business type has a predefined color scheme
        for key in business_colors:
            if key.lower() in business_type.lower() or key.lower() in industry.lower():
                return business_colors[key]
        
        # If no match, return default colors
        return primary, secondary
    
    def get_background_image(self, business_type, industry):
        """Get a relevant background image based on business type"""
        # Default image
        default_image = "https://images.unsplash.com/photo-1497366754035-f200968a6e72?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
        
        # Map business types to background images
        image_map = {
            "Restaurant": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
            "Cafe": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
            "Bakery": "https://images.unsplash.com/photo-1517433670267-08bbd4be890f?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
            "Technology": "https://images.unsplash.com/photo-1518770660439-4636190af475?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
            "Healthcare": "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
            "Education": "https://images.unsplash.com/photo-1523050854058-8e7e53415bb0?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
            "Fitness": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
            "Legal": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
            "Real Estate": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
            "Construction": "https://images.unsplash.com/photo-1503387762-592deb58ef4e?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
            "Retail": "https://images.unsplash.com/photo-1567401893414-76b7b1e5a7a5?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
            "Consulting": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
            "Marketing": "https://images.unsplash.com/photo-1552664730-d307ca884978?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
            "Financial": "https://images.unsplash.com/photo-1460925895917-d51941baf7fb?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
            "Automotive": "https://images.unsplash.com/photo-1492144534655-d51941baf7fb?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
            "Salon": "https://images.unsplash.com/photo-1560066984-138dadb4c035?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
            "Spa": "https://images.unsplash.com/photo-1540555700478-4be289fbecef?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
            "Travel": "https://images.unsplash.com/photo-1503220317375-aaad61436b1b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
        }
        
        # Check if business type has a predefined image
        for key in image_map:
            if key.lower() in business_type.lower() or key.lower() in industry.lower():
                return image_map[key]
        
        # If no match, return default image
        return default_image
    
    def get_about_image(self, business_type, industry):
        """Get a relevant about section image based on business type"""
        # Default image
        default_image = "https://images.unsplash.com/photo-1600880292203-757bb62b4baf?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
        
        # Map business types to about images
        image_map = {
            "Restaurant": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
            "Cafe": "https://images.unsplash.com/photo-1445116572660-236099ec97a0?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
            "Bakery": "https://images.unsplash.com/photo-1591688515527-f7b20bd05902?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
            "Technology": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
            "Healthcare": "https://images.unsplash.com/photo-1579684385127-1ef15d508118?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
            "Education": "https://images.unsplash.com/photo-1427504494785-3a9ca7044f45?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
            "Fitness": "https://images.unsplash.com/photo-1571902943202-507ec2618e8f?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
            "Legal": "https://images.unsplash.com/photo-1589391886645-d51941baf7fb?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
            "Real Estate": "https://images.unsplash.com/photo-1592595896616-c37162298647?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
            "Construction": "https://images.unsplash.com/photo-1504307651254-35680f356dfd?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
            "Retail": "https://images.unsplash.com/photo-1573855619003-97b4799dcd8b?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
            "Consulting": "https://images.unsplash.com/photo-1542744173-8e7e53415bb0?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
            "Marketing": "https://images.unsplash.com/photo-1533750349088-cd871a92f312?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
            "Financial": "https://images.unsplash.com/photo-1563986768494-d10d557cf95f?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
            "Automotive": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
            "Salon": "https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
            "Spa": "https://images.unsplash.com/photo-1544161515-4ab6ce6db874?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
            "Travel": "https://images.unsplash.com/photo-1526772662000-3f88f10405ff?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        }
        
        # Check if business type has a predefined image
        for key in image_map:
            if key.lower() in business_type.lower() or key.lower() in industry.lower():
                return image_map[key]
        
        # If no match, return default image
        return default_image
    
    def generate_services(self, business_type, industry):
        """Generate relevant services based on business type and industry"""
        # Default services
        default_services = [
            {
                "title": "Service 1",
                "description": "Our primary service offering tailored to your needs."
            },
            {
                "title": "Service 2",
                "description": "Our secondary service offering with premium features."
            },
            {
                "title": "Service 3",
                "description": "Our tertiary service offering for specialized needs."
            }
        ]
        
        # Map business types to specific services
        service_map = {
            "Restaurant": [
                {"title": "Fine Dining", "description": "Experience our exquisite menu in an elegant atmosphere."},
                {"title": "Catering", "description": "Let us bring our culinary expertise to your special events."},
                {"title": "Private Events", "description": "Host your celebrations in our dedicated private dining spaces."}
            ],
            "Cafe": [
                {"title": "Specialty Coffee", "description": "Enjoy our selection of premium, locally-roasted coffee beans."},
                {"title": "Breakfast & Brunch", "description": "Start your day with our fresh, homemade breakfast options."},
                {"title": "Pastries & Desserts", "description": "Indulge in our freshly baked goods made daily."}
            ],
            "Technology": [
                {"title": "Software Development", "description": "Custom software solutions tailored to your business needs."},
                {"title": "IT Consulting", "description": "Expert advice on optimizing your technology infrastructure."},
                {"title": "Cloud Services", "description": "Secure, scalable cloud solutions for your business."}
            ],
            "Healthcare": [
                {"title": "Primary Care", "description": "Comprehensive healthcare services for patients of all ages."},
                {"title": "Specialized Treatment", "description": "Expert care for specific health conditions and needs."},
                {"title": "Preventive Medicine", "description": "Proactive healthcare to maintain your wellbeing."}
            ],
            "Fitness": [
                {"title": "Personal Training", "description": "One-on-one sessions tailored to your fitness goals."},
                {"title": "Group Classes", "description": "Energetic, motivating classes for all fitness levels."},
                {"title": "Nutrition Coaching", "description": "Expert guidance on nutrition to complement your fitness journey."}
            ]
        }
        
        # Check if business type has predefined services
        for key in service_map:
            if key.lower() in business_type.lower() or key.lower() in industry.lower():
                return service_map[key]
        
        # If no match, generate generic services based on business type
        if business_type:
            return [
                {"title": f"Premium {business_type} Service", "description": f"Our flagship {business_type.lower()} service designed to exceed expectations."},
                {"title": "Consultation", "description": f"Expert {business_type.lower()} consultation tailored to your specific needs."},
                {"title": "Ongoing Support", "description": f"Continuous assistance and support for all your {business_type.lower()} requirements."}
            ]
        
        # If all else fails, return default services
        return default_services
    
    def generate_testimonials(self, business_type, location):
        """Generate relevant testimonials based on business type and location"""
        return [
            {
                "quote": f"The best {business_type.lower()} service I've experienced in {location}. Highly recommended!",
                "author": "John Smith",
                "position": "Satisfied Customer"
            },
            {
                "quote": f"Exceptional quality and service. Their {business_type.lower()} expertise is unmatched.",
                "author": "Jane Doe",
                "position": "Loyal Client"
            },
            {
                "quote": "Professional, reliable, and truly outstanding results every time.",
                "author": "Robert Johnson",
                "position": "Business Owner"
            }
        ]
    
    def generate_service_links(self, business_type, industry):
        """Generate service links for the footer based on business type"""
        # Default service links
        default_links = [
            {"text": "Service 1", "link": "#services"},
            {"text": "Service 2", "link": "#services"},
            {"text": "Service 3", "link": "#services"}
        ]
        
        # Map business types to specific service links
        service_links_map = {
            "Restaurant": [
                {"text": "Fine Dining", "link": "#services"},
                {"text": "Catering", "link": "#services"},
                {"text": "Private Events", "link": "#services"}
            ],
            "Cafe": [
                {"text": "Specialty Coffee", "link": "#services"},
                {"text": "Breakfast & Brunch", "link": "#services"},
                {"text": "Pastries & Desserts", "link": "#services"}
            ],
            "Technology": [
                {"text": "Software Development", "link": "#services"},
                {"text": "IT Consulting", "link": "#services"},
                {"text": "Cloud Services", "link": "#services"}
            ],
            "Healthcare": [
                {"text": "Primary Care", "link": "#services"},
                {"text": "Specialized Treatment", "link": "#services"},
                {"text": "Preventive Medicine", "link": "#services"}
            ],
            "Fitness": [
                {"text": "Personal Training", "link": "#services"},
                {"text": "Group Classes", "link": "#services"},
                {"text": "Nutrition Coaching", "link": "#services"}
            ]
        }
        
        # Check if business type has predefined service links
        for key in service_links_map:
            if key.lower() in business_type.lower() or key.lower() in industry.lower():
                return service_links_map[key]
        
        # If no match, generate generic service links based on business type
        if business_type:
            return [
                {"text": f"{business_type} Service", "link": "#services"},
                {"text": "Consultation", "link": "#services"},
                {"text": "Support", "link": "#services"}
            ]
        
        # If all else fails, return default links
        return default_links
