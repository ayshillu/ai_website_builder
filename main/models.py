from django.db import models
from datetime import datetime

# MongoDB connection is disabled
# Instead, we'll use Django's ORM

class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # In production, use django.contrib.auth.models.User
    created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.email

class Website(models.Model):
    user_email = models.CharField(max_length=255, default='user@example.com')  # In a real app, use ForeignKey to User
    business_name = models.CharField(max_length=255, default='New Business')
    location = models.CharField(max_length=255, default='Location')
    description = models.TextField(default='Description')
    business_type = models.CharField(max_length=100, default='Business')
    industry = models.CharField(max_length=100, default='Industry')
    content = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=datetime.now)
    
    # New fields for better customization
    color_scheme = models.CharField(max_length=100, default='modern')  # e.g., modern, classic, vibrant
    layout_style = models.CharField(max_length=100, default='responsive')  # e.g., responsive, single-page, multi-page
    font_style = models.CharField(max_length=100, default='sans-serif')  # e.g., sans-serif, serif, modern
    logo_url = models.URLField(null=True, blank=True)
    last_edited = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    theme_version = models.IntegerField(default=1)

    def __str__(self):
        return self.business_name
