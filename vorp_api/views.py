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
import openai
from openai import OpenAI
import openai
import os
from dotenv import load_dotenv

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


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
    """
    Adds a vocabulary word to the user's 'unknown' lists.
    Expects a 'word' and a 'status' ('known' or 'unknown') in the request body.
    """
    # print(request.user.email)
    # return JsonResponse({
    #     'message': 'Content received successfully!',
    #     'user': request.user.email,
    # })

    wordAnalysis_list = request.data.get('words')
    print(wordAnalysis_list)
    # status_update = request.data.get('status') # 'known' or 'unknown'

    # --- Input Validation ---
    if not wordAnalysis_list:
        return Response({"error": "Word not provided."}, status=status.HTTP_400_BAD_REQUEST)
    
    # if status_update not in ['known', 'unknown']:
    #     return Response({"error": "Status must be 'known' or 'unknown'."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # `request.user` is the currently authenticated user instance.
        current_user = request.user

        for wordAnalysis in wordAnalysis_list:

            # *** EDITED: First, determine the base form of the input word. ***
            base_form = wordAnalysis['baseForm']
            word = wordAnalysis['word']
            meaning = wordAnalysis['meaning']
            print(base_form)
            print(word)
            print(meaning)

            # Get the vocabulary object for the base_form, or create it if it doesn't exist.
            vocabulary_obj, created = Vocabulary.objects.get_or_create(
                baseForm=base_form, 
                defaults={
                    'word': word,
                    'meanings': meaning}
            )

            # # --- Logic to update user's lists ---
            # if status_update == 'known':
            #     # Check if the word is already in the known_words list
            #     if current_user.known_words.filter(pk=vocabulary_obj.pk).exists():
            #         return Response({"info": f"'{word_to_update}' (base form: {base_form}) is already in your known words list."}, status=status.HTTP_200_OK)

            #     # Add to known_words list
            #     current_user.known_words.add(vocabulary_obj)
                
            #     # *** FIXED: Only remove from unknown_words if it exists there ***
            #     if current_user.unknown_words.filter(pk=vocabulary_obj.pk).exists():
            #         current_user.unknown_words.remove(vocabulary_obj)

            #     message = f"'{word_to_update}' marked as known."
            
            # else: # status_update == 'unknown'
            #     # Check if the word is already in the unknown_words list
            #     if current_user.unknown_words.filter(pk=vocabulary_obj.pk).exists():
            #         return Response({"info": f"'{word_to_update}' (base form: {base_form}) is already in your unknown words list."}, status=status.HTTP_200_OK)

            #     # Add to unknown_words list
            #     current_user.unknown_words.add(vocabulary_obj)

            #     # *** FIXED: Only remove from known_words if it exists there ***
            #     if current_user.known_words.filter(pk=vocabulary_obj.pk).exists():
            #         current_user.known_words.remove(vocabulary_obj)
                    
            #     message = f"'{word_to_update}' marked as unknown."

            # # The .add() and .remove() methods for ManyToManyFields don't require calling .save() on the user instance.

            # return Response({"success": message}, status=status.HTTP_200_OK)

            # Check if the word is already in the unknown_words list
            if current_user.unknown_words.filter(pk=vocabulary_obj.pk).exists():
                return Response({"info": f"'{wordAnalysis['word']}' (base form: {base_form}) is already in your known words list."}, status=status.HTTP_200_OK)

            # Add to known_words list
            current_user.unknown_words.add(vocabulary_obj)
            
            # *** FIXED: Only remove from unknown_words if it exists there ***
            # if current_user.unknown_words.filter(pk=vocabulary_obj.pk).exists():
            #     current_user.unknown_words.remove(vocabulary_obj)

            message = f"'{wordAnalysis['baseForm']}' marked as unknown."
        return Response({"success": message}, status=status.HTTP_200_OK)

    except Exception as e:
        # It's good practice to log the actual error for debugging
        # import logging
        logging.error(f"Error updating vocabulary for user {request.user.email}: {e}")
        return Response({"error": "An internal error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

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
