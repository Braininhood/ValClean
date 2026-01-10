"""
Accounts app URLs with security prefix /api/aut/
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'accounts'

router = DefaultRouter()
router.register(r'profile', views.ProfileViewSet, basename='profile')

urlpatterns = [
    # Authentication endpoints (public)
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('me/', views.user_profile_view, name='user-profile'),
    path('check-email/', views.check_email_view, name='check-email'),
] + router.urls
