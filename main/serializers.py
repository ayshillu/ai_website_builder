from rest_framework import serializers
from .models import User, Website
import bcrypt

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        password = validated_data.pop('password')
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        validated_data['password'] = hashed_pw
        return User.objects.create(**validated_data)

# ✅ Add this block for WebsiteSerializer
class WebsiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        fields = '__all__'
