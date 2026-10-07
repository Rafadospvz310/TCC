from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'app'

urlpatterns = [
    path('', views.login_view, name='index'),
    
    path('logout/', views.logout_view, name='logout'),
    
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('usuarios/', views.listar_usuarios_view, name='listar'),
    path('usuarios/editar/<int:id>/', views.editar_usuario_view, name='editar'),
    path('usuarios/deletar/<int:id>/', views.deletar_usuario_view, name='deletar'),
    
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    path('estoque/', views.controle_estoque_view, name='controle'),
    path('estoque/item/', views.detalhes_item_view, name='item'),
    path('estoque/etiquetas/', views.etiquetas_view, name='etiquetas'),
    path('etiquetas/', views.gerar_etiquetas_view, name='etiquetas'),
    path('estoque/deletar/<int:produto_id>/', views.deletar_produto_view, name='deletar_produto'),
    path('estoque/item/<int:produto_id>/', views.consultar_item_view, name='item_detalhe'),
    
    path('vendas/nova/', views.nova_venda_view, name='nova'),
    path('caixa/', views.caixa_pdv_view, name='caixa'),
    path('caixa/relatorio/', views.relatorio_vendas_view, name='relatorio'),
    
    path('painel_compras_view/', views.painel_compras_view, name='painel'),
    path('painel_compras_view/', views.painel_compras_view, name='compras'),
    path('fornecedor/novo/', views.cadastro_fornecedor_view, name='cadastro_fornecedor'),

    path('login/', views.login_view, name='login'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)