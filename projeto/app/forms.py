from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import Fornecedor, Produto, Categoria, Cliente, Venda, ItemVenda

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

        def clean_CNPJ(self):
            CNPJ = self.cleaned_data.get('CNPJ')

            # Se o campo for vazio, não faz validação aqui (deixa para o required=True do Django)
            if not CNPJ:
                return CNPJ

            # Passo 0: Limpar caracteres e verificar o tamanho básico
            CNPJ_limpo = ''.join(filter(str.isdigit, str(CNPJ)))

            if len(CNPJ_limpo) != 14:
                raise ValidationError("O CNPJ deve conter exatamente 14 números.")

            # Bloquear fraudes óbvias (14 números iguais repetidos)
            if CNPJ_limpo in [str(i) * 14 for i in range(10)]:
                raise ValidationError("CNPJ inválido (sequência repetida).")

            # Passo 1: Listas de pesos
            pesos_primeiro = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
            pesos_segundo  = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

            # Separar a base (os 12 primeiros números)
            cnpj_base = CNPJ_limpo[:12]

            # Passo 2: Calcular o Primeiro Dígito
            # Multiplicamos cada número da base pelo seu peso correspondente e somamos tudo
            soma_1 = sum(int(CNPJ_base[i]) * pesos_primeiro[i] for i in range(12))
            resto_1 = soma_1 % 11
            digito_1 = str(0 if resto_1 < 2 else 11 - resto_1)

            # Adicionamos o primeiro dígito calculado à nossa base
            CNPJ_base += digito_1

            # Passo 3: Calcular o Segundo Dígito (agora com 13 números)
            soma_2 = sum(int(cnpj_base[i]) * pesos_segundo[i] for i in range(13))
            resto_2 = soma_2 % 11
            digito_2 = str(0 if resto_2 < 2 else 11 - resto_2)

            # Juntamos o último dígito para ter os 14 números matematicamente perfeitos
            cnpj_calculado = cnpj_base + digito_2

            # Passo 4: O Veredicto
            if CNPJ_limpo != cnpj_calculado:
                raise ValidationError("CNPJ inválido. Os dígitos verificadores não conferem com a Receita Federal.")

            # Se passou por tudo sem dar erro, devolvemos o CNPJ limpo para ser salvo no MySQL
            return CNPJ_limpo

class ProdutoCadastro(forms.ModelForm):
    class Meta:
        model = Produto
        fields = [
            'nome', 
            'fornecedor', 
            'categoria', 
            'codigo_barras', 
            'preco_custo', 
            'quantidade', 
            'foto'
        ]