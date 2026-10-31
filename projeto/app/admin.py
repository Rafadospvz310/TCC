from django.contrib import admin
from .models import ItemVenda, Produto, Venda

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'codigo_barras', 'preco_custo', 'quantidade')
    search_fields = ('nome', 'codigo_barras', 'id')

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ('id', 'data_venda', 'valor_total', 'forma_pagamento', 'vendedor')

@admin.register(ItemVenda)
class ItemVendaAdmin(admin.ModelAdmin):
    list_display = ('id', 'venda', 'produto', 'quantidade', 'preco_unitario')