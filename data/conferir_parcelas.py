import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

ARQUIVO_CSV = Path(__file__).parent / "parcelas_cobranca_2026-09-25_4.csv"
REF = date(2026, 9, 25)      # data de referência (data do arquivo)
CARENCIA_DIAS = 4            # a Cobrança só liga a partir de 4 dias de atraso


def ler_data(texto):
    texto = texto.strip()
    if "-" in texto:                  # aaaa-mm-dd (Loteamento)
        a, m, d = texto.split("-")
    else:                             # dd/mm/aaaa (demais)
        d, m, a = texto.split("/")
    return date(int(a), int(m), int(d))


def ler_valor(texto):
    texto = texto.strip()
    if "," in texto:                  # 2.812,50 (formato brasileiro)
        texto = texto.replace(".", "").replace(",", ".")
    return Decimal(texto)             # 2000.00 (Loteamento) já está ok


def brl(v):
    s = f"{v:,.2f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def classificar(p, atraso, excluir_originais_de_acordo=True):
    """Devolve (entra, motivo). Regras na ordem confirmada com a Cobrança."""
    if p["SITUACAO_CONTRATO"].strip().upper() != "ATIVO":
        return False, f"contrato {p['SITUACAO_CONTRATO'].strip()} (fora da cobrança)"
    if p["TIPO_PARCELA"].strip().upper() == "FINANCIAMENTO":
        return False, "financiamento (é do Repasse)"
    if (excluir_originais_de_acordo
            and p["TIPO_PARCELA"].strip().upper() != "ACORDO"
            and p["NUM_ACORDO"].strip()):
        return False, f"parcela original, renegociada no acordo {p['NUM_ACORDO'].strip()}"
    if p["STATUS_PARCELA"].strip().upper() != "ABERTA":
        return False, "já paga"
    if atraso <= 0:
        return False, "ainda não venceu"
    if atraso < CARENCIA_DIAS:
        return False, f"{atraso} dia(s) de atraso (menos de {CARENCIA_DIAS}, em compensação)"
    return True, "ENTRA"


def main():
    if not ARQUIVO_CSV.exists():
        print("Arquivo CSV não encontrado.")
        return

    contrato = input("Digite o número do contrato: ").strip()
    linhas, vistos = [], {}

    with ARQUIVO_CSV.open("r", encoding="utf-8-sig", newline="") as arq:
        leitor = csv.DictReader(arq, delimiter=";")
        for n, p in enumerate(leitor, start=2):
            if p["NUM_CONTRATO"].strip() != contrato:
                continue
            chave = tuple(p.values())
            atraso = (REF - ler_data(p["DT_VENCIMENTO"])).days
            valor = ler_valor(p["VALOR_PARCELA"])
            pago = ler_valor(p["VALOR_PAGO"])

            if chave in vistos:   # linha idêntica a outra já lida
                entra = entra_alt = False
                motivo = f"linha repetida (igual à linha {vistos[chave]})"
            else:
                vistos[chave] = n
                entra, motivo = classificar(p, atraso, True)
                entra_alt, _ = classificar(p, atraso, False)

            linhas.append(dict(linha=n, p=p, atraso=atraso, valor=valor,
                               pago=pago, saldo=valor - pago,
                               entra=entra, entra_alt=entra_alt, motivo=motivo))

    if not linhas:
        print("Nenhuma parcela encontrada.")
        return

    print(f"\nContrato {contrato}: {len(linhas)} linhas lidas "
          f"(data de referência {REF.strftime('%d/%m/%Y')})")

    # 1) resumo dos motivos de exclusão
    print("\n--- Linhas que ficam de fora, por motivo ---")
    motivos = {}
    for x in linhas:
        if not x["entra"]:
            motivos.setdefault(x["motivo"], []).append(x["linha"])
    for m, ls in motivos.items():
        print(f"{len(ls):3d} linha(s): {m}  [linhas {ls[0]} a {ls[-1]}]")

    # 2) o que entra
    entram = [x for x in linhas if x["entra"]]
    print("\n--- Linhas que ENTRAM (é isso que você soma) ---")
    for x in entram:
        p = x["p"]
        print(f"Linha {x['linha']} | {p['TIPO_PARCELA']} {p['NUM_PARCELA']} | "
              f"Venc {p['DT_VENCIMENTO']} | Atraso {x['atraso']} dias | "
              f"Valor {brl(x['valor'])} | Pago {brl(x['pago'])} | "
              f"Saldo {brl(x['saldo'])}")
    if entram:
        print("\nSaldos para somar à mão: " + " + ".join(brl(x["saldo"]) for x in entram))
    else:
        print("(nenhuma linha entra)")

    # 3) totais
    total = sum((x["saldo"] for x in entram), Decimal("0"))
    total_alt = sum((x["saldo"] for x in linhas if x["entra_alt"]), Decimal("0"))
    print(f"\nTOTAL EM ATRASO (regras confirmadas): R$ {brl(total)}")
    print(f"Total se as originais de acordo fossem contadas: R$ {brl(total_alt)} "
          f"(diferença: R$ {brl(total_alt - total)})")

    # 4) todas as linhas, se quiser conferir
    if input("\nMostrar todas as linhas com a decisão? (s/n): ").strip().lower() == "s":
        for x in linhas:
            p = x["p"]
            marca = "ENTRA" if x["entra"] else "fora "
            print(f"{marca} | Linha {x['linha']} | {p['TIPO_PARCELA']} {p['NUM_PARCELA']} | "
                  f"Venc {p['DT_VENCIMENTO']} | Atraso {x['atraso']} | "
                  f"{p['STATUS_PARCELA']} | {x['motivo']}")


if __name__ == "__main__":
    main()