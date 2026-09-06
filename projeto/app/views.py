<<<<<<< HEAD
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
=======
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model

# Obtém o modelo de usuário ativo (accounts.Usuario)
Usuario = get_user_model()
>>>>>>> 3feed93 (ta funfando eu acho)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('app:dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        user = authenticate(request, username=email, password=senha)

        if user is not None:
            login(request, user)
            return redirect('app:dashboard')
        else:
            messages.error(request, 'E-mail ou senha inválidos.')

    return render(request, 'index.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'Sessão encerrada.')
    return redirect('app:login')


def cadastro_view(request):
    if request.method == 'POST':
        nome = request.POST.get('nome_completo') or request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'Este e-mail já está cadastrado!')
            return render(request, 'cadastro.html')

        # Cria e salva o usuário no MariaDB/MySQL com senha criptografada
        usuario = Usuario.objects.create_user(
            username=email,
            email=email,
            password=senha,
            first_name=nome
        )

        messages.success(request, 'Funcionário cadastrado com sucesso!')
        return redirect('app:login')

    return render(request, 'cadastro.html')


def listar_usuarios_view(request):
    return render(request, 'listar.html')


def editar_usuario_view(request, id=None):
    return render(request, 'editar.html')


def deletar_usuario_view(request, id=None):
    return render(request, 'confirmar_delecao.html')


def dashboard_view(request):
    return render(request, 'dashboard_admin.html')

<<<<<<< HEAD
@user_passes_test(acesso_estoque)
=======

>>>>>>> 3feed93 (ta funfando eu acho)
def controle_estoque_view(request):
    return render(request, 'estoque_controle.html')


<<<<<<< HEAD
@user_passes_test(acesso_estoque)
=======
>>>>>>> 3feed93 (ta funfando eu acho)
def detalhes_item_view(request):
    return render(request, 'estoque_item.html')


<<<<<<< HEAD
@user_passes_test(acesso_estoque)
=======
>>>>>>> 3feed93 (ta funfando eu acho)
def etiquetas_view(request):
    return render(request, 'estoque_etiquetas.html')


<<<<<<< HEAD
@user_passes_test(acesso_vendas)
=======
>>>>>>> 3feed93 (ta funfando eu acho)
def nova_venda_view(request):
    return render(request, 'vendas_vendedor.html')


<<<<<<< HEAD
@user_passes_test(acesso_caixa)
=======
>>>>>>> 3feed93 (ta funfando eu acho)
def caixa_pdv_view(request):
    return render(request, 'vendas_caixa.html')


<<<<<<< HEAD
@user_passes_test(acesso_caixa)
=======
>>>>>>> 3feed93 (ta funfando eu acho)
def relatorio_vendas_view(request):
    return render(request, 'caixa_relatorio.html')


<<<<<<< HEAD
@user_passes_test(acesso_compras)
=======
>>>>>>> 3feed93 (ta funfando eu acho)
def painel_compras_view(request):
    return render(request, 'compras.html')