from django.urls import path
from . import views

urlpatterns = [
    path('', views.controle_geral, name='estoque_controle'),
    path('item/', views.consultar_item, name='estoque_item'),
    path('etiquetas/', views.gerar_etiquetas, name='estoque_etiquetas'),
]