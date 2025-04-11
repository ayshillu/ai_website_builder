from django.urls import path
from . import views
from main.api_views import WebsiteCreateAPIView, WebsiteListAPIView, WebsiteFormAPIView

urlpatterns = [
    path('', views.index, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('details/', views.details, name='details'),
    path('generate/', views.generate_website, name='generate'),
    path('websites/', views.get_websites, name='websites'),
    path('websites/<int:website_id>/', views.update_website, name='update_website'),
    path('websites/delete/<int:website_id>/', views.delete_website, name='delete_website'),
    path('websites/view/<int:website_id>/', views.view_website, name='view_website'),
    path('mongodb-diagnostic/', views.mongodb_diagnostic, name='mongodb_diagnostic'),
    path('generate-website-layout/', views.generate_website_layout, name='generate_website_layout'),
    path('view-generated-website/', views.view_generated_website, name='view_generated_website'),
    path('view-generated-website/<str:website_id>/', views.view_generated_website, name='view_generated_website_by_id'),
    path('api/create-website/', WebsiteCreateAPIView.as_view(), name='create_website_api'),
    path('api/websites/', WebsiteListAPIView.as_view(), name='list_websites_api'),
    path('api/website-form/', WebsiteFormAPIView.as_view(), name='website_form_api'),
    path('api/signup/', views.signup, name='api_signup'),
    path('api/login/', views.login, name='api_login'),
]
