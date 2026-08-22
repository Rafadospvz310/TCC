from django.shortcuts import render

def login_view(request):
    return render(request, 'index.html')

def cadastro_view(request):
    return render(request, 'cadastro.html')

def dashboard_view(request):
    return render(request, 'dashboard_admin.html')
