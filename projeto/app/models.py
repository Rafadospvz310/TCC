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


class Venda(models.Model):
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'vendas'


class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField(default=1)

    class Meta:
        db_table = 'itens_venda'