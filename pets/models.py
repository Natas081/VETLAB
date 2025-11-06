from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# ==============================================================================
# MODELO DO PET
# ==============================================================================
class Pet(models.Model):
    tutor = models.ForeignKey(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    especie = models.CharField(max_length=50)
    raca = models.CharField(max_length=50, blank=True, null=True)
    data_nascimento = models.DateField()
    peso = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.nome} ({self.especie}) - Tutor: {self.tutor.username}"

# ==============================================================================
# MODELO DO EVENTO
# ==============================================================================
class Evento(models.Model):
    TIPOS_EVENTO = (
        ('vacina', 'Vacina'),
        ('consulta', 'Consulta'),
        ('medicamento', 'Medicamento'),
        ('higiene', 'Higiene'),
        ('outro', 'Outro'),
    )
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='eventos')
    tipo = models.CharField(max_length=20, choices=TIPOS_EVENTO)
    data = models.DateField()
    observacoes = models.TextField(blank=True, null=True)
    concluido = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_tipo_display()} de {self.pet.nome} em {self.data}"

# ==============================================================================
# MODELO DA META
# ==============================================================================
class Meta(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='metas')
    descricao = models.CharField(max_length=255)
    data_prazo = models.DateField()
    progresso = models.IntegerField(default=0) # 0 a 100

    def __str__(self):
        return f"Meta para {self.pet.nome}: {self.descricao}"

# ==============================================================================
# <<< REMOVIDO: Modelo Produto >>>
# ==============================================================================

# ==============================================================================
# <<< NOVO MODELO: Item de Compra >>>
# ==============================================================================
class ItemCompra(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='lista_compras')
    descricao = models.CharField(max_length=255)
    criado_em = models.DateTimeField(auto_now_add=True)
    comprado = models.BooleanField(default=False)

    def __str__(self):
        return f"Comprar '{self.descricao}' para {self.pet.nome}"