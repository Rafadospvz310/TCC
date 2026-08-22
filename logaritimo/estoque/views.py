from django.shortcuts import render

def controle_geral(request):
    # Retorna a tela principal do estoque
    return render(request, 'estoque_controle.html')

def consultar_item(request):
    # Retorna a tela de detalhes do item
    return render(request, 'estoque_item.html')

def gerar_etiquetas(request):
    # Retorna a tela de impressão de etiquetas
    return render(request, 'estoque_etiquetas.html')
