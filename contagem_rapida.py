import pandas as pd

df = pd.read_csv("data/parcelas_cobranca_2026-09-25_4.csv",
                 sep=";", dtype=str, encoding="utf-8-sig")
print("linhas:", len(df))
print("duplicadas exatas:", df.duplicated().sum())
print(df.groupby("EMPREENDIMENTO").size())
print(df.STATUS_PARCELA.value_counts())
print(df.SITUACAO_CONTRATO.value_counts())

ab = df[df.STATUS_PARCELA.str.upper() == "ABERTA"]
# só testa se é maior que zero, então o formato do número não atrapalha
pago = ab.VALOR_PAGO.str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float)
print("abertas com valor pago > 0:", (pago > 0).sum())