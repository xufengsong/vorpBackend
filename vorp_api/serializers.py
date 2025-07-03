from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Define the fields you want to send to the frontend.
        # NEVER include the password hash.
        fields = [
            'id',  # don't delete this?
            'email', 
            'name', # don't delete this?
            'username',
            'unknown_words',
            'motherLanguage', 
            'targetLanguage', 
            'fluencyLevel'
        ]