# ==============================================================================
# IMPORTS NECESSÁRIOS
# ==============================================================================
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages  # Importa o framework de mensagens
from .models import Pet, Evento, Meta

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

        # Dicionário para repopular o formulário em caso de erro
        context_values = {
            'nome': nome, 'especie': especie, 'raca': raca, 
            'data_nascimento': data_nascimento, 'peso': peso
        }

        if not nome or not especie or not data_nascimento or not peso:
            # <<< ADICIONADO: Mensagem de erro >>>
            messages.error(request, "Os campos Nome, Espécie, Data de Nascimento e Peso são obrigatórios.")
            # Passa os valores de volta para repopular
            return render(request, 'pets/pet_form.html', {'values': context_values})
        try:
            if float(peso) <= 0:
                # <<< ADICIONADO: Mensagem de erro >>>
                messages.error(request, "O peso deve ser um valor positivo.")
                return render(request, 'pets/pet_form.html', {'values': context_values})
        except (ValueError, TypeError):
             # <<< ADICIONADO: Mensagem de erro >>>
            messages.error(request, "O valor do peso é inválido.")
            return render(request, 'pets/pet_form.html', {'values': context_values})
        
        Pet.objects.create(
            tutor=request.user,
            nome=nome,
            especie=especie,
            raca=raca,
            data_nascimento=data_nascimento,
            peso=peso
        )
        # <<< ADICIONADO: Mensagem de sucesso >>>
        messages.success(request, f"Pet '{nome}' adicionado com sucesso!")
        return redirect('pet_list')
    
    return render(request, 'pets/pet_form.html')


@login_required
def pet_edit(request, pk):
    pet = get_object_or_404(Pet, pk=pk, tutor=request.user)
    if request.method == 'POST':
        nome = request.POST.get('nome')
        especie = request.POST.get('especie')
        raca = request.POST.get('raca')
        data_nascimento = request.POST.get('data_nascimento')
        peso = request.POST.get('peso')

        if not nome or not especie or not data_nascimento or not peso:
             # <<< ADICIONADO: Mensagem de erro >>>
            messages.error(request, "Todos os campos obrigatórios devem ser preenchidos.")
            return render(request, 'pets/pet_form.html', {'pet': pet}) # Mantém os dados originais no form
        try:
            if float(peso) <= 0:
                # <<< ADICIONADO: Mensagem de erro >>>
                messages.error(request, "O peso deve ser um valor positivo.")
                return render(request, 'pets/pet_form.html', {'pet': pet})
        except (ValueError, TypeError):
             # <<< ADICIONADO: Mensagem de erro >>>
            messages.error(request, "O valor do peso é inválido.")
            return render(request, 'pets/pet_form.html', {'pet': pet})

        pet.nome = nome
        pet.especie = especie
        pet.raca = raca
        pet.data_nascimento = data_nascimento
        pet.peso = peso
        pet.save()
        # <<< ADICIONADO: Mensagem de sucesso >>>
        messages.success(request, f"Dados de '{pet.nome}' atualizados com sucesso!")
        return redirect('pet_list')
    return render(request, 'pets/pet_form.html', {'pet': pet})


@login_required
def pet_delete(request, pk):
    pet = get_object_or_404(Pet, pk=pk, tutor=request.user)
    if request.method == 'POST':
        nome_pet_deletado = pet.nome # Guarda o nome antes de deletar
        pet.delete()
        # <<< ADICIONADO: Mensagem de sucesso >>>
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


# --- VIEWS DE EVENTOS (TODAS PROTEGIDAS) ---

@login_required
def evento_selecionar_pet(request):
    pets = Pet.objects.filter(tutor=request.user)
    if not pets.exists():
        # <<< ADICIONADO: Mensagem informativa >>>
        messages.info(request, "Não há pets cadastrados. Cadastre um pet antes de adicionar um evento.")
        return render(request, 'pets/evento_sem_pets.html')

    if request.method == 'POST':
        pet_pk = request.POST.get('pet_selecionado')
        if not pet_pk:
            # <<< ADICIONADO: Mensagem de erro >>>
            messages.error(request, "Você precisa selecionar um pet.")
            return render(request, 'pets/evento_selecionar_pet.html', {'pets': pets})
        
        # Garante que o pet selecionado pertence ao usuário
        if Pet.objects.filter(pk=pet_pk, tutor=request.user).exists():
            return redirect('evento_adicionar', pet_pk=pet_pk)
        else:
             # Medida de segurança extra, caso alguém tente burlar o formulário
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
            # <<< ADICIONADO: Mensagem de erro >>>
            messages.error(request, "Os campos Tipo de Evento e Data são obrigatórios.")
            context = {'pet': pet, 'tipos_evento': Evento.TIPOS_EVENTO}
            return render(request, 'pets/evento_adicionar.html', context)

        Evento.objects.create(
            pet=pet,
            tipo=tipo,
            data=data,
            observacoes=request.POST.get('observacoes')
        )
        # <<< ADICIONADO: Mensagem de sucesso >>>
        messages.success(request, "Evento adicionado!")
        return redirect('evento_list', pet_pk=pet.pk)
    context = {'pet': pet, 'tipos_evento': Evento.TIPOS_EVENTO}
    return render(request, 'pets/evento_adicionar.html', context)


@login_required
def evento_edit(request, pk):
    evento = get_object_or_404(Evento, pk=pk, pet__tutor=request.user)
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        data = request.POST.get('data')
        
        # <<< ADICIONADO: Validação para edição >>>
        if not tipo or not data:
            messages.error(request, "Os campos Tipo de Evento e Data são obrigatórios.")
            context = {'pet': evento.pet, 'evento': evento, 'tipos_evento': Evento.TIPOS_EVENTO}
            return render(request, 'pets/evento_adicionar.html', context) # Reusa o template
            
        evento.tipo = tipo
        evento.data = data
        evento.observacoes = request.POST.get('observacoes')
        evento.save()
        # <<< ADICIONADO: Mensagem de sucesso >>>
        messages.success(request, "Evento atualizado com sucesso!")
        return redirect('evento_list', pet_pk=evento.pet.pk)
    context = {'pet': evento.pet, 'evento': evento, 'tipos_evento': Evento.TIPOS_EVENTO}
    return render(request, 'pets/evento_adicionar.html', context) # Reusa o template para GET


@login_required
def evento_delete(request, pk):
    evento = get_object_or_404(Evento, pk=pk, pet__tutor=request.user)
    pet = evento.pet
    if request.method == 'POST':
        evento.delete()
        # <<< ADICIONADO: Mensagem de sucesso >>>
        messages.success(request, "Evento removido com sucesso.")
        return redirect('evento_list', pet_pk=pet.pk)
    return render(request, 'pets/evento_confirm_delete.html', {'evento': evento, 'pet': pet})


@login_required
def evento_concluir(request, pk):
    evento = get_object_or_404(Evento, pk=pk, pet__tutor=request.user)
    if evento.concluido:
        messages.warning(request, 'Esse evento já foi concluído.')
    else:
        evento.concluido = True
        evento.save()
        messages.success(request, 'Evento marcado como concluído!')
    return redirect('evento_list', pet_pk=evento.pet.pk)


# --- VIEWS DE METAS (TODAS PROTEGIDAS) ---

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
                pet=pet,
                descricao=descricao,
                data_prazo=data_prazo
            )
            messages.success(request, 'Meta adicionada!')
        # Redireciona de volta para a mesma página (GET) para mostrar a mensagem
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
    # Redireciona de volta para a Visão Geral após atualizar
    return redirect('pet_visao_geral', pk=meta.pet.pk)