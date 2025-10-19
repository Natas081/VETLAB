from django.urls import path
from . import views

urlpatterns = [

    path('', views.pet_list, name='pet_list'),
    path('new/', views.pet_create, name='pet_create'),
    path('<int:pk>/edit/', views.pet_edit, name='pet_edit'),
    path('<int:pk>/delete/', views.pet_delete, name='pet_delete'),
    

    path('eventos/selecionar-pet/', views.evento_selecionar_pet, name='evento_selecionar_pet'),
    
    path('eventos/adicionar/<int:pet_pk>/', views.evento_adicionar, name='evento_adicionar'),
    path('eventos/<int:pk>/editar/', views.evento_edit, name='evento_edit'),
    path('eventos/<int:pk>/excluir/', views.evento_delete, name='evento_delete'),
    path('eventos/<int:pk>/concluir/', views.evento_concluir, name='evento_concluir'),

    path('<int:pet_pk>/eventos/', views.evento_list, name='evento_list'),
]