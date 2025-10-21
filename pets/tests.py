from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Pet
import datetime

# Testes são como "mini robôs" que verificam se o seu código funciona como esperado.
# Cada função que começa com "test_" é um teste individual.

class VetLabTestCase(TestCase):
    
    def setUp(self):
        """
        Esta função é executada ANTES de cada teste. 
        É útil para criar objetos que usaremos em vários testes.
        """
        # Criamos dois usuários de teste para simular diferentes tutores
        self.user_a = User.objects.create_user(username='tutor_a', password='password123')
        self.user_b = User.objects.create_user(username='tutor_b', password='password456')
        
        # Criamos um pet que pertence ao tutor_a
        self.pet_a = Pet.objects.create(
            tutor=self.user_a,
            nome='Rex',
            especie='Cachorro',
            data_nascimento=datetime.date(2020, 1, 1),
            peso=15.5
        )
        
        # O self.client é um navegador falso que podemos usar para visitar as páginas
        self.client = Client()

    # --- Testes de Páginas Públicas ---

    def test_pagina_inicial_carrega_corretamente(self):
        """ Testa se a página inicial (home) está acessível. """
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200) # 200 = Sucesso
        self.assertTemplateUsed(response, 'pets/home.html')

    # --- Testes do Sistema de Login ---

    def test_usuario_nao_logado_e_redirecionado(self):
        """ 
        Testa a regra de segurança mais importante: se um usuário não logado 
        tenta acessar a lista de pets, ele deve ser enviado para a página de login.
        """
        response = self.client.get(reverse('pet_list'))
        self.assertEqual(response.status_code, 302) # 302 = Redirecionamento
        # MUDANÇA AQUI: Adicionamos o prefixo /pets/ ao endereço esperado
        self.assertRedirects(response, '/pets/login/?next=/pets/')

    def test_usuario_logado_consegue_ver_a_lista_de_pets(self):
        """ Testa se, após o login, o usuário consegue ver a página da lista de pets. """
        self.client.login(username='tutor_a', password='password123')
        response = self.client.get(reverse('pet_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pets/pet_list.html')
        
    def test_logout_funciona(self):
        """ Testa se a função de logout desconecta o usuário e o redireciona. """
        self.client.login(username='tutor_a', password='password123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        # Verifica se o usuário não está mais autenticado
        self.assertFalse('_auth_user_id' in self.client.session)

    # --- Testes de Funcionalidades dos Pets ---

    def test_usuario_so_ve_seus_proprios_pets(self):
        """
        O teste mais importante! Garante que um usuário não consegue ver os pets de outro.
        """
        # Faz login como tutor_a
        self.client.login(username='tutor_a', password='password123')
        response = self.client.get(reverse('pet_list'))
        
        # Verifica se a página contém o nome do pet 'Rex' (que pertence ao tutor_a)
        self.assertContains(response, 'Rex')
        
        # Agora, faz login como tutor_b
        self.client.login(username='tutor_b', password='password456')
        response = self.client.get(reverse('pet_list'))
        
        # Verifica se a página NÃO contém o nome 'Rex'
        self.assertNotContains(response, 'Rex')
        # Verifica se a página mostra a mensagem de "Nenhum pet cadastrado"
        self.assertContains(response, 'Nenhum pet cadastrado ainda.')

    def test_criar_pet_funciona_para_usuario_logado(self):
        """ Testa se um usuário logado consegue criar um novo pet. """
        self.client.login(username='tutor_a', password='password123')
        
        # Conta quantos pets o tutor_a tem ANTES de criar um novo
        pet_count_before = Pet.objects.filter(tutor=self.user_a).count()
        
        # Simula o envio do formulário de criação
        response = self.client.post(reverse('pet_create'), {
            'nome': 'Bolinha',
            'especie': 'Gato',
            'data_nascimento': '2022-05-10',
            'peso': '4.2'
        })
        
        # Conta quantos pets o tutor_a tem DEPOIS de criar
        pet_count_after = Pet.objects.filter(tutor=self.user_a).count()
        
        # Verifica se fomos redirecionados para a lista de pets (sinal de sucesso)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('pet_list'))
        # Verifica se o número de pets aumentou em 1
        self.assertEqual(pet_count_after, pet_count_before + 1)
