# Em pets/views.py

from django.shortcuts import render, get_object_or_404, redirect
# IMPORTAMOS TUDO QUE VAMOS PRECISAR
from .models import Pet, Evento
from .forms import PetForm, EventoForm, PetSelecaoForm

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
        form = PetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pet_list')
    else:
        form = PetForm()
    return render(request, 'pets/pet_form.html', {'form': form})

def pet_edit(request, pk):
    pet = get_object_or_404(Pet, pk=pk)
    if request.method == 'POST':
        form = PetForm(request.POST, instance=pet)
        if form.is_valid():
            form.save()
            return redirect('pet_list')
    else:
        form = PetForm(instance=pet)
    return render(request, 'pets/pet_form.html', {'form': form})

def pet_delete(request, pk):
    pet = get_object_or_404(Pet, pk=pk)
    if request.method == 'POST':
        pet.delete()
        return redirect('pet_list')
    return render(request, 'pets/pet_confirm_delete.html', {'pet': pet})


# --- ADICIONE TODAS AS NOVAS VIEWS PARA O FLUXO DE EVENTOS AQUI ---

def evento_selecionar_pet(request):
    """
    View para o Passo 1 do fluxo: Selecionar o Pet.
    Corresponde à 'História 3' e 'Cenário 2' do seu diagrama.
    """
    if not Pet.objects.exists():
        return render(request, 'pets/evento_sem_pets.html')

    if request.method == 'POST':
        form = PetSelecaoForm(request.POST)
        if form.is_valid():
            pet_selecionado = form.cleaned_data['pet_selecionado']
            return redirect('evento_adicionar', pet_pk=pet_selecionado.pk)
    else:
        form = PetSelecaoForm()

    return render(request, 'pets/evento_selecionar_pet.html', {'form': form})

def evento_adicionar(request, pet_pk):
    """
    View para o Passo 2: Adicionar os detalhes do evento.
    Corresponde ao 'Cenário 5' do seu diagrama.
    """
    pet = get_object_or_404(Pet, pk=pet_pk)
    if request.method == 'POST':
        form = EventoForm(request.POST)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.pet = pet
            evento.save()
            return redirect('evento_list', pet_pk=pet.pk)
    else:
        form = EventoForm()
    
    return render(request, 'pets/evento_adicionar.html', {'form': form, 'pet': pet})

def evento_list(request, pet_pk):
    pet = get_object_or_404(Pet, pk=pet_pk)
    eventos = Evento.objects.filter(pet=pet).order_by('-data')
    return render(request, 'pets/evento_list.html', {'pet': pet, 'eventos': eventos})

def evento_edit(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    if request.method == 'POST':
        form = EventoForm(request.POST, instance=evento)
        if form.is_valid():
            form.save()
            return redirect('evento_list', pet_pk=evento.pet.pk)
    else:
        form = EventoForm(instance=evento)
    # Reutilizando o template de adicionar para edição
    return render(request, 'pets/evento_adicionar.html', {'form': form, 'pet': evento.pet})

def evento_delete(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    pet = evento.pet
    if request.method == 'POST':
        evento.delete()
        return redirect('evento_list', pet_pk=pet.pk)
    return render(request, 'pets/evento_confirm_delete.html', {'evento': evento, 'pet': pet})