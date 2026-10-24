from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from .forms import UsuarioCadastroForm, FornecedorCadastro, ProdutoCadastro
from .models import Fornecedor, Produto, Categoria, Cliente, Venda, ItemVenda
from django.db.models import Sum, F, Q
from django.utils import timezone
from datetime import datetime

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
            return redirect('app:painel')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erro no campo '{field}': {error}")
            return redirect('app:painel') 
    else:
        form = FornecedorCadastro()
        return redirect('app:painel')


def listar_usuarios_view(request):
    return render(request, 'listar.html')


def editar_usuario_view(request, id=None):
    return render(request, 'editar.html')


def deletar_usuario_view(request, id=None):
    return render(request, 'confirmar_delecao.html')


@login_required
def dashboard_admin_view(request):
    # Atualização do orçamento mensal via formulário POST
    if request.method == 'POST' and 'novo_orcamento' in request.POST:
        try:
            novo_orcamento = float(request.POST.get('novo_orcamento', 0))
            request.session['orcamento_mensal'] = novo_orcamento
            messages.success(request, 'Orçamento mensal atualizado com sucesso!')
        except ValueError:
            messages.error(request, 'Valor inválido para o orçamento.')
        return redirect('app:dashboard')

    # Recupera o orçamento da sessão (padrão: R$ 10.000,00)
    orcamento_definido = request.session.get('orcamento_mensal', 10000.00)

    # Considera produtos com estoque baixo (<= 10 unidades)
    LIMITE_ESTOQUE_BAIXO = 10
    produtos_para_comprar = Produto.objects.filter(quantidade__lte=LIMITE_ESTOQUE_BAIXO).order_by('quantidade')

    # Cálculo da necessidade de compra para repor estoque até 20 unidades
    ESTOQUE_DESEJADO = 20
    total_necessidade_compra = sum(
        (ESTOQUE_DESEJADO - p.quantidade) * float(p.preco_custo or 0) 
        for p in produtos_para_comprar if p.quantidade < ESTOQUE_DESEJADO
    )

    saldo_disponivel = orcamento_definido - total_necessidade_compra

    context = {
        'orcamento_definido': orcamento_definido,
        'total_gasto': total_necessidade_compra,
        'saldo_disponivel': saldo_disponivel,
        'produtos_necessidade': produtos_para_comprar,
        'nome_usuario': request.user.first_name or request.user.username,
    }
    return render(request, 'dashboard_admin.html', context)


@user_passes_test(acesso_estoque)
def controle_estoque_view(request):
    busca = request.GET.get('busca', '').strip()
    
    if busca:
        produtos = Produto.objects.filter(
            Q(nome__icontains=busca) | Q(codigo_barras__icontains=busca) | Q(id__icontains=busca)
        ).order_by('-id')
    else:
        produtos = Produto.objects.all().order_by('-id')

    # Cálculos para os cards superiores
    total_tipos = Produto.objects.count()
    total_itens_fisicos = Produto.objects.aggregate(total=Sum('quantidade'))['total'] or 0
    valor_total_estoque = Produto.objects.aggregate(
        total=Sum(F('preco_custo') * F('quantidade'))
    )['total'] or 0.0

    context = {
        'produtos': produtos,
        'busca': busca,
        'total_tipos': total_tipos,
        'total_itens_fisicos': total_itens_fisicos,
        'valor_total_estoque': valor_total_estoque,
        'nome_usuario': request.user.first_name or request.user.username,
    }
    return render(request, 'estoque_controle.html', context)


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
def etiquetas_view(request):
    return redirect('app:gerar_etiquetas')


@user_passes_test(acesso_estoque)
def gerar_etiquetas_view(request):
    todos_produtos = Produto.objects.all().order_by('-id')

    produto = None
    produto_id = request.GET.get('produto_id') or request.POST.get('produto_id')
    busca = request.GET.get('busca_etiqueta', '').strip()
    qtd_etiquetas = int(request.POST.get('qtd_etiquetas', 1)) if request.method == 'POST' else 1

    if busca:
        if busca.isdigit():
            todos_produtos = Produto.objects.filter(
                Q(id=busca) | Q(codigo_barras=busca) | Q(nome__icontains=busca)
            ).order_by('-id')
        else:
            todos_produtos = Produto.objects.filter(
                Q(nome__icontains=busca) | Q(codigo_barras__icontains=busca)
            ).order_by('-id')

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
        if busca_produto.isdigit():
            produto = Produto.objects.filter(
                Q(id=busca_produto) | Q(codigo_barras=busca_produto)
            ).first()
        
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
    carrinho = request.session.get('carrinho', [])
    ultimo_item_nome = request.session.get('ultimo_item_nome', '---')
    ultimo_item_preco = request.session.get('ultimo_item_preco', 0.0)

    if request.method == 'POST':
        acao = request.POST.get('acao')

        # 1. Adicionar item lido pelo leitor
        if acao == 'adicionar':
            codigo_barras = request.POST.get('codigo_barras', '').strip()
            if codigo_barras:
                produto = None
                if codigo_barras.isdigit():
                    produto = Produto.objects.filter(
                        Q(codigo_barras=codigo_barras) | Q(id=codigo_barras)
                    ).first()
                if not produto:
                    produto = Produto.objects.filter(nome__icontains=codigo_barras).first()

                if produto:
                    if produto.quantidade > 0:
                        preco_item = float(produto.preco_custo or 0)
                        
                        # Verifica se o produto já existe no carrinho para apenas incrementar a quantidade
                        item_existente = next((item for item in carrinho if item['produto_id'] == produto.id), None)
                        if item_existente:
                            item_existente['quantidade'] += 1
                            item_existente['subtotal'] = item_existente['quantidade'] * preco_item
                        else:
                            carrinho.append({
                                'produto_id': produto.id,
                                'nome': produto.nome,
                                'preco': preco_item,
                                'quantidade': 1,
                                'subtotal': preco_item
                            })

                        request.session['carrinho'] = carrinho
                        request.session['ultimo_item_nome'] = produto.nome
                        request.session['ultimo_item_preco'] = preco_item
                        messages.success(request, f'Item "{produto.nome}" adicionado!')
                    else:
                        messages.error(request, f'Produto "{produto.nome}" está sem estoque!')
                else:
                    messages.error(request, 'Produto não encontrado.')

            return redirect('app:caixa')

        # 2. Limpar o carrinho inteiro
        elif acao == 'limpar':
            request.session['carrinho'] = []
            request.session['ultimo_item_nome'] = '---'
            request.session['ultimo_item_preco'] = 0.0
            messages.info(request, 'Carrinho esvaziado.')
            return redirect('app:caixa')

        # 3. Finalizar e dar baixa no estoque
        elif acao == 'finalizar':
            forma_pagamento = request.POST.get('forma_pagamento')
            valor_recebido = request.POST.get('valor_recebido')
            total_compra = sum(item['subtotal'] for item in carrinho)

            if not carrinho:
                messages.error(request, 'Não há itens na venda atual!')
                return redirect('app:caixa')

            if valor_recebido:
                try:
                    valor_recebido = float(valor_recebido)
                    if valor_recebido < total_compra:
                        messages.error(request, f'Valor recebido (R$ {valor_recebido:.2f}) é menor que o total da compra (R$ {total_compra:.2f})!')
                        return redirect('app:caixa')
                except ValueError:
                    pass

            try:
                with transaction.atomic():
                    venda = Venda.objects.create(
                        vendedor=request.user,
                        valor_total=total_compra
                    )

                    for item in carrinho:
                        prod = Produto.objects.get(id=item['produto_id'])
                        ItemVenda.objects.create(
                            venda=venda,
                            produto=prod,
                            quantidade=item['quantidade'],
                            preco_unitario=item['preco']
                        )
                        prod.quantidade -= item['quantidade']
                        prod.save()

                    request.session['carrinho'] = []
                    request.session['ultimo_item_nome'] = '---'
                    request.session['ultimo_item_preco'] = 0.0

                    troco = (float(valor_recebido) - total_compra) if valor_recebido else 0.0
                    if troco > 0:
                        messages.success(request, f'Venda #{venda.id} finalizada com sucesso! Troco: R$ {troco:.2f}')
                    else:
                        messages.success(request, f'Venda #{venda.id} finalizada com sucesso!')

            except Exception as e:
                messages.error(request, f'Erro ao registrar a venda: {str(e)}')

            return redirect('app:caixa')

    total_compra = sum(item['subtotal'] for item in carrinho)

    context = {
        'carrinho': carrinho,
        'total_compra': total_compra,
        'ultimo_item_nome': ultimo_item_nome,
        'ultimo_item_preco': ultimo_item_preco,
        'nome_usuario': request.user.first_name or request.user.username,
    }
    return render(request, 'vendas_caixa.html', context)


@user_passes_test(acesso_caixa)
def relatorio_vendas_view(request):
    if request.method == 'POST':
        messages.success(request, 'Turno do caixa encerrado e relatório gerado com sucesso!')
        return redirect('app:relatorio')

    hoje = timezone.now().date()
    
    # 1. Histórico de Vendas do dia atual
    vendas_hoje = Venda.objects.filter(data_venda__date=hoje).order_by('-data_venda') if hasattr(Venda, 'data_venda') else Venda.objects.all().order_by('-id')

    total_dinheiro = 0.0
    total_cartao_pix = 0.0

    for venda in vendas_hoje:
        valor = float(venda.valor_total or 0)
        forma = str(getattr(venda, 'forma_pagamento', '') or '').lower()
        if 'dinheiro' in forma:
            total_dinheiro += valor
        else:
            total_cartao_pix += valor

    total_geral = total_dinheiro + total_cartao_pix

    # 2. Lógica de Comparação entre dois dias
    data_1_str = request.GET.get('data_1', '')
    data_2_str = request.GET.get('data_2', '')
    total_dia_1 = 0.0
    total_dia_2 = 0.0
    diferenca_valor = 0.0
    percentual_crescimento = 0.0

    if data_1_str and data_2_str:
        try:
            d1 = datetime.strptime(data_1_str, '%Y-%m-%d').date()
            d2 = datetime.strptime(data_2_str, '%Y-%m-%d').date()

            # Soma das vendas do Dia 1
            vendas_d1 = Venda.objects.filter(data_venda__date=d1) if hasattr(Venda, 'data_venda') else []
            total_dia_1 = sum(float(v.valor_total or 0) for v in vendas_d1)

            # Soma das vendas do Dia 2
            vendas_d2 = Venda.objects.filter(data_venda__date=d2) if hasattr(Venda, 'data_venda') else []
            total_dia_2 = sum(float(v.valor_total or 0) for v in vendas_d2)

            diferenca_valor = total_dia_2 - total_dia_1
            
            if total_dia_1 > 0:
                percentual_crescimento = (diferenca_valor / total_dia_1) * 100
            elif total_dia_2 > 0:
                percentual_crescimento = 100.0
        except ValueError:
            pass

    context = {
        'vendas': vendas_hoje,
        'total_dinheiro': total_dinheiro,
        'total_cartao_pix': total_cartao_pix,
        'total_geral': total_geral,
        # Variáveis de comparação
        'data_1': data_1_str,
        'data_2': data_2_str,
        'total_dia_1': total_dia_1,
        'total_dia_2': total_dia_2,
        'diferenca_valor': diferenca_valor,
        'percentual_crescimento': percentual_crescimento,
        'nome_usuario': request.user.first_name or request.user.username,
    }
    return render(request, 'caixa_relatorio.html', context)


@user_passes_test(acesso_compras)
def painel_compras_view(request):
    if request.method == 'POST':
        if 'nome_produto' in request.POST:
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

    lista_de_fornecedores = Fornecedor.objects.all().order_by('nome')

    context = {
        'fornecedores': lista_de_fornecedores,
        'nome_usuario': request.user.first_name or request.user.username,
    }
    return render(request, 'compras.html', context)