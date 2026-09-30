from django.contrib import admin
from .models import Produto

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'codigo_barras', 'preco_custo', 'quantidade')
    search_fields = ('nome', 'codigo_barras', 'id')