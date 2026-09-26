from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from .forms import UsuarioCadastroForm, FornecedorCadastro
from .models import Fornecedor


# Obtém o modelo de usuário ativo (accounts.Usuario)
Usuario = get_user_model()

# Separacao de telas por patente de usuario
def acesso_estoque(user):
    return user.is_authenticated and (user.role == 'ESTOQUE' or user.role == 'ADMINISTRADOR')

def acesso_vendas(user):
    return user.is_authenticated and (user.role == 'VENDEDOR' or user.role == 'ADMINISTRADOR')

def acesso_caixa(user):
    return user.is_authenticated and (user.role == 'CAIXA' or user.role == 'ADMINISTRADOR')

def acesso_compras(user):
    return user.is_authenticated and (user.role == 'COMPRAS' or user.role == 'ADMINISTRADOR')


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
        form = UsuarioCadastroForm(request.POST)
        
        if form.is_valid():
            form.save() 
            messages.success(request, 'Funcionário cadastrado com sucesso!')
            return redirect('app:login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erro no campo '{field}': {error}")
    else:
        form = UsuarioCadastroForm()

    return render(request, 'cadastro.html', {'form': form})

def cadastro_fornecedor_view(request):
    if request.method == 'POST':
        form = FornecedorCadastro(request.POST)
    
        if form.is_valid():
            form.save()
            messages.success(request, 'Fornecedor cadastrado com sucesso!') # Corrigido 'menssages' para 'messages'
            return redirect('app:compras')
        else:
            for field, errors in form.errors.items(): # Corrigido 'fields', 'erros.item()' para 'field', 'errors.items()'
                for error in errors:
                    messages.error(request, f"Erro no campo '{field}': {error}")
    else:
        form = FornecedorCadastro()

def listar_usuarios_view(request):
    return render(request, 'listar.html')


def editar_usuario_view(request, id=None):
    return render(request, 'editar.html')


def deletar_usuario_view(request, id=None):
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
    lista_de_fornecedores = Fornecedor.objects.all()

    context = {
        'fornecedor': lista_de_fornecedores
    }

    return render(request, 'compras.html', context)

    