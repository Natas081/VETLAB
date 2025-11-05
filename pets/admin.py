from django.contrib import admin
# Importa todos os seus modelos
from .models import Pet, Evento, Meta, Produto

# Registra cada um deles
admin.site.register(Pet)
admin.site.register(Evento)
admin.site.register(Meta)
admin.site.register(Produto)