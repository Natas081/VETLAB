from django.urls import path
from . import views

urlpatterns = [
    # --- ROTAS PRINCIPAIS E DE AUTENTICAÇÃO ---
    
    # Mantém a sua lista de pets como a raiz (quando logado)
    path('', views.pet_list, name='pet_list'), 
    
    # ADICIONADO: A rota 'home' que faltava para o logout funcionar
    path('home/', views.home_view, name='home'), 
    
    path('cadastro/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # --- ROTAS DE PETS ---
    path('pets/new/', views.pet_create, name='pet_create'),
    path('pets/<int:pk>/edit/', views.pet_edit, name='pet_edit'),
    path('pets/<int:pk>/delete/', views.pet_delete, name='pet_delete'),
    path('pets/<int:pk>/visao-geral/', views.pet_visao_geral, name='pet_visao_geral'),

    # --- ROTAS DE EVENTOS ---
    path('eventos/selecionar-pet/', views.evento_selecionar_pet, name='evento_selecionar_pet'),
    path('<int:pet_pk>/eventos/', views.evento_list, name='evento_list'),
    path('eventos/adicionar/<int:pet_pk>/', views.evento_adicionar, name='evento_adicionar'),
    path('eventos/<int:pk>/editar/', views.evento_edit, name='evento_edit'),
    path('eventos/<int:pk>/excluir/', views.evento_delete, name='evento_delete'),
    path('eventos/<int:pk>/concluir/', views.evento_concluir, name='evento_concluir'),

    # --- ROTAS DE METAS ---
    path('<int:pet_pk>/metas/', views.meta_list, name='meta_list'),
    path('metas/<int:pk>/atualizar-progresso/', views.meta_atualizar_progresso, name='meta_atualizar_progresso'),

    # --- ROTAS DO PET SHOP (ADICIONADAS) ---
    path('admin/popular-loja-agora/', views.popular_loja_view, name='popular_loja_view'),
    path('shop/', views.shop_list_view, name='shop_list'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:produto_pk>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/remove/<int:produto_pk>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('purchase-success/', views.purchase_success_view, name='purchase_success'),
]