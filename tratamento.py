"""Leitura, validação e normalização do CSV de parcelas."""

from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
import re

import pandas as pd


ARQUIVO_PADRAO = (
    Path(__file__).resolve().parent
    / "data"
    / "parcelas_cobranca_2026-09-25_4.csv"
)

COLUNAS = [
    "COLIGADA",
    "EMPREENDIMENTO",
    "UNIDADE",
    "NUM_CONTRATO",
    "SITUACAO_CONTRATO",
    "CLIENTE",
    "CPF_CNPJ",
    "TELEFONE",
    "TIPO_PARCELA",
    "NUM_PARCELA",
    "DT_VENCIMENTO",
    "VALOR_PARCELA",
    "VALOR_PAGO",
    "DT_PAGAMENTO",
    "STATUS_PARCELA",
    "NUM_ACORDO",
]

CAMPOS_OPCIONAIS = {"DT_PAGAMENTO", "NUM_ACORDO"}
FORMATOS_DATA = ("%d/%m/%Y", "%Y-%m-%d")
STATUS_VALIDOS = {"ABERTA", "PAGA"}
SITUACOES_VALIDAS = {"ATIVO", "QUITADO", "DISTRATADO"}
TIPOS_VALIDOS = {"MENSAL", "INTERMEDIARIA", "CHAVES", "FINANCIAMENTO", "ACORDO"}

_VALOR_BR = re.compile(r"-?(?:\d+|\d{1,3}(?:\.\d{3})+),\d{2}")
_VALOR_ISO = re.compile(r"-?\d+\.\d{2}")


def _erro_linha(linha: int, coluna: str, valor: str, motivo: str) -> ValueError:
    return ValueError(
        f"Linha {linha} do CSV, coluna {coluna}: {motivo} (valor {valor!r})."
    )


def _parse_data(valor: str, linha: int, coluna: str) -> pd.Timestamp:
    for formato in FORMATOS_DATA:
        try:
            return pd.Timestamp(datetime.strptime(valor, formato))
        except ValueError:
            continue
    formatos = "dd/mm/aaaa ou aaaa-mm-dd"
    raise _erro_linha(linha, coluna, valor, f"data inválida; esperado {formatos}")


def _parse_valor(valor: str, linha: int, coluna: str) -> Decimal:
    if _VALOR_BR.fullmatch(valor):
        texto = valor.replace(".", "").replace(",", ".")
    elif _VALOR_ISO.fullmatch(valor):
        texto = valor
    else:
        raise _erro_linha(
            linha,
            coluna,
            valor,
            "valor inválido; esperado formato brasileiro (1.234,56) "
            "ou decimal com ponto (1234.56)",
        )

    try:
        return Decimal(texto)
    except InvalidOperation as exc:
        raise _erro_linha(linha, coluna, valor, "valor monetário inválido") from exc


_PALAVRAS_MINUSCULAS = {"de", "da", "do", "das", "dos"}


def normalizar_empreendimento(nome: str) -> str:
    """Padroniza o nome em formato de título, com de/da/do/das/dos em minúsculas."""
    palavras = nome.split()
    return " ".join(
        palavra.lower()
        if posicao > 0 and palavra.lower() in _PALAVRAS_MINUSCULAS
        else palavra.capitalize()
        for posicao, palavra in enumerate(palavras)
    )


def normalizar_dados(dados: pd.DataFrame) -> pd.DataFrame:
    """Valida e normaliza um DataFrame lido do CSV, sem aplicar regras de cobrança."""
    colunas_ausentes = [coluna for coluna in COLUNAS if coluna not in dados.columns]
    colunas_extras = [coluna for coluna in dados.columns if coluna not in COLUNAS]
    if colunas_ausentes or colunas_extras:
        detalhes = []
        if colunas_ausentes:
            detalhes.append(f"colunas ausentes: {', '.join(colunas_ausentes)}")
        if colunas_extras:
            detalhes.append(f"colunas inesperadas: {', '.join(colunas_extras)}")
        raise ValueError("Cabeçalho do CSV inválido; " + "; ".join(detalhes) + ".")
    if dados.empty:
        raise ValueError("O CSV não contém parcelas para processar.")

    df = dados.loc[:, COLUNAS].copy()
    # Os números de linha são relativos ao arquivo, cujo cabeçalho ocupa a linha 1.
    df["_linha_arquivo"] = range(2, len(df) + 2)
    duplicatas_removidas = int(df.duplicated(subset=COLUNAS).sum())
    df = df.drop_duplicates(subset=COLUNAS, keep="first").copy()

    for coluna in COLUNAS:
        df[coluna] = df[coluna].astype("string").fillna("").str.strip()

    obrigatorias = [coluna for coluna in COLUNAS if coluna not in CAMPOS_OPCIONAIS]
    for coluna in obrigatorias:
        vazias = df[coluna].eq("")
        if vazias.any():
            linha = int(df.loc[vazias, "_linha_arquivo"].iloc[0])
            raise _erro_linha(linha, coluna, "", "campo obrigatório vazio")

    df["EMPREENDIMENTO"] = df["EMPREENDIMENTO"].map(normalizar_empreendimento)

    for coluna, valores_validos, nome_campo in (
        ("STATUS_PARCELA", STATUS_VALIDOS, "status de parcela"),
        ("SITUACAO_CONTRATO", SITUACOES_VALIDAS, "situação de contrato"),
        ("TIPO_PARCELA", TIPOS_VALIDOS, "tipo de parcela"),
    ):
        df[coluna] = df[coluna].str.upper()
        invalidos = ~df[coluna].isin(valores_validos)
        if invalidos.any():
            indice = invalidos[invalidos].index[0]
            linha = int(df.at[indice, "_linha_arquivo"])
            raise _erro_linha(
                linha,
                coluna,
                str(df.at[indice, coluna]),
                f"{nome_campo} não reconhecido",
            )

    df["DT_VENCIMENTO"] = pd.to_datetime(
        [
            _parse_data(str(valor), int(linha), "DT_VENCIMENTO")
            for valor, linha in zip(df["DT_VENCIMENTO"], df["_linha_arquivo"])
        ]
    )

    pagamentos = []
    for valor, linha in zip(df["DT_PAGAMENTO"], df["_linha_arquivo"]):
        if valor == "":
            pagamentos.append(pd.NaT)
        else:
            pagamentos.append(_parse_data(str(valor), int(linha), "DT_PAGAMENTO"))
    df["DT_PAGAMENTO"] = pd.to_datetime(pagamentos)

    for coluna in ("VALOR_PARCELA", "VALOR_PAGO"):
        df[coluna] = [
            _parse_valor(str(valor), int(linha), coluna)
            for valor, linha in zip(df[coluna], df["_linha_arquivo"])
        ]

    df = df.drop(columns="_linha_arquivo").reset_index(drop=True)
    df.attrs["duplicatas_removidas"] = duplicatas_removidas
    df.attrs["linhas_lidas"] = len(dados)
    return df


def relatorio_qualidade(df: pd.DataFrame) -> dict:
    """Resume a qualidade da carga para exibição no dashboard.

    Datas e valores inválidos interrompem a carga com erro; por isso, se o
    DataFrame chegou até aqui, os dois contadores são sempre 0.
    """
    removidas = df.attrs["duplicatas_removidas"]
    return {
        "linhas_lidas": df.attrs["linhas_lidas"],
        "duplicatas_removidas": removidas,
        "linhas_finais": len(df),
        "datas_vencimento_invalidas": int(df["DT_VENCIMENTO"].isna().sum()),
        "valores_invalidos": int(
            df[["VALOR_PARCELA", "VALOR_PAGO"]].isna().sum().sum()
        ),
        "linhas_por_empreendimento": {
            nome: int(qtd)
            for nome, qtd in df["EMPREENDIMENTO"].value_counts().sort_index().items()
        },
    }


def carregar_dados(caminho: str | Path = ARQUIVO_PADRAO) -> pd.DataFrame:
    """Lê o CSV em UTF-8 com BOM, valida o esquema e devolve dados normalizados."""
    arquivo = Path(caminho)
    try:
        dados = pd.read_csv(
            arquivo,
            sep=";",
            dtype="string",
            encoding="utf-8-sig",
            keep_default_na=False,
        )
    except UnicodeDecodeError as exc:
        raise ValueError(
            f"Não foi possível ler {arquivo}: o arquivo deve estar codificado em UTF-8."
        ) from exc

    return normalizar_dados(dados)