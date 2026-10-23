import sys
import unittest
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import regras  # noqa: E402
from regras import DATA_REF_PADRAO, calcular_inadimplencia  # noqa: E402

REF = datetime(2026, 9, 25)


def parcela(dias=10, **campos):
    """Uma parcela ativa, aberta, mensal, vencida há `dias` dias."""
    base = {
        "EMPREENDIMENTO": "Edifício Parque Azul",
        "NUM_CONTRATO": "1",
        "UNIDADE": "A1",
        "CLIENTE": "Fulano",
        "TELEFONE": "000",
        "TIPO_PARCELA": "MENSAL",
        "NUM_PARCELA": "1",
        "NUM_ACORDO": "",
        "STATUS_PARCELA": "ABERTA",
        "SITUACAO_CONTRATO": "ATIVO",
        "DT_VENCIMENTO": REF - timedelta(days=dias),
        "VALOR_PARCELA": Decimal("1000.00"),
        "VALOR_PAGO": Decimal("0.00"),
    }
    base.update(campos)
    return base


def calcular(*linhas, data_ref=DATA_REF_PADRAO):
    return calcular_inadimplencia(pd.DataFrame(list(linhas)), data_ref)


def linha(resultado, i=0):
    return resultado["parcelas"].iloc[i]


class TestRegras(unittest.TestCase):
    def test_data_ref_padrao_e_a_do_arquivo(self):
        self.assertEqual(DATA_REF_PADRAO, date(2026, 9, 25))

    def test_parcela_paga_fica_fora(self):
        p = linha(calcular(parcela(60, STATUS_PARCELA="PAGA", VALOR_PAGO=Decimal("1000.00"))))
        self.assertFalse(p["INADIMPLENTE"])
        self.assertEqual(p["MOTIVO"], regras.FORA_PAGA)

    def test_aberta_futura_fica_fora(self):
        p = linha(calcular(parcela(-10)))
        self.assertFalse(p["INADIMPLENTE"])
        self.assertEqual(p["MOTIVO"], regras.FORA_A_VENCER)

    def test_aberta_vencida_e_inadimplente_com_saldo_cheio(self):
        p = linha(calcular(parcela(45)))
        self.assertTrue(p["INADIMPLENTE"])
        self.assertEqual(p["DIAS_ATRASO"], 45)
        self.assertEqual(p["SALDO"], Decimal("1000.00"))
        self.assertEqual(p["FAIXA_ATRASO"], "31-60")

    def test_pagamento_parcial_usa_o_saldo(self):
        r = calcular(parcela(45, VALOR_PARCELA=Decimal("6117.65"), VALOR_PAGO=Decimal("2420.63")))
        self.assertEqual(linha(r)["SALDO"], Decimal("3697.02"))
        self.assertEqual(r["resumo"]["inadimplente"]["saldo"], Decimal("3697.02"))

    def test_saldo_continua_decimal(self):
        p = linha(calcular(parcela(45, VALOR_PAGO=Decimal("0.10"))))
        self.assertIsInstance(p["SALDO"], Decimal)
        self.assertEqual(p["SALDO"], Decimal("999.90"))

    def test_contrato_distratado_fica_fora_e_aparece_a_parte(self):
        r = calcular(parcela(45, SITUACAO_CONTRATO="DISTRATADO"))
        self.assertEqual(linha(r)["MOTIVO"], regras.FORA_NAO_ATIVO)
        self.assertEqual(r["resumo"]["inadimplente"]["parcelas"], 0)
        self.assertEqual(r["resumo"]["distratados"], {"parcelas": 1, "saldo": Decimal("1000.00")})

    def test_contrato_quitado_fica_fora_e_aparece_a_parte(self):
        r = calcular(parcela(45, SITUACAO_CONTRATO="QUITADO"))
        self.assertEqual(r["resumo"]["inadimplente"]["parcelas"], 0)
        self.assertEqual(r["resumo"]["quitados"]["parcelas"], 1)

    def test_financiamento_fica_fora_e_aparece_a_parte(self):
        r = calcular(parcela(45, TIPO_PARCELA="FINANCIAMENTO"))
        self.assertEqual(linha(r)["MOTIVO"], regras.FORA_FINANCIAMENTO)
        self.assertEqual(r["resumo"]["financiamento"]["parcelas"], 1)

    def test_parcela_original_de_acordo_fica_fora_e_a_do_acordo_conta(self):
        r = calcular(
            parcela(100, NUM_PARCELA="1", NUM_ACORDO="7", VALOR_PARCELA=Decimal("500.00")),
            parcela(50, NUM_PARCELA="2", TIPO_PARCELA="ACORDO", NUM_ACORDO="7",
                    VALOR_PARCELA=Decimal("300.00")),
        )
        self.assertEqual(linha(r, 0)["MOTIVO"], regras.FORA_ACORDO_ORIGINAL)
        self.assertTrue(linha(r, 1)["INADIMPLENTE"])
        self.assertEqual(r["resumo"]["inadimplente"], {"parcelas": 1, "saldo": Decimal("300.00")})
        self.assertEqual(r["resumo"]["acordo_original"], {"parcelas": 1, "saldo": Decimal("500.00")})

    def test_fronteira_vence_na_data_de_referencia_nao_e_inadimplente(self):
        p = linha(calcular(parcela(0)))
        self.assertEqual(p["DIAS_ATRASO"], 0)
        self.assertFalse(p["INADIMPLENTE"])
        self.assertEqual(p["MOTIVO"], regras.FORA_A_VENCER)

    def test_fronteira_dia_anterior_esta_em_compensacao(self):
        r = calcular(parcela(1))
        self.assertEqual(linha(r)["MOTIVO"], regras.EM_COMPENSACAO)
        self.assertEqual(r["resumo"]["em_compensacao"]["parcelas"], 1)
        self.assertEqual(r["resumo"]["inadimplente"]["parcelas"], 0)

    def test_fronteira_carencia_3_dias_fora_e_4_dias_dentro(self):
        self.assertEqual(linha(calcular(parcela(3)))["MOTIVO"], regras.EM_COMPENSACAO)
        p4 = linha(calcular(parcela(4)))
        self.assertTrue(p4["INADIMPLENTE"])
        self.assertEqual(p4["FAIXA_ATRASO"], "4-30")

    def test_fronteiras_das_faixas(self):
        esperado = {
            4: "4-30", 30: "4-30", 31: "31-60", 60: "31-60", 61: "61-90",
            90: "61-90", 91: "91-180", 180: "91-180", 181: ">180",
        }
        for dias, faixa in esperado.items():
            with self.subTest(dias=dias):
                self.assertEqual(linha(calcular(parcela(dias)))["FAIXA_ATRASO"], faixa)

    def test_faixa_so_para_inadimplentes(self):
        r = calcular(parcela(2), parcela(-5), parcela(50, STATUS_PARCELA="PAGA"))
        self.assertTrue(r["parcelas"]["FAIXA_ATRASO"].isna().all())

    def test_motivo_de_maior_prioridade_prevalece(self):
        p = linha(calcular(parcela(45, SITUACAO_CONTRATO="DISTRATADO", TIPO_PARCELA="FINANCIAMENTO")))
        self.assertEqual(p["MOTIVO"], regras.FORA_NAO_ATIVO)

    def test_agregacoes_por_contrato_e_empreendimento(self):
        r = calcular(
            parcela(10, NUM_PARCELA="1"),
            parcela(100, NUM_PARCELA="2", VALOR_PARCELA=Decimal("250.00")),
            parcela(10, NUM_CONTRATO="2", EMPREENDIMENTO="Loteamento Vista do Horto"),
        )
        c = r["por_contrato"].set_index("NUM_CONTRATO")
        self.assertEqual(c.loc["1", "PARCELAS"], 2)
        self.assertEqual(c.loc["1", "SALDO_TOTAL"], Decimal("1250.00"))
        self.assertEqual(c.loc["1", "MAIOR_ATRASO"], 100)
        e = r["por_empreendimento"].set_index("EMPREENDIMENTO")
        self.assertEqual(e.loc["Edifício Parque Azul", "CONTRATOS"], 1)
        self.assertEqual(e.loc["Loteamento Vista do Horto", "SALDO_TOTAL"], Decimal("1000.00"))

    def test_nao_altera_o_dataframe_recebido(self):
        df = pd.DataFrame([parcela(45)])
        antes = df.copy()
        calcular_inadimplencia(df)
        pd.testing.assert_frame_equal(df, antes)

    def test_data_ref_diferente_muda_os_dias(self):
        r = calcular(parcela(10), data_ref=date(2026, 9, 30))
        self.assertEqual(linha(r)["DIAS_ATRASO"], 15)


if __name__ == "__main__":
    unittest.main()
