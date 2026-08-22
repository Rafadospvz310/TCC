from django.urls import path
from . import views

urlpatterns = [
    path('', views.painel_compras, name='compras_painel'),
]
