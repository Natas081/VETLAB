from django.urls import path
from . import views

urlpatterns = [
    # URLs de Pet (sem alteração)
    path('', views.pet_list, name='pet_list'),
    path('new/', views.pet_create, name='pet_create'),
    path('<int:pk>/edit/', views.pet_edit, name='pet_edit'),
    path('<int:pk>/delete/', views.pet_delete, name='pet_delete'),
    
    # --- NOVAS URLS PARA O FLUXO DE EVENTOS ---
    # Passo 1: Página para selecionar o pet
    path('eventos/selecionar-pet/', views.evento_selecionar_pet, name='evento_selecionar_pet'),
    
    # Passo 2: Página do formulário para adicionar o evento, passando o ID do pet
    path('eventos/adicionar/<int:pet_pk>/', views.evento_adicionar, name='evento_adicionar'),
    
    # URLs para editar e deletar um evento específico (podem continuar as mesmas)
    path('eventos/<int:pk>/editar/', views.evento_edit, name='evento_edit'),
    path('eventos/<int:pk>/excluir/', views.evento_delete, name='evento_delete'),
    # Manteremos a lista de eventos de um pet, pois é útil
    path('<int:pet_pk>/eventos/', views.evento_list, name='evento_list'),
]