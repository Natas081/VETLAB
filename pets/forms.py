from django import forms
from .models import Pet, Evento

class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = '__all__'

# --- NOVO FORMULÁRIO PARA A TELA DE SELEÇÃO DE PETS ---
class PetSelecaoForm(forms.Form):
    # Cria um campo onde o usuário pode escolher um pet de uma lista
    # queryset=Pet.objects.all() busca todos os pets no banco
    # widget=forms.RadioSelect faz com que as opções apareçam como botões de rádio
    pet_selecionado = forms.ModelChoiceField(
        queryset=Pet.objects.all(),
        widget=forms.RadioSelect,
        empty_label=None, # Remove a opção "---------"
        label="Selecione o pet para cadastrar o evento"
    )

# --- FORMULÁRIO DE EVENTO ATUALIZADO ---
class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        # O campo 'pet' será cuidado pela view, não pelo usuário
        exclude = ('pet',)
        # Widgets para melhorar a interface
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'observacoes': forms.Textarea(attrs={'rows': 4}),
        }