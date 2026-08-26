from django.urls import path
from . import views

app_name = 'estoque'

urlpatterns = [
    path('', views.controle_geral, name='controle'),
    path('item/', views.consultar_item, name='item'),
    path('etiquetas/', views.gerar_etiquetas, name='etiquetas'),
]