# api/urls.py
from django.urls import path
from vorp_api.views import analyze_content, login_view, logout_view, register, user_profile_view

urlpatterns = [
    path('login/', login_view, name='login_view'),
    path('logout/', logout_view, name='logout_view'),
    path('analyze/', analyze_content, name='analyze_content'),
    path('register/', register, name='register'),
    path('user_profile_view/', user_profile_view, name='user_profile_view')
]