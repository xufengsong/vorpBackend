# api/urls.py
from django.urls import path
from vorp_api.views import analyze_content, login_view, logout_view, register, user_profile_view, add_unknown_vocabs, get_csrf_token

urlpatterns = [
    path('login/', login_view, name='login_view'),
    path('logout/', logout_view, name='logout_view'),
    path('analyze/', analyze_content, name='analyze_content'),
    path('register/', register, name='register'),
    path('update_vocabulary/', add_unknown_vocabs, name='add_unknown_vocab'),
    path('user_profile_view/', user_profile_view, name='user_profile_view'),
    path('get-csrf-token/', get_csrf_token, name='get-csrf-token'),
]