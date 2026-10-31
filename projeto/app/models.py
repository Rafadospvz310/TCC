from django.db import models

class Fornecedor(models.Model):
    nome = models.CharField(max_length=255)
    CNPJ = models.CharField(max_length=20, blank=True, null=True)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    categorias = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'fornecedores'

    def __str__(self):
        return self.nome


class Produto(models.Model):
    nome = models.CharField(max_length=255)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, related_name='produtos')
    categoria = models.CharField(max_length=100, blank=True, null=True)
    codigo_barras = models.CharField(max_length=100, blank=True, null=True)
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    quantidade = models.IntegerField(default=0)
    foto = models.ImageField(upload_to='produtos/', blank=True, null=True)

    class Meta:
        db_table = 'produtos'

    def __str__(self):
        return self.nome


# Se o seu forms.py importa estes outros modelos, declare-os aqui para evitar novos erros de importação:
class Categoria(models.Model):
    nome = models.CharField(max_length=100)

    class Meta:
        db_table = 'categorias'

    def __str__(self):
        return self.nome


class Cliente(models.Model):
    nome = models.CharField(max_length=255)

    class Meta:
        db_table = 'clientes'


from django.conf import settings  # Certifique-se de que esta importação está no topo do models.py

# ... (outros modelos)

class Venda(models.Model):
    data_venda = models.DateTimeField(auto_now_add=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    forma_pagamento = models.CharField(max_length=50, blank=True, null=True)
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'vendas'


class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Adicionado para guardar o preço no momento da venda

    class Meta:
        db_table = 'itens_venda'