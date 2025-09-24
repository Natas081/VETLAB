# Em project/urls.py

from django.contrib import admin
from django.urls import path, include
# IMPORTAMOS AS VIEWS DO APP PETS
from pets import views as pets_views

urlpatterns = [
    # A linha abaixo vai renderizar nossa página inicial na raiz do site
    path('', pets_views.home_view, name='home'),
    
    path('admin/', admin.site.urls),
    path('pets/', include('pets.urls')),
]