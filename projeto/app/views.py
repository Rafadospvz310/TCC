from django.shortcuts import render

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

def controle_estoque_view(request):
    return render(request, 'estoque_controle.html')

def detalhes_item_view(request):
    return render(request, 'estoque_item.html')

def etiquetas_view(request):
    return render(request, 'estoque_etiquetas.html')

def nova_venda_view(request):
    return render(request, 'vendas_vendedor.html')

def caixa_pdv_view(request):
    return render(request, 'vendas_caixa.html')

def relatorio_vendas_view(request):
    return render(request, 'caixa_relatorio.html')

def painel_compras_view(request):
    return render(request, 'compras.html')