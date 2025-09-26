# Em pets/views.py

from django.shortcuts import render, get_object_or_404, redirect
# IMPORTAMOS TUDO QUE VAMOS PRECISAR
from .models import Pet, Evento


# --- VIEWS DA PÁGINA INICIAL E DE PETS (NÃO MUDAM) ---
def home_view(request):
    """
    Renderiza a página inicial de boas-vindas.
    """
    return render(request, 'pets/home.html')

def pet_list(request):
    pets = Pet.objects.all()
    return render(request, 'pets/pet_list.html', {'pets': pets})

def pet_create(request):
    if request.method == 'POST':
        # Pegamos os dados manualmente do objeto request.POST
        nome = request.POST.get('nome')
        especie = request.POST.get('especie')
        raca = request.POST.get('raca')
        data_nascimento = request.POST.get('data_nascimento')
        peso = request.POST.get('peso')

        # Validação manual simples
        if not nome or not especie or not data_nascimento or not peso:
            error_message = "Os campos Nome, Espécie, Data de Nascimento e Peso são obrigatórios."
            return render(request, 'pets/pet_form.html', {'error_message': error_message})
        
        try:
            if float(peso) <= 0:
                error_message = "O peso deve ser um valor positivo."
                return render(request, 'pets/pet_form.html', {'error_message': error_message})
        except (ValueError, TypeError):
            error_message = "O valor do peso é inválido."
            return render(request, 'pets/pet_form.html', {'error_message': error_message})

        # Criamos o objeto Pet e salvamos no banco
        Pet.objects.create(
            nome=nome,
            especie=especie,
            raca=raca,
            data_nascimento=data_nascimento,
            peso=peso
        )
        return redirect('pet_list')
    
    # Se for um GET, apenas mostra o formulário vazio
    return render(request, 'pets/pet_form.html')

def pet_edit(request, pk):
    pet = get_object_or_404(Pet, pk=pk)

    if request.method == 'POST':
        # Pegamos os dados novos do formulário
        nome = request.POST.get('nome')
        especie = request.POST.get('especie')
        raca = request.POST.get('raca')
        data_nascimento = request.POST.get('data_nascimento')
        peso = request.POST.get('peso')

        # Validação manual
        if not nome or not especie or not data_nascimento or not peso:
            error_message = "Todos os campos obrigatórios devem ser preenchidos."
            return render(request, 'pets/pet_form.html', {'error_message': error_message, 'pet': pet})

        try:
            if float(peso) <= 0:
                error_message = "O peso deve ser um valor positivo."
                return render(request, 'pets/pet_form.html', {'error_message': error_message, 'pet': pet})
        except (ValueError, TypeError):
            error_message = "O valor do peso é inválido."
            return render(request, 'pets/pet_form.html', {'error_message': error_message, 'pet': pet})


        # Atualizamos o objeto pet com os dados novos
        pet.nome = nome
        pet.especie = especie
        pet.raca = raca
        pet.data_nascimento = data_nascimento
        pet.peso = peso
        pet.save() # Salva as alterações no banco

        return redirect('pet_list')

    # Se for um GET, passa o objeto 'pet' para o template preencher os campos
    return render(request, 'pets/pet_form.html', {'pet': pet})

def pet_delete(request, pk):
    pet = get_object_or_404(Pet, pk=pk)
    if request.method == 'POST':
        pet.delete()
        return redirect('pet_list')
    return render(request, 'pets/pet_confirm_delete.html', {'pet': pet})


# --- ADICIONE TODAS AS NOVAS VIEWS PARA O FLUXO DE EVENTOS AQUI ---

# Em pets/views.py

# ... (outras views) ...

# --- SUBSTITUA A VIEW evento_selecionar_pet POR ESTA ---
def evento_selecionar_pet(request):
    if not Pet.objects.exists():
        return render(request, 'pets/evento_sem_pets.html')

    if request.method == 'POST':
        pet_pk = request.POST.get('pet_selecionado')
        if not pet_pk:
            pets = Pet.objects.all()
            error_message = "Você precisa selecionar um pet."
            return render(request, 'pets/evento_selecionar_pet.html', {'pets': pets, 'error_message': error_message})
        
        return redirect('evento_adicionar', pet_pk=pet_pk)

    pets = Pet.objects.all()
    return render(request, 'pets/evento_selecionar_pet.html', {'pets': pets})

def evento_adicionar(request, pet_pk):
    pet = get_object_or_404(Pet, pk=pet_pk)
    
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        data = request.POST.get('data')
        observacoes = request.POST.get('observacoes')

        if not tipo or not data:
            error_message = "Os campos Tipo de Evento e Data são obrigatórios."
            context = {
                'pet': pet, 
                'tipos_evento': Evento.TIPOS_EVENTO,
                'error_message': error_message
            }
            return render(request, 'pets/evento_adicionar.html', context)

        Evento.objects.create(
            pet=pet,
            tipo=tipo,
            data=data,
            observacoes=observacoes
        )
        return redirect('evento_list', pet_pk=pet.pk)

    context = {
        'pet': pet,
        'tipos_evento': Evento.TIPOS_EVENTO # Passa as opções para o template
    }
    return render(request, 'pets/evento_adicionar.html', context)

def evento_list(request, pet_pk):
    pet = get_object_or_404(Pet, pk=pet_pk)
    eventos = Evento.objects.filter(pet=pet).order_by('-data')
    return render(request, 'pets/evento_list.html', {'pet': pet, 'eventos': eventos})

def evento_edit(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    pet = evento.pet

    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        data = request.POST.get('data')
        observacoes = request.POST.get('observacoes')

        if not tipo or not data:
            error_message = "Os campos Tipo de Evento e Data são obrigatórios."
            context = {
                'pet': pet, 
                'evento': evento,
                'tipos_evento': Evento.TIPOS_EVENTO,
                'error_message': error_message
            }
            return render(request, 'pets/evento_adicionar.html', context)

        evento.tipo = tipo
        evento.data = data
        evento.observacoes = observacoes
        evento.save()
        return redirect('evento_list', pet_pk=pet.pk)

    context = {
        'pet': pet,
        'evento': evento,
        'tipos_evento': Evento.TIPOS_EVENTO
    }
    return render(request, 'pets/evento_adicionar.html', context)

def evento_delete(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    pet = evento.pet
    if request.method == 'POST':
        evento.delete()
        return redirect('evento_list', pet_pk=pet.pk)
    return render(request, 'pets/evento_confirm_delete.html', {'evento': evento, 'pet': pet})