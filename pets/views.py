# ==============================================================================
# IMPORTS NECESSÁRIOS
# ==============================================================================
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Pet, Evento, Meta, Produto # Garanta que Produto está importado

# Imports para o sistema de Login
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required


# ==============================================================================
# VIEWS PÚBLICAS (NÃO PRECISAM DE LOGIN)
# ==============================================================================

def home_view(request):
    return render(request, 'pets/home.html')


# ==============================================================================
# VIEWS DE AUTENTICAÇÃO
# ==============================================================================

def register_view(request):
    if request.method == 'POST':
        nome_usuario = request.POST.get('username')
        senha1 = request.POST.get('password')
        senha2 = request.POST.get('password2')

        if senha1 != senha2:
            messages.error(request, 'As senhas não coincidem!')
            return redirect('register')

        if User.objects.filter(username=nome_usuario).exists():
            messages.error(request, 'Este nome de usuário já existe.')
            return redirect('register')

        novo_usuario = User.objects.create_user(username=nome_usuario, password=senha1)
        login(request, novo_usuario)
        messages.success(request, 'Cadastro realizado com sucesso! Você já está logado.')
        return redirect('pet_list')

    return render(request, 'pets/register.html')


def login_view(request):
    if request.method == 'POST':
        nome_usuario = request.POST.get('username')
        senha = request.POST.get('password')

        usuario = authenticate(request, username=nome_usuario, password=senha)

        if usuario is not None:
            login(request, usuario)
            return redirect('pet_list')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
            return redirect('login')

    return render(request, 'pets/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


# ==============================================================================
# VIEWS PROTEGIDAS (SÓ FUNCIONAM PARA USUÁRIOS LOGADOS)
# ==============================================================================

@login_required
def pet_list(request):
    pets = Pet.objects.filter(tutor=request.user)
    return render(request, 'pets/pet_list.html', {'pets': pets})


@login_required
def pet_create(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        especie = request.POST.get('especie')
        raca = request.POST.get('raca')
        data_nascimento = request.POST.get('data_nascimento')
        peso = request.POST.get('peso')

        context_values = {
            'nome': nome, 'especie': especie, 'raca': raca,
            'data_nascimento': data_nascimento, 'peso': peso
        }

        if not nome or not especie or not data_nascimento or not peso:
            messages.error(request, "Os campos Nome, Espécie, Data de Nascimento e Peso são obrigatórios.")
            return render(request, 'pets/pet_form.html', {'values': context_values})
        try:
            peso_float = float(peso)
            if peso_float <= 0:
                messages.error(request, "O peso deve ser um valor positivo.")
                return render(request, 'pets/pet_form.html', {'values': context_values})
        except (ValueError, TypeError):
            messages.error(request, "O valor do peso é inválido.")
            return render(request, 'pets/pet_form.html', {'values': context_values})

        Pet.objects.create(
            tutor=request.user, nome=nome, especie=especie, raca=raca,
            data_nascimento=data_nascimento, peso=peso_float
        )
        messages.success(request, f"Pet '{nome}' adicionado com sucesso!")
        return redirect('pet_list')
    
    # <<< CORREÇÃO DO ERRO 'VariableDoesNotExist' >>>
    # Passa um 'values' vazio no GET para o template não quebrar
    return render(request, 'pets/pet_form.html', {'values': {}})


@login_required
def pet_edit(request, pk):
    pet = get_object_or_404(Pet, pk=pk, tutor=request.user)
    if request.method == 'POST':
        nome = request.POST.get('nome')
        especie = request.POST.get('especie')
        raca = request.POST.get('raca')
        data_nascimento = request.POST.get('data_nascimento')
        peso = request.POST.get('peso')
        
        context_values = {
            'nome': nome, 'especie': especie, 'raca': raca,
            'data_nascimento': data_nascimento, 'peso': peso
        }

        if not nome or not especie or not data_nascimento or not peso:
            messages.error(request, "Todos os campos obrigatórios devem ser preenchidos.")
            return render(request, 'pets/pet_form.html', {'pet': pet, 'values': context_values})
        try:
            peso_float = float(peso)
            if peso_float <= 0:
                messages.error(request, "O peso deve ser um valor positivo.")
                return render(request, 'pets/pet_form.html', {'pet': pet, 'values': context_values})
        except (ValueError, TypeError):
            messages.error(request, "O valor do peso é inválido.")
            return render(request, 'pets/pet_form.html', {'pet': pet, 'values': context_values})

        pet.nome = nome
        pet.especie = especie
        pet.raca = raca
        pet.data_nascimento = data_nascimento
        pet.peso = peso_float
        pet.save()
        messages.success(request, f"Dados de '{pet.nome}' atualizados com sucesso!")
        return redirect('pet_list')
    
    # <<< CORREÇÃO DO ERRO 'VariableDoesNotExist' >>>
    # Passa 'values' vazio no GET e 'pet' para preencher os campos
    return render(request, 'pets/pet_form.html', {'pet': pet, 'values': {}})


@login_required
def pet_delete(request, pk):
    pet = get_object_or_404(Pet, pk=pk, tutor=request.user)
    if request.method == 'POST':
        nome_pet_deletado = pet.nome
        pet.delete()
        messages.success(request, f"Pet '{nome_pet_deletado}' removido com sucesso.")
        return redirect('pet_list')
    return render(request, 'pets/pet_confirm_delete.html', {'pet': pet})


@login_required
def pet_visao_geral(request, pk):
    pet = get_object_or_404(Pet, pk=pk, tutor=request.user)
    eventos = pet.eventos.all().order_by('-data')[:5]
    metas = pet.metas.all().order_by('progresso', 'data_prazo')
    total_eventos = pet.eventos.count()
    metas_concluidas = pet.metas.filter(progresso=100).count()
    
    context = {
        'pet': pet, 'eventos': eventos, 'metas': metas,
        'total_eventos': total_eventos, 'metas_concluidas': metas_concluidas,
    }
    if not eventos and not metas:
        messages.info(request, 'Esse pet ainda não possui registros de eventos ou metas.')
    return render(request, 'pets/pet_visao_geral.html', context)


# --- VIEWS DE EVENTOS ---

@login_required
def evento_selecionar_pet(request):
    pets = Pet.objects.filter(tutor=request.user)
    if not pets.exists():
        messages.info(request, "Não há pets cadastrados. Cadastre um pet antes de adicionar um evento.")
        return render(request, 'pets/evento_sem_pets.html')

    if request.method == 'POST':
        pet_pk = request.POST.get('pet_selecionado')
        if not pet_pk:
            messages.error(request, "Você precisa selecionar um pet.")
            return render(request, 'pets/evento_selecionar_pet.html', {'pets': pets})

        if Pet.objects.filter(pk=pet_pk, tutor=request.user).exists():
            return redirect('evento_adicionar', pet_pk=pet_pk)
        else:
            messages.error(request, "Pet inválido selecionado.")
            return render(request, 'pets/evento_selecionar_pet.html', {'pets': pets})

    return render(request, 'pets/evento_selecionar_pet.html', {'pets': pets})

@login_required
def evento_list(request, pet_pk):
    pet = get_object_or_404(Pet, pk=pet_pk, tutor=request.user)
    eventos = Evento.objects.filter(pet=pet).order_by('-data')
    return render(request, 'pets/evento_list.html', {'pet': pet, 'eventos': eventos})


@login_required
def evento_adicionar(request, pet_pk):
    pet = get_object_or_404(Pet, pk=pet_pk, tutor=request.user)
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        data = request.POST.get('data')

        if not tipo or not data:
            messages.error(request, "Os campos Tipo de Evento e Data são obrigatórios.")
            context = {'pet': pet, 'tipos_evento': Evento.TIPOS_EVENTO, 'values': request.POST}
            return render(request, 'pets/evento_adicionar.html', context)

        Evento.objects.create(
            pet=pet, tipo=tipo, data=data,
            observacoes=request.POST.get('observacoes')
        )
        messages.success(request, "Evento adicionado!")
        return redirect('evento_list', pet_pk=pet.pk)

    context = {'pet': pet, 'tipos_evento': Evento.TIPOS_EVENTO, 'values': {}}
    return render(request, 'pets/evento_adicionar.html', context)


@login_required
def evento_edit(request, pk):
    evento = get_object_or_404(Evento, pk=pk, pet__tutor=request.user)
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        data = request.POST.get('data')

        if not tipo or not data:
            messages.error(request, "Os campos Tipo de Evento e Data são obrigatórios.")
            context = {'pet': evento.pet, 'evento': evento, 'tipos_evento': Evento.TIPOS_EVENTO, 'values': request.POST}
            return render(request, 'pets/evento_adicionar.html', context)

        evento.tipo = tipo
        evento.data = data
        evento.observacoes = request.POST.get('observacoes')
        evento.save()
        messages.success(request, "Evento atualizado com sucesso!")
        return redirect('evento_list', pet_pk=evento.pet.pk)

    context = {'pet': evento.pet, 'evento': evento, 'tipos_evento': Evento.TIPOS_EVENTO, 'values': {}}
    return render(request, 'pets/evento_adicionar.html', context)


@login_required
def evento_delete(request, pk):
    evento = get_object_or_404(Evento, pk=pk, pet__tutor=request.user)
    pet = evento.pet
    if request.method == 'POST':
        evento.delete()
        messages.success(request, "Evento removido com sucesso.")
        return redirect('evento_list', pet_pk=pet.pk)
    return render(request, 'pets/evento_confirm_delete.html', {'evento': evento, 'pet': pet})


@login_required
def evento_concluir(request, pk):
    evento = get_object_or_404(Evento, pk=pk, pet__tutor=request.user)
    if hasattr(evento, 'concluido') and isinstance(evento.concluido, bool):
        if evento.concluido:
            messages.warning(request, 'Esse evento já foi concluído.')
        else:
            evento.concluido = True
            evento.save()
            messages.success(request, 'Evento marcado como concluído!')
    else:
        messages.error(request, 'Erro: Campo "concluido" não está configurado corretamente no modelo Evento.')

    return redirect('evento_list', pet_pk=evento.pet.pk)


# --- VIEWS DE METAS ---

@login_required
def meta_list(request, pet_pk):
    pet = get_object_or_404(Pet, pk=pet_pk, tutor=request.user)
    if request.method == 'POST':
        descricao = request.POST.get('descricao')
        data_prazo = request.POST.get('data_prazo')
        if not descricao or not data_prazo:
            messages.error(request, 'Preencha a descrição e a data para adicionar a meta.')
        else:
            Meta.objects.create(
                pet=pet, descricao=descricao, data_prazo=data_prazo
            )
            messages.success(request, 'Meta adicionada!')
        return redirect('meta_list', pet_pk=pet.pk)

    metas = Meta.objects.filter(pet=pet).order_by('progresso', 'data_prazo')
    context = {'pet': pet, 'metas': metas}
    return render(request, 'pets/meta_list.html', context)


@login_required
def meta_atualizar_progresso(request, pk):
    meta = get_object_or_404(Meta, pk=pk, pet__tutor=request.user)
    if request.method == 'POST':
        try:
            progresso = int(request.POST.get('progresso', 0))
            if 0 <= progresso <= 100:
                meta.progresso = progresso
                meta.save()
                messages.success(request, 'Progresso da meta atualizado!')
            else:
                messages.error(request, 'O progresso deve ser entre 0 e 100.')
        except (ValueError, TypeError):
            messages.error(request, 'Valor de progresso inválido.')
    return redirect('pet_visao_geral', pk=meta.pet.pk)


# ==============================================================================
# VIEWS DO PET SHOP (CORRIGIDAS PARA OS SEUS NOMES DE TEMPLATE)
# ==============================================================================

@login_required
def shop_list_view(request):
    """
    Mostra a lista de todos os produtos disponíveis na loja.
    """
    produtos = Produto.objects.filter(estoque__gt=0)
    context = {'produtos': produtos}
    # <<< CORRIGIDO: Usa o nome do seu template >>>
    return render(request, 'pets/petshop.html', context)


@login_required
def add_to_cart_view(request, produto_pk):
    """
    Ação de adicionar um produto ao carrinho na sessão.
    """
    produto = get_object_or_404(Produto, pk=produto_pk)
    carrinho = request.session.get('carrinho', {})
    pk_str = str(produto.pk)
    quantidade_no_carrinho = carrinho.get(pk_str, 0)

    if produto.estoque <= quantidade_no_carrinho:
        messages.error(request, "Produto indisponível no momento (sem estoque suficiente).")
        return redirect('shop_list')

    carrinho[pk_str] = quantidade_no_carrinho + 1
    request.session['carrinho'] = carrinho
    messages.success(request, f"'{produto.nome}' foi adicionado ao carrinho!")
    return redirect('shop_list')


@login_required
def cart_view(request):
    """
    Mostra os itens que estão atualmente no carrinho.
    """
    carrinho_session = request.session.get('carrinho', {})
    produto_ids = carrinho_session.keys()
    produtos_no_carrinho = Produto.objects.filter(pk__in=[int(pk) for pk in produto_ids])
    
    itens_carrinho = []
    total_compra = 0
    
    for produto in produtos_no_carrinho:
        pk_str = str(produto.pk)
        quantidade = carrinho_session[pk_str]
        subtotal = produto.preco * quantidade
        
        itens_carrinho.append({
            'produto': produto,
            'quantidade': quantidade,
            'subtotal': subtotal
        })
        total_compra += subtotal
        
    context = {
        'itens_carrinho': itens_carrinho,
        'total_compra': total_compra
    }
    # <<< CORRIGIDO: Usa o nome do seu template >>>
    return render(request, 'pets/petshop2.html', context)


@login_required
def remove_from_cart_view(request, produto_pk):
    """
    Ação de remover completamente um item do carrinho.
    """
    carrinho = request.session.get('carrinho', {})
    pk_str = str(produto_pk)
    
    if pk_str in carrinho:
        del carrinho[pk_str]
        request.session['carrinho'] = carrinho
        messages.info(request, "Produto removido do carrinho.")
        
    return redirect('cart_view')


@login_required
def checkout_view(request):
    """
    Processa o "pagamento" (simulado).
    """
    carrinho = request.session.get('carrinho', {})

    if not carrinho:
        messages.error(request, "Seu carrinho está vazio. Adicione produtos antes de finalizar.")
        return redirect('shop_list')

    ids = [int(pk) for pk in carrinho.keys()]
    produtos = Produto.objects.filter(pk__in=ids)
    
    for produto in produtos:
        pk_str = str(produto.pk)
        if produto.estoque < carrinho[pk_str]:
            messages.error(request, f"Desculpe, o produto '{produto.nome}' não tem estoque suficiente.")
            return redirect('cart_view')

    for produto in produtos:
        pk_str = str(produto.pk)
        produto.estoque -= carrinho[pk_str]
        produto.save()
        
    request.session['carrinho'] = {}
    
    return redirect('purchase_success')


@login_required
def purchase_success_view(request):
    """
    Mostra a mensagem de sucesso após a compra.
    """
    # <<< CORRIGIDO: Usa o nome do seu template >>>
    return render(request, 'pets/petshop3.html')