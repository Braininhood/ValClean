"""
URL configuration for customers app.
"""
from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('', views.customer_list, name='customer_list'),
    path('create/', views.customer_create, name='customer_create'),
    path('<int:pk>/', views.customer_detail, name='customer_detail'),
    path('<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('<int:pk>/delete/', views.customer_delete, name='customer_delete'),
]
