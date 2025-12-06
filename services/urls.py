"""
URL configuration for services app.
"""
from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Services
    path('', views.service_list, name='service_list'),
    path('create/', views.service_create, name='service_create'),
    path('<int:pk>/', views.service_detail, name='service_detail'),
    path('<int:pk>/edit/', views.service_edit, name='service_edit'),
    path('<int:pk>/delete/', views.service_delete, name='service_delete'),
]

