import os
import time
from datetime import date
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# IMPORTA OS MODELOS ATUAIS (SEM PRODUTO, COM ITEMCOMPRA)
from pets.models import Pet, Evento, Meta, ItemCompra 

# ===============================================
# CLASSE BASE - CONFIGURAÇÃO E LOGIN
# (Baseado no seu exemplo funcional)
# ===============================================
class BaseE2ETestCase(StaticLiveServerTestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = Options()
        # Detecção de CI (GitHub Actions)
        if os.environ.get('CI') == 'true' or os.environ.get('GITHUB_ACTIONS') == 'true':
            print("Rodando em modo CI (Headless)...")
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
        else:
            print("Rodando localmente (com navegador visível)...")
            options.add_argument("--start-maximized")
        
        cls.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        cls.wait = WebDriverWait(cls.driver, 15) # Espera explícita

    @classmethod
    def tearDownClass(cls):
        print("\nTestes concluídos. Fechando o navegador.")
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
        self.wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(self.username)
        self.driver.find_element(By.NAME, "password").send_keys(self.password)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # <<< CORREÇÃO CRÍTICA >>>
        # Espera o H1 "LISTA DE PETS" carregar para confirmar o login
        self.wait.until(EC.text_to_be_present_in_element(
            (By.TAG_NAME, 'h1'), "LISTA DE PETS"
        ))
        print(f"\nUsuário '{self.username}' logado para o teste.")
        time.sleep(0.5) # Pequena pausa para estabilizar

# ===============================================
# HISTÓRIA 1: CADASTRO DO PET
# ===============================================
class TesteHistoria1CadastroPet(BaseE2ETestCase):

    def test_cenario_1_cadastro_bem_sucedido(self):
        print("Iniciando: H1 C1 - Cadastro bem-sucedido")
        driver = self.driver
        
        self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Adicionar Novo Pet"))).click()
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), "CADASTRO DO PET"))
        
        driver.find_element(By.ID, "id_nome").send_keys("Bolinha")
        driver.find_element(By.ID, "id_especie").send_keys("Gato")
        driver.find_element(By.ID, "id_data_nascimento").send_keys("2021-08-01")
        driver.find_element(By.ID, "id_peso").send_keys("5.1")
        time.sleep(0.5)
        
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
        
        # <<< CORREÇÃO DO ERRO 500 >>>
        # 1. Espera o redirect de volta para a lista
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), "LISTA DE PETS"))
        # 2. Espera a MENSAGEM DE SUCESSO aparecer
        mensagem_sucesso = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.success')))
        self.assertIn("Pet 'Bolinha' adicionado", mensagem_sucesso.text)
        # 3. Verifica se o pet está na lista
        self.assertIn("Bolinha", driver.find_element(By.CLASS_NAME, 'pet-list').text)
        print("Teste H1 C1 concluído.")

    def test_cenario_2_cadastro_campos_obrigatorios_em_branco(self):
        print("Iniciando: H1 C2 - Campos obrigatórios em branco")
        driver = self.driver
        
        self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Adicionar Novo Pet"))).click()
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), "CADASTRO DO PET"))

        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
        
        # <<< CORREÇÃO DO ERRO 500 >>>
        # Espera a MENSAGEM DE ERRO aparecer
        mensagem_erro = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.error')))
        self.assertIn("obrigatórios", mensagem_erro.text)
        print("Teste H1 C2 concluído.")

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
        print(f"Pet '{self.pet.nome}' criado no banco.")

    def test_cenario_3_edicao_bem_sucedida(self):
        print("Iniciando: H2 C3 - Edição bem-sucedida")
        driver = self.driver
        
        driver.get(f'{self.live_server_url}/pets/')
        # Encontra o pet na lista
        pet_item = self.wait.until(EC.presence_of_element_located((By.XPATH, f"//span[text()='{self.pet.nome}']/ancestor::div[@class='pet-item']")))
        
        self.wait.until(EC.element_to_be_clickable(pet_item.find_element(By.LINK_TEXT, "Editar"))).click()
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), "EDITAR DADOS DO PET"))
        
        campo_nome = self.wait.until(EC.presence_of_element_located((By.ID, "id_nome")))
        campo_nome.clear()
        campo_nome.send_keys("PetEditado")
        time.sleep(0.5)
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
        
        # <<< CORREÇÃO DO ERRO 500 >>>
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), "LISTA DE PETS"))
        mensagem_sucesso = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.success')))
        self.assertIn("atualizados com sucesso", mensagem_sucesso.text)
        self.assertIn("PetEditado", driver.find_element(By.CLASS_NAME, 'pet-list').text)
        print("Teste H2 C3 concluído.")

    def test_cenario_5_exclusao_bem_sucedida(self):
        print("Iniciando: H2 C5 - Exclusão bem-sucedida")
        driver = self.driver

        driver.get(f'{self.live_server_url}/pets/')
        pet_item = self.wait.until(EC.presence_of_element_located((By.XPATH, f"//span[text()='{self.pet.nome}']/ancestor::div[@class='pet-item']")))
        
        self.wait.until(EC.element_to_be_clickable(pet_item.find_element(By.LINK_TEXT, "Excluir"))).click()
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), "TEM CERTEZA?"))
        
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.delete-btn.primary"))).click()

        # <<< CORREÇÃO DO ERRO 500 >>>
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), "LISTA DE PETS"))
        mensagem_sucesso = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.success')))
        self.assertIn("removido com sucesso", mensagem_sucesso.text)
        self.assertNotIn(self.pet.nome, driver.find_element(By.TAG_NAME, 'body').text)
        print("Teste H2 C5 concluído.")

# ===============================================
# HISTÓRIA 3: CADASTRO DE EVENTOS
# ===============================================
class TesteHistoria3CadastroEvento(BaseE2ETestCase):

    def setUp(self):
        super().setUp()
        self.pet = Pet.objects.create(tutor=self.user, nome="PetEventos", especie="Papagaio", data_nascimento=date(2024, 1, 1), peso=0.8)
        print(f"Pet '{self.pet.nome}' criado no banco.")

    def test_cenario_1_evento_adicionado_com_sucesso(self):
        print("Iniciando: H3 C1 - Evento adicionado com sucesso")
        driver = self.driver

        driver.get(f'{self.live_server_url}/pets/')
        pet_item = self.wait.until(EC.presence_of_element_located((By.XPATH, f"//span[text()='{self.pet.nome}']/ancestor::div[@class='pet-item']")))
        
        self.wait.until(EC.element_to_be_clickable(pet_item.find_element(By.LINK_TEXT, "Eventos"))).click()
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), f"Eventos de {self.pet.nome}"))
        
        self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Adicionar Novo Evento"))).click()
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), "ADICIONAR EVENTO"))
        
        Select(self.wait.until(EC.presence_of_element_located((By.NAME, "tipo")))).select_by_value("consulta") 
        driver.find_element(By.NAME, "data").send_keys("2025-11-20")
        driver.find_element(By.NAME, "observacoes").send_keys("Checkup anual")
        time.sleep(0.5)

        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()

        # <<< CORREÇÃO DO ERRO 500 >>>
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), f"Eventos de {self.pet.nome}"))
        mensagem_sucesso = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.success')))
        self.assertIn("Evento adicionado!", mensagem_sucesso.text)
        self.assertIn("Checkup anual", driver.find_element(By.CLASS_NAME, 'pet-list').text)
        print("Teste H3 C1 concluído.")

# ===============================================
# HISTÓRIA 4: CONCLUSÃO DE EVENTOS
# ===============================================
class TesteHistoria4ConclusaoEvento(BaseE2ETestCase):

    def setUp(self):
        super().setUp()
        self.pet = Pet.objects.create(tutor=self.user, nome="PetConcluir", especie="Cachorro", data_nascimento=date(2022, 1, 1), peso=10)
        self.evento = Evento.objects.create(pet=self.pet, tipo="medicamento", data=date(2025,10,10), observacoes="Remédio X")
        print(f"Pet e Evento criados no banco.")

    def test_cenario_1_evento_concluido_com_sucesso(self):
        print("Iniciando: H4 C1 - Evento concluído com sucesso")
        driver = self.driver

        driver.get(f'{self.live_server_url}/pets/{self.pet.pk}/eventos/')
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), f"Eventos de {self.pet.nome}"))

        evento_item = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'pet-item') and contains(., 'Remédio X')]")))
        
        self.wait.until(EC.element_to_be_clickable(evento_item.find_element(By.LINK_TEXT, "Concluir"))).click()
        
        # <<< CORREÇÃO DO ERRO 500 >>>
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), f"Eventos de {self.pet.nome}"))
        mensagem_sucesso = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.success')))
        self.assertIn("Evento marcado como concluído!", mensagem_sucesso.text)
        
        # Verifica se o item agora tem o texto (Concluído)
        evento_item_atualizado = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'pet-item') and contains(@class, 'concluido')]")))
        self.assertIn("(Concluído)", evento_item_atualizado.text)
        print("Teste H4 C1 concluído.")

# ===============================================
# HISTÓRIA 5: CADASTRO DE METAS
# ===============================================
class TesteHistoria5CadastroMeta(BaseE2ETestCase):

    def setUp(self):
        super().setUp()
        self.pet = Pet.objects.create(tutor=self.user, nome="PetMetas", especie="Gato", data_nascimento=date(2020, 2, 14), peso=6)
        print(f"Pet '{self.pet.nome}' criado no banco.")

    def test_cenario_1_meta_adicionada_com_sucesso(self):
        print("Iniciando: H5 C1 - Meta adicionada com sucesso")
        driver = self.driver

        driver.get(f'{self.live_server_url}/pets/{self.pet.pk}/metas/')
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), f"Metas de {self.pet.nome}"))
        
        driver.find_element(By.NAME, "descricao").send_keys("Manter a caixa de areia limpa")
        driver.find_element(By.NAME, "data_prazo").send_keys("2026-03-01")
        time.sleep(0.5)

        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "form.meta-form button[type='submit']"))).click()
        
        # <<< CORREÇÃO DO ERRO 500 >>>
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), f"Metas de {self.pet.nome}"))
        mensagem_sucesso = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.success')))
        self.assertIn("Meta adicionada!", mensagem_sucesso.text)
        self.assertIn("Manter a caixa de areia limpa", driver.find_element(By.CLASS_NAME, 'pet-list').text)
        print("Teste H5 C1 concluído.")

# ===============================================
# HISTÓRIA (LISTA DE COMPRAS)
# (Substituindo o antigo Pet Shop)
# ===============================================
class TesteHistoria8ListaDeCompras(BaseE2ETestCase):
    
    def setUp(self):
        super().setUp()
        self.pet = Pet.objects.create(tutor=self.user, nome="PetCompras", especie="Cachorro", data_nascimento=date(2022, 1, 1), peso=12)
        print(f"Pet '{self.pet.nome}' criado no banco.")

    def test_cenario_1_adicionar_item_lista(self):
        print("Iniciando: H8 C1 - Adicionar item à lista de compras")
        driver = self.driver
        
        driver.get(f'{self.live_server_url}/pets/{self.pet.pk}/compras/')
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), f"Lista de Compras de {self.pet.nome}"))

        driver.find_element(By.NAME, "descricao").send_keys("Ração Nova 10kg")
        time.sleep(0.5)
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "form.meta-form button[type='submit']"))).click()

        # <<< CORREÇÃO DO ERRO 500 >>>
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), f"Lista de Compras de {self.pet.nome}"))
        mensagem_sucesso = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.success')))
        self.assertIn("Item adicionado à lista", mensagem_sucesso.text)
        self.assertIn("Ração Nova 10kg", driver.find_element(By.XPATH, "//h2[text()='A Comprar']/following-sibling::div").text)
        print("Teste H8 C1 concluído.")

    def test_cenario_2_marcar_item_como_comprado(self):
        print("Iniciando: H8 C2 - Marcar item como comprado")
        driver = self.driver
        item = ItemCompra.objects.create(pet=self.pet, descricao="Item para comprar")
        
        driver.get(f'{self.live_server_url}/pets/{self.pet.pk}/compras/')
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), f"Lista de Compras de {self.pet.nome}"))

        item_div = self.wait.until(EC.presence_of_element_located((By.XPATH, f"//span[contains(text(), '{item.descricao}')]/ancestor::div[contains(@class, 'pet-item')]")))
        self.wait.until(EC.element_to_be_clickable(item_div.find_element(By.LINK_TEXT, "Marcar Comprado"))).click()
        
        # <<< CORREÇÃO DO ERRO 500 >>>
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), f"Lista de Compras de {self.pet.nome}"))
        mensagem_sucesso = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.success')))
        self.assertIn("marcado como comprado", mensagem_sucesso.text)
        
        # Verifica se o item mudou para a lista de "Comprados"
        lista_comprados = driver.find_element(By.XPATH, "//h2[text()='Comprados']/following-sibling::div").text
        self.assertIn(item.descricao, lista_comprados)
        print("Teste H8 C2 concluído.")