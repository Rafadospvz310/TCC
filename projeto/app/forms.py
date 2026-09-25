from django import forms
from django.contrib.auth import get_user_model
from .models import Fornecedor

# Vai buscar o seu modelo automaticamente, quer esteja na app 'accounts' ou 'app'
Usuario = get_user_model()

class UsuarioCadastroForm(forms.ModelForm):
    # Declaramos a senha e o nome para bater certo com o seu HTML
    senha = forms.CharField(widget=forms.PasswordInput)
    nome = forms.CharField(max_length=150)

    class Meta:
        model = Usuario
        # Os campos que o formulário vai esperar receber do HTML
        fields = ['nome', 'email', 'role']

    def save(self, commit=True):
        # Pausa a gravação para fazermos ajustes manuais de segurança
        user = super().save(commit=False)
        
        # O Django exige um 'username', por isso usamos o email para preencher esse buraco
        user.username = self.cleaned_data['email']
        user.first_name = self.cleaned_data['nome']
        
        # A função set_password aplica a encriptação na palavra-passe!
        user.set_password(self.cleaned_data['senha'])
        
        if commit:
            user.save()
        return user
class FornecedorCadastro(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = ['nome', 'CNPJ', 'telefone', 'email', 'categorias']