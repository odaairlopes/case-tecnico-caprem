"""Conferência independente do total em atraso por empreendimento.

O cálculo abaixo NÃO usa regras.py: são filtros e somas diretas sobre o CSV
tratado. Só no final o resultado é comparado com regras.calcular_inadimplencia.
Saída: tabela lado a lado e código 0 (sem divergência) ou 1 (com divergência).
"""

import sys
from datetime import datetime
from decimal import Decimal

import pandas as pd

from tratamento import carregar_dados

DATA_REF = datetime(2026, 9, 25)
CARENCIA = 4


def calcular_conferencia(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica os filtros um a um e soma o saldo por empreendimento."""
    d = df[df["SITUACAO_CONTRATO"] == "ATIVO"]
    d = d[d["TIPO_PARCELA"] != "FINANCIAMENTO"]
    d = d[d["STATUS_PARCELA"] == "ABERTA"]
    # Original de acordo: tipo diferente de ACORDO com NUM_ACORDO preenchido.
    original_de_acordo = (d["TIPO_PARCELA"] != "ACORDO") & (d["NUM_ACORDO"] != "")
    d = d[~original_de_acordo]
    atraso = (DATA_REF - d["DT_VENCIMENTO"]).dt.days
    d = d[atraso >= CARENCIA]

    saldos = d["VALOR_PARCELA"] - d["VALOR_PAGO"]
    linhas = {}
    for emp in sorted(d["EMPREENDIMENTO"].unique()):
        sel = d["EMPREENDIMENTO"] == emp
        linhas[emp] = {
            "parcelas": int(sel.sum()),
            "contratos": int(d.loc[sel, "NUM_CONTRATO"].nunique()),
            "saldo": sum(saldos[sel], Decimal("0")),
        }
    return pd.DataFrame.from_dict(linhas, orient="index")


def formatar(valor: Decimal) -> str:
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def main() -> int:
    df = carregar_dados()
    conf = calcular_conferencia(df)

    # Só agora o regras.py entra, para comparar.
    from regras import calcular_inadimplencia

    res = calcular_inadimplencia(df, DATA_REF.date())["por_empreendimento"]
    reg = res.set_index("EMPREENDIMENTO").rename(
        columns={"PARCELAS": "parcelas", "CONTRATOS": "contratos", "SALDO_TOTAL": "saldo"}
    )

    empreendimentos = sorted(set(conf.index) | set(reg.index))
    zero = {"parcelas": 0, "contratos": 0, "saldo": Decimal("0")}
    divergencias = []
    print(f"Data de referência: {DATA_REF.date()}\n")
    print(f"{'Empreendimento':<36}{'Campo':<11}{'conferir':>16}{'regras':>16}{'diferença':>14}")

    tot_c = dict(zero)
    tot_r = dict(zero)
    for emp in empreendimentos:
        c = conf.loc[emp].to_dict() if emp in conf.index else zero
        r = reg.loc[emp].to_dict() if emp in reg.index else zero
        for campo in ("parcelas", "contratos", "saldo"):
            vc, vr = c[campo], r[campo]
            if campo == "saldo":
                vr = Decimal(vr)
            dif = vc - vr
            if campo != "contratos":
                tot_c[campo] += vc
                tot_r[campo] += vr
            mostrar = formatar if campo == "saldo" else str
            print(f"{emp:<36}{campo:<11}{mostrar(vc):>16}{mostrar(vr):>16}{mostrar(dif):>14}")
            if dif != 0:
                divergencias.append(f"{emp}: {campo} conferir={vc} regras={vr}")

    print()
    for campo in ("parcelas", "saldo"):
        mostrar = formatar if campo == "saldo" else str
        dif = tot_c[campo] - tot_r[campo]
        print(f"{'TOTAL GERAL':<36}{campo:<11}{mostrar(tot_c[campo]):>16}"
              f"{mostrar(tot_r[campo]):>16}{mostrar(dif):>14}")
        if dif != 0:
            divergencias.append(f"TOTAL: {campo} conferir={tot_c[campo]} regras={tot_r[campo]}")

    print()
    if divergencias:
        print("DIVERGÊNCIAS:")
        for item in divergencias:
            print(" -", item)
        return 1
    print("Sem divergência.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
