
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
   path('estoque/', include(('estoque.urls', 'estoque'), namespace='estoque')),
    path('compras/', include('compras.urls')),
    path('vendas/', include('vendas.urls')),
    path('', include('usuarios.urls')),
]
