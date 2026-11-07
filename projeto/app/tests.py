from datetime import timedelta

from django.test import TestCase
from decimal import Decimal
from django.utils import timezone
from .forms import TributacaoImpostosForm
from .models import Produto, Fornecedor, Categoria
from .models import Venda

class TributacaoImpostosFormTest(TestCase):

    def setUp(self):
        self.fornecedor = Fornecedor.objects.create(
            nome="Distribuidora de Ferragens S/A", 
            CNPJ="12345678000199"
        )
        
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

        produto_atualizado = form.processar_calculo(self.produto)

        self.assertEqual(float(produto_atualizado.preco_custo), 100.0)
        self.assertEqual(float(produto_atualizado.preco_venda), 197.94)

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
            'calc_pis': 50.0,
            'calc_markup': 0.0
        }

        form = TributacaoImpostosForm(data=payload)
        self.assertTrue(form.is_valid())

        produto_atualizado = form.processar_calculo(self.produto)
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


class RelatorioVendasCaixaTest(TestCase):
    """
    Testes de integração para o Relatório de Vendas (Fechamento de Caixa).
    """

    def setUp(self):
        self.hoje = timezone.now().date()

        self.venda_dinheiro = Venda.objects.create(
            valor_total=Decimal('150.00'),
            forma_pagamento='Dinheiro'
        )
        # Forçando a data para garantir precisão no teste
        self.venda_dinheiro.data_venda = timezone.now()
        self.venda_dinheiro.save()

        self.venda_pix = Venda.objects.create(
            valor_total=Decimal('350.00'),
            forma_pagamento='PIX'
        )
        self.venda_pix.data_venda = timezone.now()
        self.venda_pix.save()

        self.venda_ontem = Venda.objects.create(
            valor_total=Decimal('500.00'),
            forma_pagamento='Dinheiro'
        )

        self.venda_ontem.data_venda = timezone.now() - timedelta(days=1)
        self.venda_ontem.save()

    def test_deve_retornar_apenas_as_vendas_realizadas_no_dia_atual(self):
        vendas_hoje = Venda.objects.filter(data_venda__date=self.hoje)

        self.assertEqual(vendas_hoje.count(), 2)
        

        self.assertIn(self.venda_dinheiro, vendas_hoje)
        self.assertIn(self.venda_pix, vendas_hoje)
        
        self.assertNotIn(self.venda_ontem, vendas_hoje)

    def test_deve_separar_e_somar_totais_por_forma_de_pagamento(self):
        vendas_hoje = Venda.objects.filter(data_venda__date=self.hoje)
        
        total_dinheiro = 0.0
        total_cartao_pix = 0.0

        for venda in vendas_hoje:
            valor = float(venda.valor_total or 0)
            forma = str(getattr(venda, 'forma_pagamento', '') or '').lower()
            if 'dinheiro' in forma:
                total_dinheiro += valor
            else:
                total_cartao_pix += valor

        self.assertEqual(total_dinheiro, 150.00) 
        self.assertEqual(total_cartao_pix, 350.00)
        self.assertEqual(total_dinheiro + total_cartao_pix, 500.00)


