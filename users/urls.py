from django.urls import path
from users.views import (
    csrf_view,
    login_view,
    logout_view,
    me_view,
    profile_view,
    register_view,
)

urlpatterns = [
    path('auth/csrf/', csrf_view, name='users-csrf'),
    path('auth/register/', register_view, name='users-register'),
    path('auth/login/', login_view, name='users-login'),
    path('auth/logout/', logout_view, name='users-logout'),
    path('auth/me/', me_view, name='users-me'),
    path('profile/', profile_view, name='users-profile'),
]