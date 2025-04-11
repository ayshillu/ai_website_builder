import jwt
import os
from django.shortcuts import redirect
from django.urls import reverse

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # URLs that don't require authentication
        public_urls = [
            reverse('home'),
            reverse('login'),
            reverse('signup'),
            reverse('details'),  # Make the details page public
            '/static/',
            '/admin/',
            '/api/'
        ]

        # Check if the current URL is in the public URLs list
        is_public = any(request.path.startswith(url) for url in public_urls)

        # If it's not a public URL and the user is not authenticated, redirect to login
        if not is_public and 'auth_token' not in request.session:
            return redirect('login')

        # Continue processing the request
        response = self.get_response(request)
        return response 