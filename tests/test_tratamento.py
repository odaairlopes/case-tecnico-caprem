import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

import pandas as pd

from tratamento import (
    COLUNAS,
    carregar_dados,
    normalizar_dados,
    normalizar_empreendimento,
    relatorio_qualidade,
)


def linha_parcela(**alteracoes):
    linha = {
        "COLIGADA": "1",
        "EMPREENDIMENTO": "Edifício Parque Azul",
        "UNIDADE": "Apto 101",
        "NUM_CONTRATO": "1010403",
        "SITUACAO_CONTRATO": "ATIVO",
        "CLIENTE": "Cliente Teste",
        "CPF_CNPJ": "00000000000",
        "TELEFONE": "(00) 00000-0000",
        "TIPO_PARCELA": "MENSAL",
        "NUM_PARCELA": "1",
        "DT_VENCIMENTO": "15/04/2025",
        "VALOR_PARCELA": "3.625,00",
        "VALOR_PAGO": "1.234,56",
        "DT_PAGAMENTO": "15/04/2025",
        "STATUS_PARCELA": "Aberta",
        "NUM_ACORDO": "",
    }
    linha.update(alteracoes)
    return linha


class TestNormalizarDados(unittest.TestCase):
    def test_normaliza_valores_status_datas_e_mantem_precisao_monetaria(self):
        dados = pd.DataFrame(
            [
                linha_parcela(
                    EMPREENDIMENTO="LOTEAMENTO VISTA DO HORTO",
                    DT_VENCIMENTO="2026-04-10",
                    VALOR_PARCELA="2200.00",
                    VALOR_PAGO="0.00",
                    DT_PAGAMENTO="",
                    STATUS_PARCELA="Paga",
                ),
                linha_parcela(
                    NUM_CONTRATO="1010404",
                    VALOR_PARCELA="3.625,00",
                    VALOR_PAGO="1.234,56",
                ),
            ]
        )

        resultado = normalizar_dados(dados)
        parcela_iso = resultado.iloc[0]
        parcela_br = resultado.iloc[1]

        self.assertEqual(parcela_iso["STATUS_PARCELA"], "PAGA")
        self.assertEqual(parcela_iso["TIPO_PARCELA"], "MENSAL")
        self.assertEqual(parcela_iso["DT_VENCIMENTO"], pd.Timestamp("2026-04-10"))
        self.assertTrue(pd.isna(parcela_iso["DT_PAGAMENTO"]))
        self.assertEqual(parcela_iso["VALOR_PARCELA"], Decimal("2200.00"))
        self.assertEqual(parcela_iso["VALOR_PAGO"], Decimal("0.00"))
        self.assertEqual(parcela_br["VALOR_PARCELA"], Decimal("3625.00"))
        self.assertEqual(parcela_br["VALOR_PAGO"], Decimal("1234.56"))

    def test_remove_linhas_exatamente_duplicadas_e_informa_contagem(self):
        linha = linha_parcela()
        resultado = normalizar_dados(pd.DataFrame([linha, linha.copy()]))

        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado.attrs["duplicatas_removidas"], 1)

    def test_rejeita_coluna_ausente(self):
        dados = pd.DataFrame([linha_parcela()]).drop(columns="NUM_ACORDO")

        with self.assertRaisesRegex(ValueError, "colunas ausentes: NUM_ACORDO"):
            normalizar_dados(dados)

    def test_rejeita_data_invalida_com_linha_e_coluna(self):
        dados = pd.DataFrame([linha_parcela(DT_VENCIMENTO="31/02/2026")])

        with self.assertRaisesRegex(
            ValueError, r"Linha 2 do CSV, coluna DT_VENCIMENTO: data inválida"
        ):
            normalizar_dados(dados)

    def test_rejeita_valor_monetario_invalido(self):
        dados = pd.DataFrame([linha_parcela(VALOR_PAGO="1,2")])

        with self.assertRaisesRegex(
            ValueError, r"Linha 2 do CSV, coluna VALOR_PAGO: valor inválido"
        ):
            normalizar_dados(dados)

    def test_rejeita_status_desconhecido(self):
        dados = pd.DataFrame([linha_parcela(STATUS_PARCELA="PENDENTE")])

        with self.assertRaisesRegex(
            ValueError, r"Linha 2 do CSV, coluna STATUS_PARCELA"
        ):
            normalizar_dados(dados)

    def test_rejeita_campo_obrigatorio_vazio(self):
        dados = pd.DataFrame([linha_parcela(NUM_CONTRATO="")])

        with self.assertRaisesRegex(
            ValueError, r"Linha 2 do CSV, coluna NUM_CONTRATO: campo obrigatório vazio"
        ):
            normalizar_dados(dados)

    def test_le_csv_com_bom_e_separador_ponto_e_virgula(self):
        linha = linha_parcela()
        conteudo = ";".join(COLUNAS) + "\n"
        conteudo += ";".join(linha[coluna] for coluna in COLUNAS) + "\n"

        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "parcelas.csv"
            caminho.write_text("\ufeff" + conteudo, encoding="utf-8")

            resultado = carregar_dados(caminho)

        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado.loc[0, "VALOR_PARCELA"], Decimal("3625.00"))


class TestEmpreendimento(unittest.TestCase):
    def test_padroniza_caixa_e_preposicoes(self):
        self.assertEqual(
            normalizar_empreendimento("LOTEAMENTO VISTA DO HORTO"),
            "Loteamento Vista do Horto",
        )
        self.assertEqual(
            normalizar_empreendimento("Residencial  Jardim das Palmeiras"),
            "Residencial Jardim das Palmeiras",
        )
        self.assertEqual(
            normalizar_empreendimento("Edifício Parque Azul"), "Edifício Parque Azul"
        )

    def test_unifica_variacoes_de_caixa_na_carga(self):
        dados = pd.DataFrame(
            [
                linha_parcela(EMPREENDIMENTO="LOTEAMENTO VISTA DO HORTO"),
                linha_parcela(
                    EMPREENDIMENTO="Loteamento Vista do Horto", NUM_CONTRATO="2"
                ),
            ]
        )

        resultado = normalizar_dados(dados)

        self.assertEqual(
            resultado["EMPREENDIMENTO"].unique().tolist(), ["Loteamento Vista do Horto"]
        )


class TestRelatorioQualidade(unittest.TestCase):
    def test_conta_linhas_duplicatas_e_empreendimentos(self):
        linha = linha_parcela()
        outra = linha_parcela(NUM_CONTRATO="2", EMPREENDIMENTO="OUTRO LOTE")
        dados = pd.DataFrame([linha, linha.copy(), outra])

        relatorio = relatorio_qualidade(normalizar_dados(dados))

        self.assertEqual(relatorio["linhas_lidas"], 3)
        self.assertEqual(relatorio["duplicatas_removidas"], 1)
        self.assertEqual(relatorio["linhas_finais"], 2)
        self.assertEqual(relatorio["datas_vencimento_invalidas"], 0)
        self.assertEqual(relatorio["valores_invalidos"], 0)
        self.assertEqual(
            relatorio["linhas_por_empreendimento"],
            {"Edifício Parque Azul": 1, "Outro Lote": 1},
        )


if __name__ == "__main__":
    unittest.main()
