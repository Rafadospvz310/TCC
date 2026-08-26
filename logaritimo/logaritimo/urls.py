
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='usuarios:login'), name='home'),
    
    path('admin/', admin.site.urls),
    path('estoque/', include('estoque.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('vendas/', include('vendas.urls')),
    path('compras/', include('compras.urls')),
]
