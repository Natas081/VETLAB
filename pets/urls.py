from django.urls import path
from . import views

urlpatterns = [
    # --- ROTAS PRINCIPAIS E DE AUTENTICAÇÃO ---
    # (Estas rotas já estão com o prefixo 'pets/' vindo do projeto)
    path('home/', views.home_view, name='home'),
    path('cadastro/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # --- ROTAS DE PETS ---
    path('', views.pet_list, name='pet_list'), # Raiz (ex: /pets/)
    path('new/', views.pet_create, name='pet_create'), # Correto: /pets/new/
    path('<int:pk>/edit/', views.pet_edit, name='pet_edit'), # Correto: /pets/1/edit/
    path('<int:pk>/delete/', views.pet_delete, name='pet_delete'), # Correto: /pets/1/delete/
    path('<int:pk>/visao-geral/', views.pet_visao_geral, name='pet_visao_geral'),

    # --- ROTAS DE EVENTOS ---
    path('eventos/selecionar-pet/', views.evento_selecionar_pet, name='evento_selecionar_pet'),
    path('<int:pet_pk>/eventos/', views.evento_list, name='evento_list'),
    path('<int:pet_pk>/eventos/adicionar/', views.evento_adicionar, name='evento_adicionar'),
    path('eventos/<int:pk>/editar/', views.evento_edit, name='evento_edit'),
    path('eventos/<int:pk>/excluir/', views.evento_delete, name='evento_delete'),
    path('eventos/<int:pk>/concluir/', views.evento_concluir, name='evento_concluir'),

    # --- ROTAS DE METAS ---
    path('<int:pet_pk>/metas/', views.meta_list, name='meta_list'),
    path('metas/<int:pk>/atualizar-progresso/', views.meta_atualizar_progresso, name='meta_atualizar_progresso'),

    # --- ROTAS DA LISTA DE COMPRAS ---
    path('<int:pet_pk>/compras/', views.shop_list_view, name='shop_list'),
    path('compras/<int:pk>/marcar/', views.shop_item_marcar, name='shop_item_marcar'),
    path('compras/<int:pk>/remover/', views.shop_item_remover, name='shop_item_remover'),
]