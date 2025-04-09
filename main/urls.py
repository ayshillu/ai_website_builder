from django.urls import path
from . import views
from main.api_views import WebsiteCreateAPIView

urlpatterns = [
    path('', views.index, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('create/', views.create, name='create'),
    path('details/', views.details, name='details'),
    path('generate/', views.generate_website, name='generate'),
    path('websites/', views.get_websites, name='websites'),
    path('websites/<int:website_id>/', views.update_website, name='update_website'),
    path('websites/delete/<int:website_id>/', views.delete_website, name='delete_website'),
    path('api/create-website/', WebsiteCreateAPIView.as_view(), name='create_website_api'),
]
