# Como Contribuir com o VETLAB 🐾

Primeiramente, obrigado pelo seu interesse em contribuir\! O VETLAB é um projeto Django focado em gerenciamento de pets, e estamos felizes em ter sua ajuda.

Este guia não é apenas sobre como rodar o projeto, mas também sobre **como não quebrar as coisas que já funcionam**. Nós passamos por muitos bugs para chegar até aqui, e este guia contém o conhecimento adquirido.

## 1\. Configuração Essencial do Ambiente

Siga estes passos para ter o projeto rodando localmente.

### Passo 1: Fork, Clone e Ambiente Virtual

1.  **Faça um Fork** do repositório principal e **Clone** o seu fork:

    ```bash
    git clone https://github.com/SEU-USUARIO/VETLAB.git
    cd VETLAB
    ```

2.  **Crie e Ative seu Ambiente Virtual:**

    ```bash
    # Criar o .venv
    python -m venv .venv

    # Ativar no Windows (PowerShell)
    .\.venv\Scripts\Activate

    # Ativar no macOS/Linux
    source .venv/bin/activate
    ```

    *(Seu terminal deve agora mostrar `(.venv)` no início.)*

### Passo 2: Instalação e Banco de Dados

1.  **Instale as Dependências:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure o Banco de Dados (Automático):**
    O `settings.py` é inteligente. Ele usará o `db.sqlite3` (local) automaticamente se não encontrar a variável de ambiente `DATABASE_URL`.

    Para criar seu arquivo `db.sqlite3` local, rode:

    ```bash
    python manage.py migrate
    ```

### Passo 3: Rodar o Servidor

1.  **(Opcional) Crie um Superusuário** para acessar o Admin (`/admin/`):

    ```bash
    python manage.py createsuperuser
    ```

2.  **Rode o Servidor:**

    ```bash
    python manage.py runserver
    ```

    Abra `http://127.0.0.1:8000/` no seu navegador. Você deverá ver a página inicial.

## 2\. Princípios de Código e Armadilhas Comuns (LEIA ISSO)

Nós quebramos o site várias vezes antes de descobrir isso. Economize seu tempo e leia abaixo.

### 🐞 Armadilha 1: O Erro 500 ao Salvar (Campos Opcionais)

Este foi o bug mais difícil. Se você adicionar um campo opcional no `models.py`, ele **DEVE** ser tratado na `view`.

  * **Modelo (`models.py`):**

    ```python
    # 'raca' pode ser nula no banco de dados
    raca = models.CharField(max_length=50, blank=True, null=True)
    ```

  * **View (`views.py`):**
    O formulário HTML enviará `raca=''` (uma string vazia) se o campo for deixado em branco. Salvar `''` em um campo `null=True` causa um **Erro 500 (IntegrityError)**.

  * **A CORREÇÃO:** Sempre converta strings vazias em `None` antes de salvar.

    ```python

    raca_do_form = request.POST.get('raca')

    pet.raca = raca_do_form or None # Converte '' para None
    pet.save()

    # Ou no create:
    Pet.objects.create(..., raca = raca_do_form or None, ...)
    ```

### 🐞 Armadilha 2: O Bug do `Decimal` vs `Float`

O campo `peso` é um `DecimalField` para precisão. O Python usa `float` por padrão. Eles não são compatíveis.

  * **A CORREÇÃO:** Sempre importe `Decimal` e converta os dados do formulário antes de salvar.
    ```python
    # DENTRO DA VIEW (ex: pet_create)
    from decimal import Decimal, InvalidOperation

    peso_do_form = request.POST.get('peso')

    try:
        peso_decimal = Decimal(peso_do_form) # NUNCA use float(peso_do_form)
    except InvalidOperation:
        # Trate o erro...

    Pet.objects.create(..., peso=peso_decimal)
    ```

### 🐞 Armadilha 3: O Bug do `VariableDoesNotExist`

Muitos formulários (como `pet_form.html` e `evento_adicionar.html`) são usados para **Criar (Create)** e **Editar (Edit)**.

O template de Edição espera uma variável (ex: `evento.data`). Se a view de Criação (ex: `evento_adicionar`) não enviar essa variável, o template quebra.

  * **A CORREÇÃO:** A view de **Criação** (GET) deve **SEMPRE** enviar as mesmas variáveis que a view de Edição, mas com o valor `None`.

    ```python
    # DENTRO DA VIEW (ex: evento_adicionar)
    def evento_adicionar(request, pet_pk):
        # ...
        context = {
            'pet': pet,
            'tipos_evento': Evento.TIPOS_EVENTO,
            'values': {},
            'evento': None  # <-- ESSA LINHA É OBRIGATÓRIA
        }
        return render(request, 'pets/evento_adicionar.html', context)
    ```

## 3\. Rodando os Testes (Obrigatório\!)

Nós usamos Selenium para testes de ponta-a-ponta (E2E). **Nenhum Pull Request será aceito se os testes falharem.**

### Como Rodar

Com seu `.venv` ativado:

```bash
# Para rodar TODOS os testes do projeto
python manage.py test

# Para rodar APENAS os testes de Cadastro de Pet (mais rápido)
python manage.py test pets.tests.TesteHistoria1CadastroPet
```

### Decifrando Erros de Teste

Você **VAI** ver erros. 99% das vezes, o problema é no seu código Django, não no teste.

  * **Se o teste der `TimeoutException` (Exceção de Tempo Esgotado):**
    Isso quase sempre significa que o robô clicou em "Salvar" e o servidor retornou um **Erro 500** (veja as Armadilhas 1 e 2). O robô ficou esperando a página de "Parabéns" (que nunca chegou) e desistiu.

      * **Como confirmar:** Olhe o log de debug. Se ele disser `O H1 atual na página é: 'Server Error (500)'`, o bug está na sua `view`.

  * **Se o teste der `WebDriverException: ... unhandled inspector error`:**
    Isso é um *race condition*. O robô está tentando ler um elemento (ex: o `<h1>`) no exato momento em que o Django está recarregando a página.

      * **A CORREÇÃO:** Altere o teste para esperar por um elemento que só existe *depois* do recarregamento (ex: a mensagem de sucesso).
      * *Errado:* `self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), "Lista de Metas"))`
      * *Correto:* `self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.messages .message.success')))`

  * **Se o teste der `AssertionError: '2.5 kg' != '2.50 kg'`:**
    Isso é um bug de lógica no teste. Nossos `DecimalFields` têm 2 casas decimais, então o template renderiza "2.50". O teste deve esperar "2.50 kg", não "2.5 kg".

## 4\. Processo de Pull Request (PR)

1.  **Crie uma Branch:** `git checkout -b minha-feature`
2.  **Faça suas Mágicas:** (Lembre-se das Armadilhas\!)
3.  **Rode os Testes:** `python manage.py test`
4.  **Faça o Commit e Push:**
    ```bash
    git add .
    git commit -m "Minha feature incrível que não quebra o site"
    git push origin minha-feature
    ```
5.  **Abra o Pull Request** no GitHub.

Obrigado por ajudar a tornar o VETLAB melhor\!