from django.urls import path
from . import views

urlpatterns = [
    path('', views.incident_list, name='incident_list'),
    path('<int:incident_id>/', views.incident_detail, name='incident_detail'),
    path('create/', views.incident_create, name='incident_create'),
]
