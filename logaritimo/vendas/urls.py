from django.urls import path
from . import views

app_name = 'vendas'

urlpatterns = [
        
    path('', views.nova_venda, name='nova'),
    path('caixa/', views.pdv_caixa, name='caixa'),
    path('relatorio/', views.relatorio_caixa, name='relatorio'),
]