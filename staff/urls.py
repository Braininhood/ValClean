"""
URL configuration for staff app.
"""
from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('', views.staff_list, name='staff_list'),
    path('create/', views.staff_create, name='staff_create'),
    path('<int:pk>/', views.staff_detail, name='staff_detail'),
    path('<int:pk>/edit/', views.staff_edit, name='staff_edit'),
    path('<int:pk>/delete/', views.staff_delete, name='staff_delete'),
    path('<int:staff_pk>/schedule/', views.staff_schedule_edit, name='staff_schedule_edit'),
]

