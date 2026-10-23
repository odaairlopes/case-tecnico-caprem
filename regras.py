"""Regras de negócio da inadimplência (recebe o resultado de tratamento.carregar_dados)."""

from datetime import date
from decimal import Decimal

import pandas as pd

DATA_REF_PADRAO = date(2026, 9, 25)
CARENCIA_DIAS = 4

FORA_NAO_ATIVO = "Contrato não ativo (fora da cobrança)"
FORA_FINANCIAMENTO = "Financiamento (é do Repasse)"
FORA_ACORDO_ORIGINAL = "Parcela original renegociada em acordo"
FORA_PAGA = "Já paga"
FORA_A_VENCER = "Ainda não venceu"
EM_COMPENSACAO = "Em compensação (1 a 3 dias de atraso)"
INADIMPLENTE = "Inadimplente"

FAIXAS = ["4-30", "31-60", "61-90", "91-180", ">180"]
_LIMITES_FAIXAS = [CARENCIA_DIAS - 1, 30, 60, 90, 180, float("inf")]

ZERO = Decimal("0")


def _soma(valores) -> Decimal:
    return sum(valores, ZERO)


def _motivos(df: pd.DataFrame, dias: pd.Series) -> pd.Series:
    """Um motivo por parcela; vale o primeiro da ordem abaixo.

    1. Contrato diferente de ATIVO (distratado, quitado): fora da cobrança.
    2. Tipo FINANCIAMENTO: fora (é do Repasse).
    3. Tipo diferente de ACORDO com NUM_ACORDO preenchido: parcela original
       renegociada, fora; vale só a dívida das parcelas ACORDO.
    4. Status PAGA: fora.
    5. Atraso de 0 dia ou menos (vence hoje ou depois): ainda não venceu.
    6. Atraso de 1 a 3 dias: fora do total, "em compensação".
    7. Atraso de 4 dias ou mais (e ABERTA): inadimplente.
    """
    motivo = pd.Series(INADIMPLENTE, index=df.index, dtype="object")
    # Aplicadas da última para a primeira, para a regra de maior prioridade prevalecer.
    motivo[dias < CARENCIA_DIAS] = EM_COMPENSACAO
    motivo[dias <= 0] = FORA_A_VENCER
    motivo[df["STATUS_PARCELA"] == "PAGA"] = FORA_PAGA
    motivo[(df["TIPO_PARCELA"] != "ACORDO") & (df["NUM_ACORDO"] != "")] = (
        FORA_ACORDO_ORIGINAL
    )
    motivo[df["TIPO_PARCELA"] == "FINANCIAMENTO"] = FORA_FINANCIAMENTO
    motivo[df["SITUACAO_CONTRATO"] != "ATIVO"] = FORA_NAO_ATIVO
    return motivo


def _faixa(dias: pd.Series, inadimplente: pd.Series) -> pd.Series:
    faixa = pd.cut(dias, bins=_LIMITES_FAIXAS, labels=FAIXAS).astype("object")
    return faixa.where(inadimplente, None)


def _grupo(parcelas: pd.DataFrame, mascara: pd.Series) -> dict:
    sel = parcelas[mascara]
    return {"parcelas": len(sel), "saldo": _soma(sel["SALDO"])}


def calcular_inadimplencia(df: pd.DataFrame, data_ref=DATA_REF_PADRAO) -> dict:
    """Calcula a inadimplência na data de referência (padrão 25/09/2026, nunca hoje).

    Dias de atraso = data_ref - DT_VENCIMENTO (dias corridos).
    Saldo = VALOR_PARCELA - VALOR_PAGO (Decimal), o que cobre pagamento parcial.
    A cobrança só vale para contratos ATIVO, sem financiamento e sem parcelas
    originais de acordo, com status ABERTA e 4 dias de atraso ou mais.
    Faixas de atraso: 4-30, 31-60, 61-90, 91-180 e >180.
    Não altera o DataFrame recebido.

    Retorna um dicionário com "parcelas" (uma linha por parcela, com
    DIAS_ATRASO, SALDO, MOTIVO, INADIMPLENTE e FAIXA_ATRASO), "por_contrato",
    "por_empreendimento" e "resumo".
    """
    parcelas = df.copy()
    dias = (pd.Timestamp(data_ref) - parcelas["DT_VENCIMENTO"]).dt.days
    parcelas["DIAS_ATRASO"] = dias
    parcelas["SALDO"] = parcelas["VALOR_PARCELA"] - parcelas["VALOR_PAGO"]
    parcelas["MOTIVO"] = _motivos(parcelas, dias)
    parcelas["INADIMPLENTE"] = parcelas["MOTIVO"] == INADIMPLENTE
    parcelas["FAIXA_ATRASO"] = _faixa(dias, parcelas["INADIMPLENTE"])

    inad = parcelas[parcelas["INADIMPLENTE"]]
    chave_contrato = ["EMPREENDIMENTO", "NUM_CONTRATO", "UNIDADE", "CLIENTE", "TELEFONE"]
    por_contrato = (
        inad.groupby(chave_contrato, sort=True)
        .agg(
            PARCELAS=("SALDO", "size"),
            SALDO_TOTAL=("SALDO", _soma),
            MAIOR_ATRASO=("DIAS_ATRASO", "max"),
        )
        .reset_index()
    )
    por_empreendimento = (
        inad.groupby("EMPREENDIMENTO", sort=True)
        .agg(
            PARCELAS=("SALDO", "size"),
            CONTRATOS=("NUM_CONTRATO", "nunique"),
            SALDO_TOTAL=("SALDO", _soma),
        )
        .reset_index()
    )

    # Nos grupos "fora da cobrança" só entram parcelas abertas com 4+ dias de
    # atraso, para serem comparáveis ao total e não contar parcelas futuras.
    vencida_aberta = (parcelas["STATUS_PARCELA"] == "ABERTA") & (dias >= CARENCIA_DIAS)
    resumo = {
        "data_ref": pd.Timestamp(data_ref).date(),
        "inadimplente": _grupo(parcelas, parcelas["INADIMPLENTE"]),
        "em_compensacao": _grupo(parcelas, parcelas["MOTIVO"] == EM_COMPENSACAO),
        "distratados": _grupo(
            parcelas, vencida_aberta & (parcelas["SITUACAO_CONTRATO"] == "DISTRATADO")
        ),
        "quitados": _grupo(
            parcelas, vencida_aberta & (parcelas["SITUACAO_CONTRATO"] == "QUITADO")
        ),
        "financiamento": _grupo(
            parcelas, vencida_aberta & (parcelas["MOTIVO"] == FORA_FINANCIAMENTO)
        ),
        "acordo_original": _grupo(
            parcelas, vencida_aberta & (parcelas["MOTIVO"] == FORA_ACORDO_ORIGINAL)
        ),
    }

    return {
        "parcelas": parcelas,
        "por_contrato": por_contrato,
        "por_empreendimento": por_empreendimento,
        "resumo": resumo,
    }
