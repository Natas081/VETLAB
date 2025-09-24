from django.urls import path
from . import views

urlpatterns = [
    path('', views.pet_list, name='pet_list'),
    path('new/', views.pet_create, name='pet_create'),
    path('<int:pk>/edit/', views.pet_edit, name='pet_edit'),
    path('<int:pk>/delete/', views.pet_delete, name='pet_delete'),
]
