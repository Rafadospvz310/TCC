from django.urls import path
from . import views

app_name = 'compras'

urlpatterns = [

    path('', views.painel_compras, name='painel'),
]