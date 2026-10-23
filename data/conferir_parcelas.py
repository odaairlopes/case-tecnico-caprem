import csv
from pathlib import Path
from datetime import date

# O CSV precisa estar na mesma pasta deste script.
ARQUIVO_CSV = Path(__file__).with_name(
    "parcelas_cobranca_2026-09-25_4.csv"
)

REF = date(2026, 9, 25)

def ler_data(texto):
    texto = texto.strip()
    if "-" in texto:
        ano, mes, dia = texto.split("-")
    else:
        dia, mes, ano = texto.split("/")
    return date(int(ano), int(mes), int(dia))


def main():
    if not ARQUIVO_CSV.exists():
        print("Arquivo CSV não encontrado.")
        return

    contrato = input("Digite o número do contrato: ").strip()
    encontrados = 0

    with ARQUIVO_CSV.open(
        "r", encoding="utf-8-sig", newline=""
    ) as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=";")

        for linha, parcela in enumerate(leitor, start=2):
            if parcela["NUM_CONTRATO"].strip() != contrato:
                continue

            encontrados += 1
            acordo = parcela["NUM_ACORDO"].strip() or "-"
            atraso = (REF - ler_data(parcela["DT_VENCIMENTO"])).days

            print(
                f"Linha {linha} | "
                f"Contrato: {parcela['NUM_CONTRATO']} | "
                f"Situação: {parcela['SITUACAO_CONTRATO']} | "
                f"Parcela: {parcela['NUM_PARCELA']} | "
                f"Tipo: {parcela['TIPO_PARCELA']} | "
                f"Vencimento: {parcela['DT_VENCIMENTO']} | "
                f"Status: {parcela['STATUS_PARCELA']} | "
                f"Valor: {parcela['VALOR_PARCELA']} | "
                f"Pago: {parcela['VALOR_PAGO']} | "
                f"Acordo: {acordo}  | "
                f" Atraso: {atraso}d dias"
            )

    if encontrados == 0:
        print("Nenhuma parcela encontrada.")
    else:
        print(f"\nTotal de linhas encontradas: {encontrados}")
        print("Confira as regras de cobrança manualmente.")


if __name__ == "__main__":
    main()