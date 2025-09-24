# Em pets/views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import Pet
from .forms import PetForm

# --- SUAS FUNÇÕES ANTIGAS (NÃO MEXA NELAS) ---
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


# --- ADICIONE A NOVA FUNÇÃO AQUI NO FINAL ---
def home_view(request):
    """
    Renderiza a página inicial de boas-vindas.
    """
    return render(request, 'pets/home.html')