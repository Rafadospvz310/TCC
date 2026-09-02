from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.login_view, name='index'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('usuarios/', views.listar_usuarios_view, name='listar'),
    path('usuarios/editar/<int:id>/', views.editar_usuario_view, name='editar'),
    path('usuarios/deletar/<int:id>/', views.deletar_usuario_view, name='deletar'),
    
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    path('estoque/', views.controle_estoque_view, name='controle'),
    path('estoque/item/', views.detalhes_item_view, name='item'),
    path('estoque/etiquetas/', views.etiquetas_view, name='etiquetas'),
    
    path('vendas/nova/', views.nova_venda_view, name='nova'),
    path('caixa/', views.caixa_pdv_view, name='caixa'),
    path('caixa/relatorio/', views.relatorio_vendas_view, name='relatorio'),
    
    path('compras/', views.painel_compras_view, name='painel'),
]