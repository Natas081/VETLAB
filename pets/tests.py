# tests.py (substitua inteiramente pelo conteúdo abaixo)

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
from selenium.common.exceptions import TimeoutException

# Modelos
from pets.models import Pet, Evento, Meta, ItemCompra


class BaseE2ETestCase(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = Options()
        # Se estiver em CI (GitHub Actions) roda headless
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
        cls.wait = WebDriverWait(cls.driver, 15)

    @classmethod
    def tearDownClass(cls):
        print("\nTestes concluídos. Fechando o navegador.")
        # Dá uma pausa local pra você ver o resultado final (não em CI)
        if not (os.environ.get('CI') == 'true' or os.environ.get('GITHUB_ACTIONS') == 'true'):
            time.sleep(3)
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.username = f'testuser_{int(time.time())}'
        self.password = 'testpass123'
        # Cria usuário no banco de testes
        self.user = User.objects.create_user(username=self.username, password=self.password)

        # Navega para login e autentica via UI (para simular fluxo real)
        self.driver.get(f'{self.live_server_url}/pets/login/')
        self.wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(self.username)
        self.driver.find_element(By.NAME, "password").send_keys(self.password)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Aguarda a lista de pets aparecer para confirmar login
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), "LISTA DE PETS"))
        print(f"\nUsuário '{self.username}' logado para o teste.")
        time.sleep(0.4)

    # --- Helpers ---
    def set_date_by_js(self, element, yyyy_mm_dd):
        """
        Define value do input type=date via JS para evitar problemas de locale/keyboard.
        element: WebElement (ou localizador encontrado)
        yyyy_mm_dd: string 'YYYY-MM-DD'
        """
        # assegura que o elemento está visível/presente
        self.driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input')); arguments[0].dispatchEvent(new Event('change'));", element, yyyy_mm_dd)

    def debug_and_reraise(self, exc):
        """
        Imprime diagnóstico útil (URL e H1 atual) e re-raise a exceção.
        """
        try:
            current_url = self.driver.current_url
        except Exception:
            current_url = "<não foi possível obter URL>"

        try:
            h1 = self.driver.find_element(By.TAG_NAME, "h1").text
        except Exception:
            h1 = "<sem H1 na página>"

        print("\n--- DEBUG (TimeoutException) ---")
        print(f"URL atual: {current_url}")
        print(f"H1 atual: {h1}")
        raise exc


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

        # Usa JS para setar a data corretamente
        data_input = driver.find_element(By.ID, "id_data_nascimento")
        self.set_date_by_js(data_input, "2021-08-01")

        driver.find_element(By.ID, "id_peso").send_keys("5.1")
        time.sleep(0.3)

        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()

        try:
            self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), "LISTA DE PETS"))
            mensagem_sucesso = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.success')))
            self.assertIn("adicionado", mensagem_sucesso.text)
            self.assertIn("Bolinha", driver.find_element(By.CLASS_NAME, 'pet-list').text)
            print("Teste H1 C1 concluído.")
            time.sleep(0.6)
        except TimeoutException as e:
            self.debug_and_reraise(e)

    def test_cenario_2_cadastro_campos_obrigatorios_em_branco(self):
        print("Iniciando: H1 C2 - Campos obrigatórios em branco")
        driver = self.driver

        self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Adicionar Novo Pet"))).click()
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), "CADASTRO DO PET"))

        # Submete sem preencher campos
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()

        try:
            mensagem_erro = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.error')))
            self.assertIn("obrigatórios", mensagem_erro.text)
            print("Teste H1 C2 concluído.")
            time.sleep(0.4)
        except TimeoutException as e:
            self.debug_and_reraise(e)


# ===============================================
# HISTÓRIA 2: GERENCIAR PETS
# ===============================================
class TesteHistoria2GerenciarPets(BaseE2ETestCase):

    def setUp(self):
        super().setUp()
        # Cria pet direto no DB para edição/exclusão
        self.pet = Pet.objects.create(
            tutor=self.user, nome="PetGerencia", especie="Coelho",
            data_nascimento=date(2023, 5, 1), peso=1.8
        )
        print(f"Pet '{self.pet.nome}' criado no banco.")

    def test_cenario_3_edicao_bem_sucedida(self):
        print("Iniciando: H2 C3 - Edição bem-sucedida")
        driver = self.driver

        driver.get(f'{self.live_server_url}/pets/')
        # Localiza o container do pet
        pet_item = self.wait.until(EC.presence_of_element_located((By.XPATH, f"//span[text()='{self.pet.nome}']/ancestor::div[contains(@class,'pet-item')]")))
        # Clica no link Editar dentro do item
        edit_link = pet_item.find_element(By.LINK_TEXT, "Editar")
        self.wait.until(EC.element_to_be_clickable(edit_link)).click()

        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), "EDITAR DADOS DO PET"))

        campo_nome = self.wait.until(EC.presence_of_element_located((By.ID, "id_nome")))
        campo_nome.clear()
        campo_nome.send_keys("PetEditado")
        time.sleep(0.4)
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()

        try:
            self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), "LISTA DE PETS"))
            mensagem_sucesso = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.success')))
            self.assertIn("atualizados", mensagem_sucesso.text)
            self.assertIn("PetEditado", driver.find_element(By.CLASS_NAME, 'pet-list').text)
            print("Teste H2 C3 concluído.")
            time.sleep(0.6)
        except TimeoutException as e:
            self.debug_and_reraise(e)

    def test_cenario_5_exclusao_bem_sucedida(self):
        print("Iniciando: H2 C5 - Exclusão bem-sucedida")
        driver = self.driver

        driver.get(f'{self.live_server_url}/pets/')
        pet_item = self.wait.until(EC.presence_of_element_located((By.XPATH, f"//span[text()='{self.pet.nome}']/ancestor::div[contains(@class,'pet-item')]")))
        delete_link = pet_item.find_element(By.LINK_TEXT, "Excluir")
        self.wait.until(EC.element_to_be_clickable(delete_link)).click()

        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), "TEM CERTEZA?"))
        # clica no botão confirmar
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.delete-btn.primary"))).click()

        try:
            self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), "LISTA DE PETS"))
            mensagem_sucesso = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.success')))
            self.assertIn("removido", mensagem_sucesso.text)
            # garante que o pet não está mais no body
            self.assertNotIn(self.pet.nome, driver.find_element(By.TAG_NAME, 'body').text)
            print("Teste H2 C5 concluído.")
            time.sleep(0.6)
        except TimeoutException as e:
            self.debug_and_reraise(e)


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
        pet_item = self.wait.until(EC.presence_of_element_located((By.XPATH, f"//span[text()='{self.pet.nome}']/ancestor::div[contains(@class,'pet-item')]")))
        eventos_link = pet_item.find_element(By.LINK_TEXT, "Eventos")
        self.wait.until(EC.element_to_be_clickable(eventos_link)).click()

        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), f"Eventos de {self.pet.nome}"))

        self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Adicionar Novo Evento"))).click()
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), "ADICIONAR EVENTO"))

        # seleciona tipo
        Select(self.wait.until(EC.presence_of_element_located((By.NAME, "tipo")))).select_by_value("consulta")
        # seta data via JS (formato YYYY-MM-DD)
        data_input = driver.find_element(By.NAME, "data")
        self.set_date_by_js(data_input, "2025-11-20")

        driver.find_element(By.NAME, "observacoes").send_keys("Checkup anual")
        time.sleep(0.4)
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()

        try:
            self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), f"Eventos de {self.pet.nome}"))
            mensagem_sucesso = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.success')))
            self.assertIn("Evento adicionado", mensagem_sucesso.text)
            # verifica se observação aparece
            self.assertIn("Checkup anual", driver.find_element(By.CLASS_NAME, 'pet-list').text)
            print("Teste H3 C1 concluído.")
            time.sleep(0.6)
        except TimeoutException as e:
            self.debug_and_reraise(e)


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

        # acha o evento com a descrição
        evento_item = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'pet-item') and contains(., 'Remédio X')]")))
        concluir_link = evento_item.find_element(By.LINK_TEXT, "Concluir")
        self.wait.until(EC.element_to_be_clickable(concluir_link)).click()

        try:
            self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), f"Eventos de {self.pet.nome}"))
            mensagem_sucesso = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.success')))
            self.assertIn("concluído", mensagem_sucesso.text)

            # evento deve agora ter a classe 'concluido' no DOM
            evento_item_atualizado = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'pet-item') and contains(@class, 'concluido')]")))
            self.assertIn("Concluído", evento_item_atualizado.text)
            print("Teste H4 C1 concluído.")
            time.sleep(0.6)
        except TimeoutException as e:
            self.debug_and_reraise(e)


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
        # Aguarda H1 que o template mostra (pode variar entre "Quadro de Metas..." ou "Metas para ...")
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, 'h1')))

        # Preenche e seta a data via JS
        driver.find_element(By.NAME, "descricao").send_keys("Manter a caixa de areia limpa")
        data_input = driver.find_element(By.NAME, "data_prazo")
        self.set_date_by_js(data_input, "2026-03-01")
        time.sleep(0.3)

        # botão de submit dentro do form.meta-form
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "form.meta-form button[type='submit']"))).click()

        try:
            # Aguarda voltar para a mesma página e mensagem
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, 'h1')))
            mensagem_sucesso = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.success')))
            self.assertIn("Meta adicionada", mensagem_sucesso.text)
            self.assertIn("Manter a caixa de areia limpa", driver.find_element(By.CLASS_NAME, 'pet-list').text)
            print("Teste H5 C1 concluído.")
            time.sleep(0.6)
        except TimeoutException as e:
            self.debug_and_reraise(e)


# ===============================================
# HISTÓRIA (LISTA DE COMPRAS)
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
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), f"Lista de Compras"))

        driver.find_element(By.NAME, "descricao").send_keys("Ração Nova 10kg")
        time.sleep(0.3)
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "form.meta-form button[type='submit']"))).click()

        try:
            self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), f"Lista de Compras"))
            mensagem_sucesso = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.success')))
            self.assertIn("adicionado", mensagem_sucesso.text)
            # valida se o item aparece na seção A Comprar
            textos_a_comprar = driver.find_element(By.XPATH, "//h2[text()='A Comprar']/following-sibling::div").text
            self.assertIn("Ração Nova 10kg", textos_a_comprar)
            print("Teste H8 C1 concluído.")
            time.sleep(0.6)
        except TimeoutException as e:
            self.debug_and_reraise(e)

    def test_cenario_2_marcar_item_como_comprado(self):
        print("Iniciando: H8 C2 - Marcar item como comprado")
        driver = self.driver
        item = ItemCompra.objects.create(pet=self.pet, descricao="Item para comprar")

        driver.get(f'{self.live_server_url}/pets/{self.pet.pk}/compras/')
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), f"Lista de Compras"))

        item_div = self.wait.until(EC.presence_of_element_located((By.XPATH, f"//span[contains(text(), '{item.descricao}')]/ancestor::div[contains(@class,'pet-item')]")))
        marcar_link = item_div.find_element(By.LINK_TEXT, "Marcar Comprado")
        self.wait.until(EC.element_to_be_clickable(marcar_link)).click()

        try:
            self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), f"Lista de Compras"))
            mensagem_sucesso = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.success')))
            self.assertIn("comprado", mensagem_sucesso.text)
            # verifica se foi movido para "Comprados"
            lista_comprados = driver.find_element(By.XPATH, "//h2[text()='Comprados']/following-sibling::div").text
            self.assertIn(item.descricao, lista_comprados)
            print("Teste H8 C2 concluído.")
            time.sleep(0.6)
        except TimeoutException as e:
            self.debug_and_reraise(e)
