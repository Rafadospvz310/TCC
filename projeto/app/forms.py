from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import transaction
from datetime import datetime
from .models import Fornecedor, Produto, Categoria, Cliente, Venda, ItemVenda

Usuario = get_user_model()

class UsuarioCadastroForm(forms.ModelForm):
    senha = forms.CharField(widget=forms.PasswordInput)
    nome = forms.CharField(max_length=150)

    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.first_name = self.cleaned_data['nome']
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

        if not CNPJ:
            return CNPJ

        CNPJ_limpo = ''.join(filter(str.isdigit, str(CNPJ)))

        if len(CNPJ_limpo) != 14:
            raise ValidationError("O CNPJ deve conter exatamente 14 números.")

        if CNPJ_limpo in [str(i) * 14 for i in range(10)]:
            raise ValidationError("CNPJ inválido (sequência repetida).")

        pesos_primeiro = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        pesos_segundo  = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

        cnpj_base = CNPJ_limpo[:12]

        soma_1 = sum(int(cnpj_base[i]) * pesos_primeiro[i] for i in range(12))
        resto_1 = soma_1 % 11
        digito_1 = str(0 if resto_1 < 2 else 11 - resto_1)
        cnpj_base += digito_1

        soma_2 = sum(int(cnpj_base[i]) * pesos_segundo[i] for i in range(13))
        resto_2 = soma_2 % 11
        digito_2 = str(0 if resto_2 < 2 else 11 - resto_2)
        cnpj_calculado = cnpj_base + digito_2

        if CNPJ_limpo != cnpj_calculado:
            raise ValidationError("CNPJ inválido. Os dígitos verificadores não conferem com a Receita Federal.")

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

class TributacaoImpostosForm(forms.Form):
    produto_id = forms.IntegerField()
    calc_custo = forms.FloatField(required=False, initial=0)
    calc_frete = forms.FloatField(required=False, initial=0)
    calc_ipi = forms.FloatField(required=False, initial=0)
    calc_icms = forms.FloatField(required=False, initial=0)
    calc_pis = forms.FloatField(required=False, initial=0)
    calc_cofins = forms.FloatField(required=False, initial=0)
    calc_iss = forms.FloatField(required=False, initial=0)
    calc_markup = forms.FloatField(required=False, initial=0)

    def processar_calculo(self, produto):
        custo = float(self.cleaned_data.get('calc_custo') or 0)
        frete = float(self.cleaned_data.get('calc_frete') or 0)
        ipi = float(self.cleaned_data.get('calc_ipi') or 0)
        icms = float(self.cleaned_data.get('calc_icms') or 0)
        pis = float(self.cleaned_data.get('calc_pis') or 0)
        cofins = float(self.cleaned_data.get('calc_cofins') or 0)
        iss = float(self.cleaned_data.get('calc_iss') or 0)
        markup = float(self.cleaned_data.get('calc_markup') or 0)
        
        # Legislação Brasileira: Custo Efetivo + Tributação "por dentro"
        custo_efetivo = custo + frete + (custo * (ipi / 100))
        total_impostos = (icms + pis + cofins + iss) / 100
        if total_impostos >= 1:
            total_impostos = 0.99
        
        preco_base_tributado = custo_efetivo / (1 - total_impostos)
        preco_final = preco_base_tributado * (1 + (markup / 100))
        
        # Salva os novos valores no banco de dados
        produto.preco_custo = custo
        produto.preco_venda = round(preco_final, 2)
        produto.save()
        return produto

class FinalizarVendaForm(forms.Form):
    forma_pagamento = forms.CharField()
    valor_recebido = forms.FloatField(required=False)

    def efetivar_venda(self, request, carrinho, total_compra):
        forma_pagamento = self.cleaned_data.get('forma_pagamento')
        
        with transaction.atomic():
            # Cria a venda com os campos corretos agora suportados pelo modelo
            venda = Venda.objects.create(
                vendedor=request.user if request.user.is_authenticated else None,
                valor_total=total_compra,
                forma_pagamento=forma_pagamento
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
                
        return venda

class RelatorioVendasForm(forms.Form):
    data_1 = forms.CharField(required=False)
    data_2 = forms.CharField(required=False)

    def processar_relatorio(self):
        data_1_str = self.cleaned_data.get('data_1')
        data_2_str = self.cleaned_data.get('data_2')
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

        return data_1_str, data_2_str, total_dia_1, total_dia_2, diferenca_valor, percentual_crescimento