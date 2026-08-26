from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Rota raiz do site (site.com/) vai direto para o Login
    path('', views.login_view, name='login'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]