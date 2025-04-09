from django.db import models

class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.email

class Website(models.Model):
    user_email = models.EmailField()
    business_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField()
    business_type = models.CharField(max_length=100)
    content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.business_name} - {self.user_email}"
