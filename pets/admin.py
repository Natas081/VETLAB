from django.contrib import admin
from .models import Pet, Evento, Meta, ItemCompra # <-- Mudança aqui

admin.site.register(Pet)
admin.site.register(Evento)
admin.site.register(Meta)
admin.site.register(ItemCompra) # <-- Mudança aqui