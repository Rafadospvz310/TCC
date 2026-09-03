from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    PERMISSOES = ( 
        ('ADMINISTRADOR', 'Administrador'),
        ('ESTOQUE', 'Estoque'),
        ('VENDEDOR', 'Vendedor'),
        ('CAIXA', 'Caixa'),
        ('COMPRAS', 'Compras')
    )

    role = models.CharField(max_length=20, choices=PERMISSOES, default='VENDEDOR')
    