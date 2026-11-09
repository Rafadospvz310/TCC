from datetime import datetime, timedelta
from django.test import TestCase
from decimal import Decimal
from django.utils import timezone
from .forms import TributacaoImpostosForm
from .models import Produto, Fornecedor, Categoria
from .models import Venda
from .forms import RelatorioVendasForm


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

        # 1. Criamos os registros normalmente
        self.venda_dinheiro = Venda.objects.create(
            valor_total=Decimal('150.00'),
            forma_pagamento='Dinheiro'
        )
        
        self.venda_pix = Venda.objects.create(
            valor_total=Decimal('350.00'),
            forma_pagamento='PIX'
        )
        
        self.venda_ontem = Venda.objects.create(
            valor_total=Decimal('500.00'),
            forma_pagamento='Dinheiro'
        )

        Venda.objects.filter(id=self.venda_dinheiro.id).update(data_venda=timezone.now())
        Venda.objects.filter(id=self.venda_pix.id).update(data_venda=timezone.now())
        Venda.objects.filter(id=self.venda_ontem.id).update(data_venda=timezone.now() - timedelta(days=1))

        self.venda_dinheiro.refresh_from_db()
        self.venda_pix.refresh_from_db()
        self.venda_ontem.refresh_from_db()


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

class RelatorioComparacaoVendasTest(TestCase):
    """
    Testes de integração para a Comparação de Vendas entre dois dias (data_1 e data_2).
    Valida as somas financeiras, a diferença monetária e o percentual de crescimento.
    """

    def setUp(self):
        # ==========================================
        # 1. ARRANGE (Preparação do ambiente)
        # ==========================================
        
        # DIA 1: Vamos simular 2 vendas totalizando R$ 200,00
        self.data_1_str = '2026-11-01'
        data_1_obj = datetime.strptime(self.data_1_str, '%Y-%m-%d')
        
        self.v1 = Venda.objects.create(valor_total=Decimal('150.00'), forma_pagamento='PIX')
        self.v2 = Venda.objects.create(valor_total=Decimal('50.00'), forma_pagamento='Dinheiro')

        self.data_2_str = '2026-11-02'
        data_2_obj = datetime.strptime(self.data_2_str, '%Y-%m-%d')

        self.v3 = Venda.objects.create(valor_total=Decimal('300.00'), forma_pagamento='Dinheiro')

        Venda.objects.filter(id=self.v1.id).update(data_venda=data_1_obj)
        Venda.objects.filter(id=self.v2.id).update(data_venda=data_1_obj)
        Venda.objects.filter(id=self.v3.id).update(data_venda=data_2_obj)

    def test_deve_calcular_diferenca_e_percentual_de_crescimento_entre_dois_dias(self):

        form = RelatorioVendasForm(data={'data_1': self.data_1_str, 'data_2': self.data_2_str})
        self.assertTrue(form.is_valid())
        

        d1, d2, total_d1, total_d2, diferenca, percentual = form.processar_relatorio()

        self.assertEqual(total_d1, 200.00) 
        self.assertEqual(total_d2, 300.00) 

        self.assertEqual(diferenca, 100.00)

        self.assertEqual(percentual, 50.00)

    def test_deve_evitar_erro_de_divisao_por_zero_se_dia_anterior_nao_tiver_vendas(self):
        """
        Garante que o sistema não trave com ZeroDivisionError ao comparar
        um dia normal de vendas com um dia em que a loja esteve fechada (R$ 0).
        """
        # ARRANGE: '2026-11-10' é um dia vazio no nosso banco de teste
        data_vazia = '2026-11-10'
        form = RelatorioVendasForm(data={'data_1': data_vazia, 'data_2': self.data_2_str})
        self.assertTrue(form.is_valid())

        d1, d2, total_vazio, total_d2, diferenca, percentual = form.processar_relatorio()

        # ASSERT
        self.assertEqual(total_vazio, 0.0)
        self.assertEqual(total_d2, 300.00)
        self.assertEqual(diferenca, 300.00)
        
        # A sua lógica no Form salva o sistema garantindo 100% de crescimento direto
        self.assertEqual(percentual, 100.00)