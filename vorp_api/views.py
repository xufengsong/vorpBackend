from django.shortcuts import render
from translation.translation_core import callLocalMachine_TranslationwContext, userInputProcess
# Create your views here.

# vorp_api/views.py
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm
import json

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
            analysis_result = callLocalMachine_TranslationwContext(user_tokens)

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


@csrf_exempt
def login_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return JsonResponse({'error': 'Email and password are required'}, status=400)

        # Use Django's built-in authenticate function.
        # It securely checks the hashed password in the database.
        user = authenticate(request, email=email, password=password)

        if user is not None:
            # If authentication is successful, 'user' is a User object.
            # The 'login' function creates a secure session for the user.
            login(request, user)
            return JsonResponse({
                'message': 'Login successful!',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                }
            })
        else:
            # If authenticate returns None, the credentials were wrong.
            return JsonResponse({'error': 'Invalid credentials'}, status=401)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@csrf_exempt # You need a way to log out too!
def logout_view(request):
    logout(request) # Django's built-in logout
    return JsonResponse({'message': 'Logout successful!'})


@csrf_exempt
def register(request):
    if request.method == 'POST':

        try:
            # 1. Load the JSON data from the request body
            data = json.loads(request.body)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': "Invalid JSON data provided."}, status=400)
        
        # This is a POST request, process the form data
        form = CustomUserCreationForm(data)
        # print(form)
        if form.is_valid():
            form.save() # This is the key step! Django handles creating the user in the database.
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return JsonResponse({
                "userNane": form.cleaned_data.get('username'),
                "email": form.cleaned_data.get('email'),
                "motherLanguage": form.cleaned_data.get('motherLanguage'),
                "targetLanguage": form.cleaned_data.get('targetLanguage'),
                "fluencyLevel": form.cleaned_data.get('fluencyLevel')})
        # else:

    else:
        # This is a GET request, just display a blank form
        form = CustomUserCreationForm()
    # return render(request, '../vorp-lingua-scribe/src/pages/SignUp.tsx', {'form': form})
    return JsonResponse({'error': "There are something wrong"})


# @login_required
@csrf_exempt
def user_profile_view(request):
    """
    A view to get the logged-in user's profile information.
    """
    # Use this check instead of the @login_required decorator
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    if request.method == 'GET':
        user = request.user
        return JsonResponse({
            'username': user.username,
            'email': user.email,
            'motherLanguage': user.motherLanguage,
            'targetLanguage': user.targetLanguage,
            'fluencyLevel': user.fluencyLevel,
            # 'known_words': user.known_words,
        })
    return JsonResponse({'error': 'Invalid request method'}, status=405)