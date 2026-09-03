from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test

def acesso_estoque(user):
    return user.is_authenticated and (user.role == 'ESTOQUE' or user.role == 'ADMINISTRADOR')

def acesso_vendas(user):
    return user.is_authenticated and (user.role == 'VENDEDOR' or user.role == 'ADMINISTRADOR')

def acesso_caixa(user):
    return user.is_authenticated and (user.role == 'CAIXA' or user.role == 'ADMINISTRADOR')

def acesso_compras(user):
    return user.is_authenticated and (user.role == 'COMPRAS' or user.role == 'ADMINISTRADOR')

def login_view(request):
    return render(request, 'index.html')


def login_view(request):
    return render(request, 'index.html')

def cadastro_view(request):
    return render(request, 'cadastro.html')

def listar_usuarios_view(request):
    return render(request, 'listar.html')

def editar_usuario_view(request):
    return render(request, 'editar.html')

def deletar_usuario_view(request):
    return render(request, 'confirmar_delecao.html')

def dashboard_view(request):
    return render(request, 'dashboard_admin.html')

@user_passes_test(acesso_estoque)
def controle_estoque_view(request):
    return render(request, 'estoque_controle.html')


@user_passes_test(acesso_estoque)
def detalhes_item_view(request):
    return render(request, 'estoque_item.html')


@user_passes_test(acesso_estoque)
def etiquetas_view(request):
    return render(request, 'estoque_etiquetas.html')


@user_passes_test(acesso_vendas)
def nova_venda_view(request):
    return render(request, 'vendas_vendedor.html')


@user_passes_test(acesso_caixa)
def caixa_pdv_view(request):
    return render(request, 'vendas_caixa.html')


@user_passes_test(acesso_caixa)
def relatorio_vendas_view(request):
    return render(request, 'caixa_relatorio.html')


@user_passes_test(acesso_compras)
def painel_compras_view(request):
    return render(request, 'compras.html')