from django.urls import path
from . import views

urlpatterns = [
    path('', views.nova_venda, name='vendas_nova'),
    path('caixa/', views.pdv_caixa, name='vendas_caixa'),
    path('relatorio/', views.relatorio_caixa, name='caixa_relatorio'),
]