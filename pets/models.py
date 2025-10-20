from django.db import models
from datetime import date 
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator 

class Pet(models.Model):
    tutor = models.ForeignKey(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    especie = models.CharField(max_length=50)
    raca = models.CharField(max_length=50, blank=True, null=True)
    data_nascimento = models.DateField()
    peso = models.FloatField()
    def calcular_idade(self):
        hoje = date.today()

        idade = hoje.year - self.data_nascimento.year - ((hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day))
        return f"{idade} anos"

    def __str__(self):
        return self.nome

    def __str__(self):
        return self.nome
        #adicionando método para representar o pet pelo nome

        #adicionando método para representar o eventio pelo nome



class Evento(models.Model):
    TIPOS_EVENTO = [
        ('vacina', 'Vacina'),
        ('consulta', 'Consulta'),
        ('medicamento', 'Medicamento'),
    ]

    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name="eventos")
    tipo = models.CharField(max_length=20, choices=TIPOS_EVENTO)
    data = models.DateField()
    observacoes = models.TextField(blank=True, null=True)

    concluido = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.tipo} - {self.pet.nome}"
    
    # ... (classe Pet e Evento continuam aqui em cima) ...

class Meta(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name="metas")
    descricao = models.TextField()  
    data_prazo = models.DateField() 
    progresso = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )


    def __str__(self):
        return f"Meta para {self.pet.nome}: {self.descricao[:30]}..." # Mostra os primeiros 30 caracteres
