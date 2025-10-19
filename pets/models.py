from django.db import models

class Pet(models.Model):
    nome = models.CharField(max_length=100)
    especie = models.CharField(max_length=50)
    raca = models.CharField(max_length=50, blank=True, null=True)
    data_nascimento = models.DateField()
    peso = models.FloatField()

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
    concluida = models.BooleanField(default=False) 

    def __str__(self):
        return f"Meta para {self.pet.nome}: {self.descricao[:30]}..."
