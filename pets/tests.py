from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from django.contrib.auth.models import User
# IMPORTA O NOVO MODELO 'PRODUTO'
from pets.models import Pet, Evento, Meta, Produto 
import time
import os
from datetime import date
import decimal # Para o preço

# ===============================================
# CLASSE BASE - CONFIGURAÇÃO E LOGIN
# ===============================================
class BaseE2ETestCase(StaticLiveServerTestCase):
    """
    Classe base para configurar WebDriver e realizar login antes de cada teste.
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = Options()
        if os.environ.get('GITHUB_ACTIONS') == 'true':
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
        
        cls.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        cls.driver.implicitly_wait(10)
        cls.wait = WebDriverWait(cls.driver, 15) # Espera explícita de 15 segundos

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        """
        Executa antes de CADA teste. Cria um usuário e faz login via UI.
        """
        super().setUp()
        self.username = f'testuser_{int(time.time())}'
        self.password = 'testpass123'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        
        self.driver.get(f'{self.live_server_url}/pets/login/')
        self.driver.find_element(By.ID, "username").send_keys(self.username)
        self.driver.find_element(By.ID, "password").send_keys(self.password)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1")))
        self.wait.until(EC.url_contains('/pets/'))
        print(f"\nUsuário '{self.username}' logado para o teste.")
        time.sleep(1)

# ===============================================
# HISTÓRIA 1: CADASTRO DO PET
# ===============================================
class TesteHistoria1CadastroPet(BaseE2ETestCase):

    def test_cenario_1_cadastro_bem_sucedido(self):
        print("\nIniciando Teste: História 1, Cenário 1 - Cadastro bem-sucedido")
        driver = self.driver
        
        print("Clicando em Adicionar Novo Pet...")
        self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Adicionar Novo Pet"))).click()
        self.wait.until(EC.url_contains('/pets/new/'))
        print("Preenchendo formulário do pet 'Bolinha'...")
        driver.find_element(By.ID, "id_nome").send_keys("Bolinha")
        driver.find_element(By.ID, "id_especie").send_keys("Gato")
        driver.find_element(By.ID, "id_data_nascimento").send_keys("2021-08-01")
        driver.find_element(By.ID, "id_peso").send_keys("5.1")
        time.sleep(2)
        
        print("Clicando em Salvar...")
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
        
        print("Verificando se 'Bolinha' está na lista...")
        self.wait.until(EC.url_contains('/pets/'))
        # Verifica a mensagem de sucesso
        mensagem_sucesso = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.success')))
        self.assertIn("Pet 'Bolinha' adicionado", mensagem_sucesso.text)
        # Verifica se o nome está na lista
        lista_pets_div = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.pet-list')))
        self.assertIn("Bolinha", lista_pets_div.text)
        print("Teste Cenário 1 concluído.")
        time.sleep(3)

    def test_cenario_2_cadastro_campos_obrigatorios_em_branco(self):
        print("\nIniciando Teste: História 1, Cenário 2 - Campos obrigatórios em branco")
        driver = self.driver
        
        driver.get(f'{self.live_server_url}/pets/')
        self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Adicionar Novo Pet"))).click()
        self.wait.until(EC.url_contains('/pets/new/'))

        print("Tentando submeter formulário vazio...")
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
        
        print("Verificando mensagem de erro...")
        # <<< CORRIGIDO: Procura pela mensagem de erro do Django messages >>>
        mensagem_erro = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.error')))
        self.assertIn("obrigatórios", mensagem_erro.text)
        print("Teste Cenário 2 concluído.")
        time.sleep(3)

    def test_cenario_3_cadastro_peso_negativo(self):
        print("\nIniciando Teste: História 1, Cenário 3 - Peso negativo")
        driver = self.driver

        driver.get(f'{self.live_server_url}/pets/')
        self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Adicionar Novo Pet"))).click()
        self.wait.until(EC.url_contains('/pets/new/'))

        print("Preenchendo com peso negativo...")
        driver.find_element(By.ID, "id_nome").send_keys("Negativo")
        driver.find_element(By.ID, "id_especie").send_keys("Hamster")
        driver.find_element(By.ID, "id_data_nascimento").send_keys("2023-01-01")
        driver.find_element(By.ID, "id_peso").send_keys("-0.5")
        time.sleep(2)

        print("Submetendo formulário...")
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()

        print("Verificando mensagem de erro...")
        # <<< CORRIGIDO: Procura pela mensagem de erro do Django messages >>>
        mensagem_erro = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.error')))
        self.assertIn("positivo", mensagem_erro.text)
        print("Teste Cenário 3 concluído.")
        time.sleep(3)

# ===============================================
# HISTÓRIA 2: GERENCIAR PETS
# ===============================================
class TesteHistoria2GerenciarPets(BaseE2ETestCase):

    def setUp(self):
        super().setUp()
        self.pet = Pet.objects.create(
            tutor=self.user, nome="PetGerencia", especie="Coelho", 
            data_nascimento=date(2023, 5, 1), peso=1.8
        )
        print(f"Pet '{self.pet.nome}' criado no banco para os testes de gerenciamento.")

    def test_cenario_1_exibir_lista_e_visualizar(self):
        print("\nIniciando Teste: História 2, Cenário 1 - Exibir lista e visualizar")
        driver = self.driver
        
        driver.get(f'{self.live_server_url}/pets/')
        print("Verificando se 'PetGerencia' está na lista...")
        lista_pets_div = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.pet-list')))
        self.assertIn("PetGerencia", lista_pets_div.text)
        print("Pet encontrado na lista.")
        time.sleep(2)

        print("Clicando em Visão Geral...")
        pet_item = self.wait.until(
             EC.presence_of_element_located((By.XPATH, f"//div[contains(@class, 'pet-item') and .//span[contains(text(), '{self.pet.nome}')]]"))
        )
        self.wait.until(EC.element_to_be_clickable(pet_item.find_element(By.LINK_TEXT, "Visão Geral"))).click()

        print("Verificando página de visão geral...")
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), f"Visão Geral: {self.pet.nome}"))
        self.assertIn(f"Visão Geral: {self.pet.nome}", driver.find_element(By.TAG_NAME, 'h1').text)
        print("Teste Cenário 1 concluído.")
        time.sleep(3)

    def test_cenario_3_edicao_bem_sucedida(self):
        print("\nIniciando Teste: História 2, Cenário 3 - Edição bem-sucedida")
        driver = self.driver
        
        driver.get(f'{self.live_server_url}/pets/')
        pet_item = self.wait.until(
             EC.presence_of_element_located((By.XPATH, f"//div[contains(@class, 'pet-item') and .//span[contains(text(), '{self.pet.nome}')]]"))
        )
        print("Clicando em Editar...")
        self.wait.until(EC.element_to_be_clickable(pet_item.find_element(By.LINK_TEXT, "Editar"))).click()
        self.wait.until(EC.url_contains('/edit/'))
        
        print("Editando nome para 'PetEditado'...")
        campo_nome = self.wait.until(EC.presence_of_element_located((By.ID, "id_nome")))
        campo_nome.clear()
        campo_nome.send_keys("PetEditado")
        time.sleep(2)
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
        
        print("Verificando alteração na lista e mensagem de sucesso...")
        self.wait.until(EC.url_contains('/pets/'))
        mensagem_sucesso = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.success')))
        self.assertIn("atualizados com sucesso", mensagem_sucesso.text)
        lista_pets_div_depois = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.pet-list')))
        self.assertIn("PetEditado", lista_pets_div_depois.text)
        self.assertNotIn("PetGerencia", lista_pets_div_depois.text)
        print("Teste Cenário 3 concluído.")
        time.sleep(3)

    def test_cenario_5_exclusao_bem_sucedida(self):
        print("\nIniciando Teste: História 2, Cenário 5 - Exclusão bem-sucedida")
        driver = self.driver

        driver.get(f'{self.live_server_url}/pets/')
        pet_item = self.wait.until(
             EC.presence_of_element_located((By.XPATH, f"//div[contains(@class, 'pet-item') and .//span[contains(text(), '{self.pet.nome}')]]"))
        )
        print("Clicando em Excluir...")
        self.wait.until(EC.element_to_be_clickable(pet_item.find_element(By.LINK_TEXT, "Excluir"))).click()
        self.wait.until(EC.url_contains('/delete/'))
        print("Página de confirmação acessada.")
        time.sleep(2)

        print("Confirmando exclusão...")
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.delete-btn.primary"))).click()

        print("Verificando se o pet foi removido e mensagem de sucesso...")
        self.wait.until(EC.url_contains('/pets/'))
        mensagem_sucesso = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.success')))
        self.assertIn("removido com sucesso", mensagem_sucesso.text)
        self.wait.until(
            EC.any_of(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'pet-item-empty')]")),
                EC.staleness_of(pet_item)
            )
        )
        time.sleep(1)
        self.assertNotIn(self.pet.nome, driver.find_element(By.TAG_NAME, 'body').text)
        print("Teste Cenário 5 concluído.")
        time.sleep(3)

# ===============================================
# HISTÓRIA 3: CADASTRO DE EVENTOS
# ===============================================
class TesteHistoria3CadastroEvento(BaseE2ETestCase):

    def setUp(self):
        super().setUp()
        self.pet = Pet.objects.create(tutor=self.user, nome="PetEventos", especie="Papagaio", data_nascimento=date(2024, 1, 1), peso=0.8)
        print(f"Pet '{self.pet.nome}' criado no banco para os testes de eventos.")

    def test_cenario_1_evento_adicionado_com_sucesso(self):
        print("\nIniciando Teste: História 3, Cenário 1 - Evento adicionado com sucesso")
        driver = self.driver

        driver.get(f'{self.live_server_url}/pets/')
        pet_item = self.wait.until(
            EC.presence_of_element_located((By.XPATH, f"//div[contains(@class, 'pet-item') and .//span[contains(text(), '{self.pet.nome}')]]"))
        )
        print("Clicando em Eventos...")
        self.wait.until(EC.element_to_be_clickable(pet_item.find_element(By.LINK_TEXT, "Eventos"))).click()
        self.wait.until(EC.url_contains('/eventos/'))
        time.sleep(1)

        print("Clicando em Adicionar Novo Evento...")
        self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Adicionar Novo Evento"))).click()
        self.wait.until(EC.url_contains('/eventos/adicionar/'))
        time.sleep(1)

        print("Preenchendo formulário do evento 'Consulta'...")
        Select(self.wait.until(EC.presence_of_element_located((By.NAME, "tipo")))).select_by_value("consulta") 
        driver.find_element(By.NAME, "data").send_keys("2025-11-20")
        driver.find_element(By.NAME, "observacoes").send_keys("Checkup")
        time.sleep(2)

        print("Clicando em Adicionar...")
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()

        print("Verificando se o evento 'Consulta' foi criado e mensagem de sucesso...")
        self.wait.until(EC.url_contains('/eventos/'))
        mensagem_sucesso = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.success')))
        self.assertIn("Evento adicionado!", mensagem_sucesso.text)
        lista_eventos_div = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.pet-list')))
        self.assertIn("Consulta", lista_eventos_div.text)
        print("Teste Cenário 1 concluído.")
        time.sleep(3)

    def test_cenario_3_adicionar_evento_dados_incompletos(self):
        print("\nIniciando Teste: História 3, Cenário 3 - Adicionar evento dados incompletos")
        driver = self.driver

        driver.get(f'{self.live_server_url}/pets/')
        pet_item = self.wait.until(
            EC.presence_of_element_located((By.XPATH, f"//div[contains(@class, 'pet-item') and .//span[contains(text(), '{self.pet.nome}')]]"))
        )
        self.wait.until(EC.element_to_be_clickable(pet_item.find_element(By.LINK_TEXT, "Eventos"))).click()
        self.wait.until(EC.url_contains('/eventos/'))
        self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Adicionar Novo Evento"))).click()
        self.wait.until(EC.url_contains('/eventos/adicionar/'))
        time.sleep(1)

        print("Deixando campo 'data' em branco e submetendo...")
        Select(self.wait.until(EC.presence_of_element_located((By.NAME, "tipo")))).select_by_value("vacina") 
        time.sleep(2)
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()

        print("Verificando mensagem de erro...")
        # <<< CORRIGIDO: Procura pela mensagem de erro do Django messages >>>
        mensagem_erro = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.error')))
        self.assertIn("obrigatórios", mensagem_erro.text)
        print("Teste Cenário 3 concluído.")
        time.sleep(3)


# ===============================================
# HISTÓRIA 4: CONCLUSÃO DE EVENTOS
# ===============================================
class TesteHistoria4ConclusaoEvento(BaseE2ETestCase):

    def setUp(self):
        super().setUp()
        self.pet = Pet.objects.create(tutor=self.user, nome="PetConcluirEvento", especie="Cachorro", data_nascimento=date(2022, 1, 1), peso=10)
        self.evento = Evento.objects.create(pet=self.pet, tipo="medicamento", data=date(2025,10,10), observacoes="Remédio X")
        print(f"Pet '{self.pet.nome}' e Evento '{self.evento.get_tipo_display()}' criados no banco.")

    def test_cenario_1_evento_concluido_com_sucesso(self):
        print("\nIniciando Teste: História 4, Cenário 1 - Evento concluído com sucesso")
        driver = self.driver

        driver.get(f'{self.live_server_url}/pets/{self.pet.pk}/eventos/')
        self.wait.until(EC.url_contains('/eventos/'))

        print("Encontrando o evento Medicamento...")
        evento_item = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'pet-item') and contains(., 'Medicamento')]"))
        )
        print("Clicando em Concluir...")
        self.wait.until(EC.element_to_be_clickable(evento_item.find_element(By.LINK_TEXT, "Concluir"))).click()
        
        print("Verificando se o evento foi marcado como concluído...")
        mensagem_sucesso = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.success')))
        self.assertIn("Evento marcado como concluído!", mensagem_sucesso.text)
        
        evento_item_atualizado = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'pet-item') and contains(@class, 'concluido') and contains(., 'Medicamento')]"))
        )
        self.assertIn("(Concluído)", evento_item_atualizado.text)
        print("Teste Cenário 1 concluído.")
        time.sleep(3)

    def test_cenario_3_concluir_evento_ja_concluido(self):
        print("\nIniciando Teste: História 4, Cenário 3 - Concluir evento já concluído")
        driver = self.driver
        self.evento.concluido = True
        self.evento.save()
        print("Evento já marcado como concluído no banco.")

        driver.get(f'{self.live_server_url}/pets/{self.pet.pk}/eventos/')
        self.wait.until(EC.url_contains('/eventos/'))

        print("Verificando que o botão 'Concluir' não existe...")
        evento_item_concluido = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'pet-item') and contains(., 'Medicamento')]"))
        )
        # Verifica que o botão não está lá
        concluir_buttons = evento_item_concluido.find_elements(By.LINK_TEXT, "Concluir")
        self.assertEqual(len(concluir_buttons), 0)
        self.assertIn("(Concluído)", evento_item_concluido.text)
        
        print("Tentando acessar URL de concluir diretamente...")
        url_concluir_direta = f'{self.live_server_url}/pets/eventos/{self.evento.pk}/concluir/'
        driver.get(url_concluir_direta)

        print("Verificando mensagem de aviso...")
        mensagem_aviso = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.warning')))
        self.assertIn("Esse evento já foi concluído.", mensagem_aviso.text)
        print("Teste Cenário 3 concluído.")
        time.sleep(3)


# ===============================================
# HISTÓRIA 5: CADASTRO DE METAS
# ===============================================
class TesteHistoria5CadastroMeta(BaseE2ETestCase):

    def setUp(self):
        super().setUp()
        self.pet = Pet.objects.create(tutor=self.user, nome="PetMetas", especie="Gato", data_nascimento=date(2020, 2, 14), peso=6)
        print(f"Pet '{self.pet.nome}' criado no banco para os testes de metas.")

    def test_cenario_1_meta_adicionada_com_sucesso(self):
        print("\nIniciando Teste: História 5, Cenário 1 - Meta adicionada com sucesso")
        driver = self.driver

        driver.get(f'{self.live_server_url}/pets/{self.pet.pk}/metas/')
        self.wait.until(EC.url_contains('/metas/'))
        print("Página de metas acessada.")
        time.sleep(1)

        print("Preenchendo formulário da meta...")
        driver.find_element(By.NAME, "descricao").send_keys("Manter a caixa de areia limpa")
        driver.find_element(By.NAME, "data_prazo").send_keys("2026-03-01")
        time.sleep(2)

        print("Clicando em Adicionar...")
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "form.meta-form button[type='submit']"))).click()
        
        print("Verificando se a meta foi criada e mensagem de sucesso...")
        mensagem_sucesso = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.success')))
        self.assertIn("Meta adicionada!", mensagem_sucesso.text)
        
        lista_metas_div = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.pet-list')))
        self.assertIn("Manter a caixa de areia limpa", lista_metas_div.text)
        print("Teste Cenário 1 concluído.")
        time.sleep(3)

    def test_cenario_3_adicionar_meta_dados_incompletos(self):
        print("\nIniciando Teste: História 5, Cenário 3 - Adicionar meta dados incompletos")
        driver = self.driver

        driver.get(f'{self.live_server_url}/pets/{self.pet.pk}/metas/')
        self.wait.until(EC.url_contains('/metas/'))
        time.sleep(1)

        print("Deixando campo 'data_prazo' em branco e submetendo...")
        driver.find_element(By.NAME, "descricao").send_keys("Meta sem data")
        time.sleep(2)
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "form.meta-form button[type='submit']"))).click()

        print("Verificando mensagem de erro...")
        mensagem_erro = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.error')))
        self.assertIn("Preencha a descrição e a data", mensagem_erro.text)
        print("Teste Cenário 3 concluído.")
        time.sleep(3)


# ===============================================
# <<< NOVA HISTÓRIA 8: PET SHOP >>>
# ===============================================
class TesteHistoria8PetShop(BaseE2ETestCase):
    
    def setUp(self):
        """ Cria dados para os testes da loja """
        super().setUp() # Faz login
        # Cria produtos no banco de dados
        self.produto1 = Produto.objects.create(
            nome="Ração Super Premium", emoji="🐶",
            descricao="Ração para cães de porte médio.",
            preco=decimal.Decimal("150.00"), estoque=20
        )
        self.produto2 = Produto.objects.create(
            nome="Arranhador para Gatos", emoji="🐱",
            descricao="Torre com 3 andares.",
            preco=decimal.Decimal("200.00"), estoque=10
        )
        self.produto_sem_estoque = Produto.objects.create(
            nome="Bolinha Velha", emoji="🎾",
            descricao="Já foi mordida.",
            preco=decimal.Decimal("5.00"), estoque=0 # Sem estoque
        )

    def test_cenario_1_adicionar_ao_carrinho(self):
        print("\nIniciando Teste: História 8, Cenário 1 - Adicionar produtos ao carrinho")
        driver = self.driver
        
        # Acessa a loja
        driver.get(f'{self.live_server_url}/shop/')
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), "Pet Shop"))
        print("Página da loja acessada.")
        time.sleep(1)

        # Encontra a Ração e clica em "Adicionar"
        print("Adicionando Ração ao carrinho...")
        item_racao = self.wait.until(EC.presence_of_element_located((By.XPATH, f"//div[contains(@class, 'shop-item') and contains(., 'Ração Super Premium')]")))
        self.wait.until(EC.element_to_be_clickable(item_racao.find_element(By.LINK_TEXT, "Adicionar ao carrinho"))).click()
        
        # Verifica a mensagem de sucesso
        print("Verificando mensagem de sucesso...")
        mensagem_sucesso = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.success')))
        self.assertIn("Ração Super Premium' foi adicionado", mensagem_sucesso.text)
        time.sleep(2)

        # Adiciona o Arranhador
        print("Adicionando Arranhador ao carrinho...")
        item_arranhador = self.wait.until(EC.presence_of_element_located((By.XPATH, f"//div[contains(@class, 'shop-item') and contains(., 'Arranhador para Gatos')]")))
        self.wait.until(EC.element_to_be_clickable(item_arranhador.find_element(By.LINK_TEXT, "Adicionar ao carrinho"))).click()

        # Verifica a mensagem de sucesso
        print("Verificando mensagem de sucesso...")
        mensagem_sucesso_2 = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.success')))
        self.assertIn("Arranhador para Gatos' foi adicionado", mensagem_sucesso_2.text)
        time.sleep(2)
        
        # Vai para o carrinho
        print("Acessando o carrinho...")
        driver.get(f'{self.live_server_url}/cart/')
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), "Meu Carrinho"))
        
        # Verifica se os dois itens estão lá
        body_text = driver.find_element(By.TAG_NAME, 'body').text
        self.assertIn("Ração Super Premium", body_text)
        self.assertIn("Arranhador para Gatos", body_text)
        self.assertIn("Total: R$ 350.00", body_text) # 150 + 200
        print("Teste Cenário 1 concluído.")
        time.sleep(3)

    def test_cenario_2_finalizar_compra(self):
        print("\nIniciando Teste: História 8, Cenário 2 - Finalizar compra")
        driver = self.driver
        
        # Adiciona um item ao carrinho primeiro (usando a URL direta para ser mais rápido)
        driver.get(f'{self.live_server_url}/cart/add/{self.produto1.pk}/')
        
        # Vai para o carrinho
        print("Acessando o carrinho...")
        driver.get(f'{self.live_server_url}/cart/')
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), "Meu Carrinho"))
        self.assertIn("Ração Super Premium", driver.find_element(By.TAG_NAME, 'body').text)
        time.sleep(1)

        # Clica em "Finalizar Compra"
        print("Clicando em Finalizar Compra...")
        self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Finalizar Compra"))).click()

        # Verifica se foi para a página de sucesso
        print("Verificando página de sucesso...")
        self.wait.until(EC.url_contains('/purchase-success/'))
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), "Compra realizada com sucesso!"))
        self.assertIn("Compra realizada com sucesso!", driver.find_element(By.TAG_NAME, 'body').text)
        print("Teste Cenário 2 concluído.")
        time.sleep(3)
        
    def test_cenario_3_finalizar_compra_carrinho_vazio(self):
        print("\nIniciando Teste: História 8, Cenário 3 - Carrinho vazio")
        driver = self.driver

        # Tenta finalizar a compra (indo direto para a view de checkout)
        print("Tentando acessar a URL de checkout com carrinho vazio...")
        driver.get(f'{self.live_server_url}/checkout/')

        # Verifica se foi redirecionado para a loja e se a mensagem de erro apareceu
        print("Verificando redirecionamento para a loja e mensagem de erro...")
        self.wait.until(EC.url_contains('/shop/')) # Deve ser redirecionado para a loja
        mensagem_erro = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.error')))
        self.assertIn("Seu carrinho está vazio", mensagem_erro.text)
        print("Teste Cenário 3 concluído.")
        time.sleep(3)

    def test_cenario_4_produto_indisponivel(self):
        print("\nIniciando Teste: História 8, Cenário 4 - Produto indisponível")
        driver = self.driver
        
        # Acessa a loja
        driver.get(f'{self.live_server_url}/shop/')
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), "Pet Shop"))
        print("Página da loja acessada.")

        # Tenta adicionar o produto sem estoque (indo pela URL direta)
        print("Tentando adicionar produto sem estoque...")
        driver.get(f'{self.live_server_url}/cart/add/{self.produto_sem_estoque.pk}/')

        # Verifica se continua na loja e se a mensagem de erro apareceu
        print("Verificando mensagem de erro...")
        self.wait.until(EC.url_contains('/shop/')) 
        mensagem_erro = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.error')))
        self.assertIn("Produto indisponível", mensagem_erro.text)
        print("Teste Cenário 4 concluído.")
        time.sleep(3)