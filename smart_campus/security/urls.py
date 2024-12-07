from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('cameras/', views.camera_list, name='camera_list'),
    path('cameras/<int:camera_id>/', views.camera_detail, name='camera_detail'),
    path('cameras/<int:camera_id>/feed/', views.camera_feed, name='camera_feed'),
]
