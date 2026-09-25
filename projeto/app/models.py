from django.db import models

class Fornecedor(models.Model):
    nome = models.CharField(max_length=255)
    CNPJ = models.CharField(max_length=20, blank=True, null=True)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    categorias = models.CharField(max_length=255, blank=True, null=True) # Adicionado aqui

    def __str__(self):
        return self.nome