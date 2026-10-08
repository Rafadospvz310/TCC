from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from .forms import UsuarioCadastroForm, FornecedorCadastro, ProdutoCadastro
from .models import Fornecedor, Produto, Categoria, Cliente, Venda, ItemVenda
from django.db.models import Sum, F, Q


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
            messages.success(request, 'Fornecedor cadastrado com sucesso!')
            return redirect('app:painel') # <-- Volta para o painel com sucesso
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    # Cria a mensagem de erro vermelha
                    messages.error(request, f"Erro no campo '{field}': {error}")
            
            # <-- CRUCIAL: Mesmo dando erro, volta para o painel para mostrar as mensagens!
            return redirect('app:painel') 
            
    else:
        form = FornecedorCadastro()
        # Se alguém tentar acessar a URL diretamente sem enviar dados, manda de volta pro painel
        return redirect('app:painel')

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
    # Busca todos os produtos gravados no MySQL ordenados pelos mais recentes
    produtos = Produto.objects.all().order_by('-id')

    # Métricas gerais dos cards de resumo
    total_tipos = produtos.count()
    total_unidades = produtos.aggregate(Sum('quantidade'))['quantidade__sum'] or 0
    
    # Calcula o valor total em estoque (preco_custo * quantidade)
    valor_total = sum(p.preco_custo * p.quantidade for p in produtos)

    context = {
        'produtos': produtos,
        'total_tipos': total_tipos,
        'total_unidades': total_unidades,
        'valor_total': valor_total,
        'nome_usuario': request.user.first_name or request.user.username,
    }
    return render(request, 'estoque_controle.html', context)


@user_passes_test(acesso_estoque)
def detalhes_item_view(request, produto_id=None):
    produto = None
    
    codigo_interno = request.GET.get('codigo_interno', '').strip()
    codigo_barras = request.GET.get('codigo_barras', '').strip()

    if produto_id:
        produto = get_object_or_404(Produto, id=produto_id)
        
    elif codigo_interno:
        busca_id = codigo_interno.replace('#', '')
        if busca_id.isdigit():
            produto = Produto.objects.filter(id=busca_id).first()
            
    elif codigo_barras:
        produto = Produto.objects.filter(codigo_barras=codigo_barras).first()

    context = {
        'produto': produto,
        'codigo_interno_digitado': codigo_interno,
        'codigo_barras_digitado': codigo_barras,
        'nome_usuario': request.user.first_name or request.user.username,
    }
    
    return render(request, 'estoque_item.html', context)

@user_passes_test(acesso_estoque)
def deletar_produto_view(request, produto_id):
    if request.method == 'POST':
        produto = get_object_or_404(Produto, id=produto_id)
        nome_produto = produto.nome
        produto.delete()
        messages.success(request, f'Produto "{nome_produto}" removido com sucesso!')
    return redirect('app:controle')

@user_passes_test(acesso_estoque)
def consultar_item_view(request, produto_id=None):
    produto = None
    
    # Em vez de 'q', nós capturamos os dois campos do HTML
    codigo_interno = request.GET.get('codigo_interno', '').strip()
    codigo_barras = request.GET.get('codigo_barras', '').strip()

    # 1. Mantém a sua lógica original: Se vier um ID direto pela URL
    if produto_id:
        produto = get_object_or_404(Produto, id=produto_id)
        
    # 2. Se o usuário digitou no campo de Código Numérico Interno
    elif codigo_interno:
        busca_id = codigo_interno.replace('#', '') # Remove a '#' se ele digitar
        if busca_id.isdigit():
            produto = Produto.objects.filter(id=busca_id).first()
            
    # 3. Se o usuário digitou no campo de Código de Barras
    elif codigo_barras:
        produto = Produto.objects.filter(codigo_barras=codigo_barras).first()

    context = {
        'produto': produto,
        # Devolvemos o que foi digitado para o campo não ficar em branco caso dê erro
        'codigo_interno_digitado': codigo_interno,
        'codigo_barras_digitado': codigo_barras,
        'nome_usuario': request.user.first_name or request.user.username,
    }
    
    return render(request, 'estoque_item.html', context)

@user_passes_test(acesso_estoque)
def etiquetas_view(request):
    return render(request, 'estoque_etiquetas.html')

@user_passes_test(acesso_estoque)
def gerar_etiquetas_view(request):
    # Consulta direta sem filtros para garantir que traz a QuerySet
    todos_produtos = Produto.objects.all().order_by('-id')

    produto = None
    produto_id = request.GET.get('produto_id') or request.POST.get('produto_id')
    busca = request.GET.get('busca_etiqueta', '').strip()
    qtd_etiquetas = int(request.POST.get('qtd_etiquetas', 1)) if request.method == 'POST' else 1

    # Se houve filtro por texto
    if busca:
        if busca.isdigit():
            todos_produtos = Produto.objects.filter(
                Q(id=busca) | Q(codigo_barras=busca) | Q(nome__icontains=busca)
            ).order_by('-id')
        else:
            todos_produtos = Produto.objects.filter(
                Q(nome__icontains=busca) | Q(codigo_barras__icontains=busca)
            ).order_by('-id')

    # Seleção do produto
    if produto_id:
        produto = Produto.objects.filter(id=produto_id).first()
    elif todos_produtos.exists():
        produto = todos_produtos.first()

    imprimir = False
    if request.method == 'POST' and 'imprimir' in request.POST:
        imprimir = True

    context = {
        'todos_produtos': todos_produtos,
        'produto': produto,
        'busca': busca,
        'qtd_etiquetas': qtd_etiquetas,
        'imprimir': imprimir,
        'nome_usuario': request.user.first_name or request.user.username,
    }
    return render(request, 'estoque_etiquetas.html', context)

@user_passes_test(acesso_vendas)
def nova_venda_view(request):
    busca_produto = request.GET.get('busca_produto', '').strip()
    produto = None

    if busca_produto:
        # 1. Se o que o usuário digitou for apenas números (Pode ser ID ou Código de Barras)
        if busca_produto.isdigit():
            produto = Produto.objects.filter(
                Q(id=busca_produto) | Q(codigo_barras=busca_produto)
            ).first()
        
        # 2. Se não achou por número, ou se o usuário digitou letras (ex: "Martelo"), busca por Nome
        if not produto:
            produto = Produto.objects.filter(nome__icontains=busca_produto).first()

    context = {
        'produto': produto,
        'busca_digitada': busca_produto,
        'nome_usuario': request.user.first_name if request.user.is_authenticated else "Vendedor"
    }
    
    return render(request, 'vendas_vendedor.html', context)


@user_passes_test(acesso_caixa)
def caixa_pdv_view(request):
    return render(request, 'vendas_caixa.html')


@user_passes_test(acesso_caixa)
def relatorio_vendas_view(request):
    return render(request, 'caixa_relatorio.html')


@user_passes_test(acesso_compras)
def painel_compras_view(request):
    if request.method == 'POST':
        # Identifica se a requisição veio do formulário de Produto ou de Fornecedor
        if 'nome_produto' in request.POST:
            # Mapeia os inputs do HTML para o formulário do Django
            dados_produto = {
                'nome': request.POST.get('nome_produto'),
                'fornecedor': request.POST.get('fornecedor_id'),
                'categoria': request.POST.get('categoria'),
                'codigo_barras': request.POST.get('codigo_barras'),
                'preco_custo': request.POST.get('preco_custo'),
                'quantidade': request.POST.get('quantidade'),
            }
            form_produto = ProdutoCadastro(dados_produto, request.FILES)
            if form_produto.is_valid():
                form_produto.save()
                messages.success(request, 'Produto adicionado ao estoque com sucesso!')
            else:
                for field, errors in form_produto.errors.items():
                    for error in errors:
                        messages.error(request, f"Erro no campo '{field}': {error}")
            return redirect('app:painel')

        elif 'nome' in request.POST:
            form_fornecedor = FornecedorCadastro(request.POST)
            if form_fornecedor.is_valid():
                form_fornecedor.save()
                messages.success(request, 'Fornecedor cadastrado com sucesso!')
            else:
                for field, errors in form_fornecedor.errors.items():
                    for error in errors:
                        messages.error(request, f"Erro no campo '{field}': {error}")
            return redirect('app:painel')

    # Busca a lista de fornecedores cadastrados para popular os selects do HTML
    lista_de_fornecedores = Fornecedor.objects.all().order_by('nome')

    context = {
        'fornecedores': lista_de_fornecedores,
        'nome_usuario': request.user.first_name or request.user.username,
    }

    return render(request, 'compras.html', context)

    