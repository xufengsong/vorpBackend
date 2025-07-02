from django.shortcuts import render
from translation.translation_core import callLocalMachine_TranslationwContext, userInputProcess, callOpenAI_TranslationwContext
from .models import Vocabulary, User
# Create your views here.
import logging
# vorp_api/views.py
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
from .serializers import UserSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .forms import CustomUserCreationForm
import json
from openai import OpenAI
import openai
import os
from dotenv import load_dotenv

# =================================================================
# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
# =================================================================

@api_view(['GET']) # Use DRF's decorator
@permission_classes([AllowAny]) # Make this view public
@ensure_csrf_cookie
def get_csrf_token(request):
    """
    This view sends the CSRF token as a cookie.
    The frontend calls this once to get the cookie set.
    """
    return JsonResponse({"detail": "CSRF cookie set"})

@csrf_exempt
def analyze_content(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            content = data.get('content')

            # =================================================
            # START: Add your data processing logic right here!
            # =================================================

            # 'content' holds the string that the user typed in the textarea.
            # You can now use it for any purpose. For example:

            user_tokens = userInputProcess(content)
            # analysis_result = callLocalMachine_TranslationwContext(user_tokens)
            analysis_result = callOpenAI_TranslationwContext(client=client, tokens=user_tokens)

            # ===============================================
            # END: Your data processing logic ends here.
            # ===============================================

            return JsonResponse({
                'message': 'Content received successfully!', 
                'originalContent': content,
                'analysis': analysis_result,
                })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_unknown_vocabs(request):

    print(request.user.email)
    return JsonResponse({
        'message': 'Content received successfully!',
        # 'user': request.user.email,
    })
        

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')

    user = authenticate(request, username=email, password=password)

    if user is not None:
        # THE FIX: Before calling login, explicitly set the user's backend attribute.
        # This tells Django's login function exactly how this user was authenticated.
        user.backend = 'vorp_api.backends.EmailBackend'
        
        # Now, use Django's standard, battle-tested login function.
        login(request, user)
        return Response({'message': 'Login successful'})
    else:
        return Response({'error': 'Invalid credentials'}, status=401)


@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    logout(request) # Django's built-in logout
    return JsonResponse({'message': 'Logout successful!'})


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    # Use DRF's request.data, which handles JSON parsing automatically.
    form = CustomUserCreationForm(request.data)
    
    if form.is_valid():
        user = form.save(commit=False)
        user.is_active = True
        user.save()
        return Response({'message': 'Account created successfully!'}, status=201)
    else:
        # This is the standard way to return validation errors.
        return Response(form.errors, status=400)


@api_view(['GET']) # Explicitly allow GET requests
@permission_classes([IsAuthenticated]) # Enforce that the user must be logged in
def user_profile_view(request):
    """
    A view to get the logged-in user's profile information.
    """

    user = request.user
    
    # Use a serializer to safely convert the user model to JSON.
    serializer = UserSerializer(user) 
    
    return Response(serializer.data)
