"""Diagnóstico do CSV de parcelas, por empreendimento. Somente reporta; não corrige nada.

Uso: python perfil.py [caminho.csv] [--max-exemplos N] [--saida relatorio.txt]
O relatório é impresso e também gravado (UTF-8) em docs/evidencias/perfil_saida.txt.
"""
import argparse
import re
import sys
from contextlib import redirect_stdout
from pathlib import Path
import pandas as pd

ARQUIVO_PADRAO = Path("data/parcelas_cobranca_2026-09-25_4.csv")
SAIDA_PADRAO = Path("docs/evidencias/perfil_saida.txt")
COLS_DATA = ["DT_VENCIMENTO", "DT_PAGAMENTO"]
COLS_VALOR = ["VALOR_PARCELA", "VALOR_PAGO"]
CHAVE_PARCELA = ["COLIGADA", "NUM_CONTRATO", "TIPO_PARCELA", "NUM_PARCELA"]


def ler(caminho: Path) -> pd.DataFrame:
    for enc in ("utf-8-sig", "latin-1"):
        try:
            df = pd.read_csv(caminho, sep=";", dtype=str, keep_default_na=False,
                             encoding=enc)
            df.attrs["encoding"] = enc
            # Número da linha no arquivo (cabeçalho = linha 1)
            df["_linha"] = range(2, len(df) + 2)
            return df
        except UnicodeDecodeError:
            continue
    raise SystemExit("Não foi possível decodificar o arquivo (utf-8-sig/latin-1).")


def vazio(s: pd.Series) -> pd.Series:
    return s.str.strip() == ""


def formato_data(v: str) -> str:
    v = v.strip()
    return "(vazio)" if not v else re.sub(r"\d", "9", v)


def formato_valor(v: str) -> str:
    v = v.strip()
    if not v:
        return "(vazio)"
    # Grupos de até 3 dígitos mantêm o tamanho; maiores viram "9+"
    return re.sub(r"\d+", lambda m: "9" * len(m.group()) if len(m.group()) <= 3 else "9+", v)


def parse_valor(v: str):
    """Leitura tolerante, apenas para diagnóstico. Retorna float ou None."""
    v = v.strip().replace("R$", "").replace(" ", "")
    if not v:
        return None
    if "," in v and "." in v:
        dec = "," if v.rfind(",") > v.rfind(".") else "."
        mil = "." if dec == "," else ","
        v = v.replace(mil, "").replace(dec, ".")
    elif "," in v:
        v = v.replace(".", "").replace(",", ".")
    elif v.count(".") > 1:
        v = v.replace(".", "")
    try:
        return float(v)
    except ValueError:
        return None


def so_digitos(v: str) -> str:
    return re.sub(r"\D", "", v)


def titulo(txt: str, char: str = "=") -> None:
    print(f"\n{char * 78}\n{txt}\n{char * 78}")


def linhas_resumo(linhas, limite=8) -> str:
    linhas = sorted(linhas)
    txt = ", ".join(map(str, linhas[:limite]))
    return txt + (f" ... (+{len(linhas) - limite})" if len(linhas) > limite else "")


def perfil_formatos(g: pd.DataFrame) -> None:
    print("\n[Formatos de data]  (9 = dígito)")
    for col in COLS_DATA:
        formatos = g[col].map(formato_data)
        print(f"  {col}:")
        for fmt, n in formatos.value_counts().items():
            extra = ""
            if "/" in fmt:
                partes = g.loc[formatos == fmt, col].str.strip().str.split("/", expand=True)
                if partes.shape[1] >= 2:
                    p1 = pd.to_numeric(partes[0], errors="coerce").max()
                    p2 = pd.to_numeric(partes[1], errors="coerce").max()
                    extra = f"  [maior 1º campo={p1:.0f}, maior 2º campo={p2:.0f}]"
            print(f"    {fmt:<14} {n:>6}{extra}")

    print("\n[Formatos de valor numérico]  (9 = dígito, 9+ = 4 ou mais dígitos)")
    for col in COLS_VALOR:
        contagem = g[col].map(formato_valor).value_counts()
        print(f"  {col}:")
        for fmt, n in contagem.head(12).items():
            print(f"    {fmt:<16} {n:>6}")
        if len(contagem) > 12:
            print(f"    ... (+{len(contagem) - 12} formatos)")
        invalidos = g[col].map(lambda x: x.strip() != "" and parse_valor(x) is None).sum()
        if invalidos:
            print(f"    ATENÇÃO: {invalidos} valores não interpretáveis")


def perfil_distintos(g: pd.DataFrame) -> None:
    for col in ("STATUS_PARCELA", "SITUACAO_CONTRATO"):
        print(f"\n[Valores distintos de {col}]")
        for val, n in g[col].value_counts().items():
            print(f"    {val!r:<28} {n:>6}")


def perfil_duplicadas(g: pd.DataFrame) -> None:
    cols = [c for c in g.columns if c != "_linha"]
    exatas = g[g.duplicated(subset=cols, keep=False)]
    n_extra = int(g.duplicated(subset=cols, keep="first").sum())
    print(f"\n[Linhas duplicadas]\n  Idênticas em todas as colunas: {n_extra} repetições "
          f"({len(exatas)} linhas envolvidas)")
    if len(exatas):
        print(f"    linhas do arquivo: {linhas_resumo(exatas['_linha'])}")
    por_chave = g[g.duplicated(subset=CHAVE_PARCELA, keep=False)]
    so_chave = por_chave[~por_chave.index.isin(exatas.index)]
    print(f"  Mesma chave ({'+'.join(CHAVE_PARCELA)}) mas conteúdo diferente: "
          f"{len(so_chave)} linhas")
    if len(so_chave):
        print(f"    linhas do arquivo: {linhas_resumo(so_chave['_linha'])}")


def perfil_nulos(g: pd.DataFrame) -> None:
    print("\n[Nulos/vazios por coluna]")
    achou = False
    for c in g.columns:
        if c == "_linha":
            continue
        n = int(vazio(g[c]).sum())
        if n:
            achou = True
            print(f"    {c:<18} {n:>6}  ({n / len(g):.1%})")
    if not achou:
        print("    nenhum")


def perfil_abertas_pagas(g: pd.DataFrame) -> None:
    status = g["STATUS_PARCELA"].str.strip().str.casefold()
    abertas = g[status.str.contains("abert", na=False)]
    pago = abertas["VALOR_PAGO"].map(parse_valor)
    suspeitas = abertas[pago.fillna(0) > 0]
    print(f"\n[Parcelas ABERTAS com VALOR_PAGO > 0]\n  Parcelas abertas: {len(abertas)} | "
          f"com valor pago > 0: {len(suspeitas)}")
    if len(suspeitas):
        print(f"    linhas do arquivo: {linhas_resumo(suspeitas['_linha'])}")
        print(f"    soma VALOR_PAGO: {pago[suspeitas.index].sum():,.2f}")


def perfil_identidade(g: pd.DataFrame, maximo: int) -> None:
    d = g.assign(
        _cpf=g["CPF_CNPJ"].map(so_digitos),
        _nome=g["CLIENTE"].str.strip().str.casefold().str.replace(r"\s+", " ", regex=True),
        _contrato=g["COLIGADA"].str.strip() + "/" + g["NUM_CONTRATO"].str.strip(),
    )
    com_cpf = d[d["_cpf"] != ""]
    por_contrato = com_cpf.groupby("_contrato")["_cpf"].nunique()
    multi = por_contrato[por_contrato > 1]
    print(f"\n[Contratos (coligada/contrato) com mais de um CPF/CNPJ]: {len(multi)}")
    for ct in multi.index[:maximo]:
        sub = com_cpf[com_cpf["_contrato"] == ct]
        print(f"    {ct}: {sorted(sub['CPF_CNPJ'].unique())}  linhas {linhas_resumo(sub['_linha'], 5)}")
    if len(multi) > maximo:
        print(f"    ... (+{len(multi) - maximo})")

    com_nome = com_cpf[com_cpf["_nome"] != ""]
    por_cpf = com_nome.groupby("_cpf")["_nome"].nunique()
    multi_n = por_cpf[por_cpf > 1]
    print(f"\n[CPFs/CNPJs com mais de um nome]: {len(multi_n)}  "
          "(nomes comparados sem diferenciar caixa/espaços)")
    for cpf in multi_n.index[:maximo]:
        sub = com_nome[com_nome["_cpf"] == cpf]
        print(f"    {cpf}: {sorted(sub['CLIENTE'].unique())}  linhas {linhas_resumo(sub['_linha'], 5)}")
    if len(multi_n) > maximo:
        print(f"    ... (+{len(multi_n) - maximo})")


class Tee:
    """Escreve na tela e no arquivo ao mesmo tempo."""

    def __init__(self, *destinos):
        self.destinos = destinos

    def write(self, texto: str) -> int:
        for d in self.destinos:
            d.write(texto)
        return len(texto)

    def flush(self) -> None:
        for d in self.destinos:
            d.flush()


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivo", nargs="?", type=Path, default=ARQUIVO_PADRAO)
    ap.add_argument("--max-exemplos", type=int, default=15)
    ap.add_argument("--saida", type=Path, default=SAIDA_PADRAO)
    args = ap.parse_args()
    if not args.arquivo.exists():
        raise SystemExit(f"Arquivo não encontrado: {args.arquivo}")

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    with open(args.saida, "w", encoding="utf-8") as f, redirect_stdout(Tee(sys.stdout, f)):
        relatorio(args)
    print(f"\nRelatório gravado em: {args.saida}")


def relatorio(args: argparse.Namespace) -> None:
    df = ler(args.arquivo)
    titulo(f"PERFIL DO ARQUIVO: {args.arquivo}")
    print(f"Encoding: {df.attrs['encoding']} | linhas de dados: {len(df)} | "
          f"colunas: {len(df.columns) - 1}")

    for emp, g in df.groupby("EMPREENDIMENTO", sort=True):
        titulo(f"EMPREENDIMENTO: {emp!r}  ({len(g)} linhas; arquivo linhas "
               f"{g['_linha'].min()}–{g['_linha'].max()})", "-")
        perfil_formatos(g)
        perfil_distintos(g)
        perfil_duplicadas(g)
        perfil_nulos(g)
        perfil_abertas_pagas(g)
        perfil_identidade(g, args.max_exemplos)


if __name__ == "__main__":
    main()
