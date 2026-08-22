from django.shortcuts import render

def nova_venda(request):
    return render(request, 'vendas_vendedor.html')

def pdv_caixa(request):
    return render(request, 'vendas_caixa.html')

def relatorio_caixa(request):
    return render(request, 'caixa_relatorio.html')
