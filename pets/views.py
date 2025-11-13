# ==============================================================================
# IMPORTS NECESSÁRIOS
# ==============================================================================
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Pet, Evento, Meta, ItemCompra 
from decimal import Decimal, InvalidOperation 
from datetime import date # <<< IMPORTAÇÃO CRÍTICA PARA A IDADE >>>

# Imports para o sistema de Login
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
import traceback


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
            return render(request, 'pets/pet_form.html', {'values': context_values, 'pet': None})
        
        try:
            peso_decimal = Decimal(peso) 
            if peso_decimal <= 0:
                messages.error(request, "O peso deve ser um valor positivo.")
                return render(request, 'pets/pet_form.html', {'values': context_values, 'pet': None})
        except (InvalidOperation, TypeError, ValueError): 
            messages.error(request, "O valor do peso é inválido.")
            return render(request, 'pets/pet_form.html', {'values': context_values, 'pet': None})

        try:
            Pet.objects.create(
                tutor=request.user,
                nome=nome,
                especie=especie,
                raca=raca or None, # Converte '' para None
                data_nascimento=data_nascimento,
                peso=peso_decimal
            )
            messages.success(request, f"Pet '{nome}' adicionado com sucesso!")
            return redirect('pet_list')
        except Exception:
            traceback.print_exc()
            messages.error(request, "Ocorreu um erro ao salvar o pet. Verifique os logs.")
            return render(request, 'pets/pet_form.html', {'values': context_values, 'pet': None})

    return render(request, 'pets/pet_form.html', {'values': {}, 'pet': None})

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
            peso_decimal = Decimal(peso)
            if peso_decimal <= 0:
                messages.error(request, "O peso deve ser um valor positivo.")
                return render(request, 'pets/pet_form.html', {'pet': pet, 'values': context_values})
        except (InvalidOperation, TypeError, ValueError):
            messages.error(request, "O valor do peso é inválido.")
            return render(request, 'pets/pet_form.html', {'pet': pet, 'values': context_values})

        try:
            pet.nome = nome
            pet.especie = especie
            pet.raca = raca or None # <<< CORREÇÃO DO BUG 500 ESTÁ AQUI
            pet.data_nascimento = data_nascimento
            pet.peso = peso_decimal
            pet.save()
            messages.success(request, f"Dados de '{pet.nome}' atualizados com sucesso!")
            return redirect('pet_list')
        except Exception:
            print("\n--- ERRO AO ATUALIZAR PET (traceback abaixo) ---")
            traceback.print_exc()
            messages.error(request, "Ocorreu um erro ao atualizar o pet. Verifique os logs do servidor.")
            return render(request, 'pets/pet_form.html', {'pet': pet, 'values': context_values})

    values = {
        'nome': pet.nome,
        'especie': pet.especie,
        'raca': pet.raca,
        'data_nascimento': pet.data_nascimento.strftime('%Y-%m-%d') if pet.data_nascimento else '',
        'peso': pet.peso
    }
    return render(request, 'pets/pet_form.html', {'pet': pet, 'values': values})

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
    
    # --- Cálculos dos Stats ---
    idade = None
    if pet.data_nascimento:
        hoje = date.today()
        idade = hoje.year - pet.data_nascimento.year - ((hoje.month, hoje.day) < (pet.data_nascimento.month, pet.data_nascimento.day))
    
    total_eventos = pet.eventos.count()
    metas_concluidas = pet.metas.filter(progresso=100).count()
    
    # --- Listas ---
    eventos = pet.eventos.all().order_by('-data')[:5]
    
    # <<< CORREÇÃO DO BUG 2 (FAIL) >>>
    # Filtra para mostrar apenas metas em andamento (progresso < 100)
    metas_em_andamento = pet.metas.filter(progresso__lt=100).order_by('progresso', 'data_prazo')
    
    context = {
        'pet': pet, 
        'eventos': eventos, 
        'metas': metas_em_andamento, # <-- Usa a lista filtrada
        'idade': idade, 
        'total_eventos': total_eventos, 
        'metas_concluidas': metas_concluidas, 
    }
    
    if not eventos and not metas_em_andamento:
        messages.info(request, 'Esse pet ainda não possui registros de eventos ou metas.')
        
    return render(request, 'pets/pet_visao_geral.html', context)


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
        observacoes = request.POST.get('observacoes')

        if not tipo or not data:
            messages.error(request, "Os campos Tipo de Evento e Data são obrigatórios.")
            context = {
                'pet': pet, 
                'tipos_evento': Evento.TIPOS_EVENTO, 
                'values': request.POST, 
                'evento': None 
            }
            return render(request, 'pets/evento_adicionar.html', context)
        
        if not observacoes:
            observacoes = None

        Evento.objects.create(
            pet=pet, tipo=tipo, data=data,
            observacoes=observacoes
        )
        messages.success(request, "Evento adicionado!")
        return redirect('evento_list', pet_pk=pet.pk)

    context = {
        'pet': pet, 
        'tipos_evento': Evento.TIPOS_EVENTO, 
        'values': {}, 
        'evento': None 
    }
    return render(request, 'pets/evento_adicionar.html', context)


@login_required
def evento_edit(request, pk):
    evento = get_object_or_404(Evento, pk=pk, pet__tutor=request.user)
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        data = request.POST.get('data')
        observacoes = request.POST.get('observacoes')

        if not tipo or not data:
            messages.error(request, "Os campos Tipo de Evento e Data são obrigatórios.")
            context = {'pet': evento.pet, 'evento': evento, 'tipos_evento': Evento.TIPOS_EVENTO, 'values': request.POST}
            return render(request, 'pets/evento_adicionar.html', context)
        
        # <<< CORREÇÃO DO BUG 500 ESTÁ AQUI >>>
        if not observacoes:
            observacoes = None

        evento.tipo = tipo
        evento.data = data
        evento.observacoes = observacoes # <-- Salva None
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
        messages.success(request, f"Evento '{evento.get_tipo_display()}' removido com sucesso.")
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
    
    # Redireciona de volta para a Visão Geral
    return redirect('pet_visao_geral', pk=meta.pet.pk)


@login_required
def shop_list_view(request, pet_pk):
    pet = get_object_or_404(Pet, pk=pet_pk, tutor=request.user)
    
    if request.method == 'POST':
        descricao = request.POST.get('descricao')
        if not descricao:
            messages.error(request, 'Você precisa digitar o nome do item.')
        else:
            ItemCompra.objects.create(pet=pet, descricao=descricao)
            messages.success(request, 'Item adicionado à lista de compras!')
        return redirect('shop_list', pet_pk=pet.pk)
    
    itens_nao_comprados = ItemCompra.objects.filter(pet=pet, comprado=False).order_by('criado_em')
    itens_comprados = ItemCompra.objects.filter(pet=pet, comprado=True).order_by('-criado_em')
    
    context = {
        'pet': pet,
        'itens_nao_comprados': itens_nao_comprados,
        'itens_comprados': itens_comprados,
    }
    return render(request, 'pets/petshop.html', context)


@login_required
def shop_item_marcar(request, pk):
    item = get_object_or_404(ItemCompra, pk=pk, pet__tutor=request.user)
    
    item.comprado = not item.comprado
    item.save()
    
    if item.comprado:
        messages.success(request, f"Item '{item.descricao}' marcado como comprado!")
    else:
        messages.info(request, f"Item '{item.descricao}' movido de volta para a lista.")
        
    return redirect('shop_list', pet_pk=item.pet.pk)


@login_required
def shop_item_remover(request, pk):
    item = get_object_or_404(ItemCompra, pk=pk, pet__tutor=request.user)
    descricao_item = item.descricao
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, f"Item '{descricao_item}' removido da lista.")
        return redirect('shop_list', pet_pk=item.pet.pk)
    
    return render(request, 'pets/shop_item_confirm_delete.html', {'item': item})