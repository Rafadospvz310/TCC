from django.test import TestCase
from decimal import Decimal
from .forms import TributacaoImpostosForm
from .models import Produto, Fornecedor, Categoria

class TributacaoImpostosFormTest(TestCase):

    def setUp(self):
        self.fornecedor = Fornecedor.objects.create(
            nome="Distribuidora de Ferragens S/A", 
            CNPJ="12345678000199"
        )
        
        # Produto inicial antes de aplicar a nova tributação
        self.produto = Produto.objects.create(
            nome="Parafuso Sextavado",
            codigo_barras="7891234567890",
            preco_custo=Decimal('10.00'),
            preco_venda=Decimal('15.00'),
            quantidade=100,
            fornecedor=self.fornecedor,
            categoria="Ferragens"
        )

    def test_calculo_tributacao_completo_e_salvamento(self):
        """
        Testa o cálculo completo com frete, IPI, ICMS, PIS, COFINS e Markup,
        verificando se o preço final é gravado corretamente no banco.
        """
        payload = {
            'produto_id': self.produto.id,
            'calc_custo': 100.0,
            'calc_frete': 10.0,
            'calc_ipi': 10.0,
            'calc_icms': 18.0,
            'calc_pis': 1.65,
            'calc_cofins': 7.6,
            'calc_iss': 0.0,   
            'calc_markup': 20.0
        }

        form = TributacaoImpostosForm(data=payload)
        self.assertTrue(form.is_valid())

        # Executa o processamento transferido para o form
        produto_atualizado = form.processar_calculo(self.produto)

        # Validações dos valores retornados pela função
        self.assertEqual(float(produto_atualizado.preco_custo), 100.0)
        self.assertEqual(float(produto_atualizado.preco_venda), 197.94)

        # Recarrega o produto do banco para confirmar a gravação física (save)
        self.produto.refresh_from_db()
        self.assertEqual(float(self.produto.preco_venda), 197.94)

    def test_trava_seguranca_impostos_maior_ou_igual_100_percento(self):
        """
        Garante que a condição 'if total_impostos >= 1: total_impostos = 0.99' 
        evita erro de divisão por zero.
        """
        payload = {
            'produto_id': self.produto.id,
            'calc_custo': 100.0,
            'calc_icms': 50.0,
            'calc_pis': 50.0, # Soma 100% -> O form deve travar em 99%
            'calc_markup': 0.0
        }

        form = TributacaoImpostosForm(data=payload)
        self.assertTrue(form.is_valid())

        produto_atualizado = form.processar_calculo(self.produto)
        # Custo Efetivo: 100 / (1 - 0.99) = 10000.0
        self.assertEqual(float(produto_atualizado.preco_venda), 10000.0)

    def test_processamento_com_campos_opcionais_vazios(self):
        """
        Testa a execução enviando apenas os campos obrigatórios (produto_id).
        """
        payload = {'produto_id': self.produto.id}

        form = TributacaoImpostosForm(data=payload)
        self.assertTrue(form.is_valid())

        produto_atualizado = form.processar_calculo(self.produto)
        self.assertEqual(float(produto_atualizado.preco_custo), 0.0)
        self.assertEqual(float(produto_atualizado.preco_venda), 0.0)
