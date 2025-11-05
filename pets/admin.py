from django.contrib import admin
# IMPORTANTE: Importa todos os modelos necessários
from .models import Pet, Evento, Meta, Produto

# Registra cada modelo para que apareça no admin
admin.site.register(Pet)
admin.site.register(Evento)
admin.site.register(Meta)
admin.site.register(Produto)