"""Painel de inadimplência da Caprem para a Cobrança (streamlit run app.py)."""

from decimal import Decimal
from io import BytesIO

import altair as alt
import pandas as pd
import streamlit as st

import regras
import tratamento

COR_BARRAS = "#C0392B"
CHAVE_CONTRATO = ["EMPREENDIMENTO", "NUM_CONTRATO", "UNIDADE", "CLIENTE", "TELEFONE"]


def moeda(valor) -> str:
    """Formata no padrão brasileiro: R$ 1.234,56 (só para exibir)."""
    texto = f"{Decimal(valor):,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


@st.cache_data(show_spinner="Carregando os dados...")
def carregar():
    df = tratamento.carregar_dados()
    return df, tratamento.relatorio_qualidade(df)


@st.cache_data(show_spinner="Calculando a inadimplência...")
def calcular(data_ref):
    df, _ = carregar()
    resultado = regras.calcular_inadimplencia(df, data_ref)
    parcelas = resultado["parcelas"]
    return parcelas[parcelas["INADIMPLENTE"]].copy(), resultado["resumo"]


def tabela_por_contrato(inad: pd.DataFrame) -> pd.DataFrame:
    agrupado = (
        inad.groupby(CHAVE_CONTRATO, sort=False)
        .agg(
            SALDO=("SALDO", lambda s: sum(s, Decimal("0"))),
            PARCELAS=("SALDO", "size"),
            MAIOR_ATRASO=("DIAS_ATRASO", "max"),
        )
        .reset_index()
        .sort_values("SALDO", ascending=False)
    )
    return agrupado


def excel(tabela: pd.DataFrame) -> bytes:
    saida = BytesIO()
    with pd.ExcelWriter(saida, engine="openpyxl") as escritor:
        tabela.to_excel(escritor, index=False, sheet_name="Inadimplência")
        planilha = escritor.sheets["Inadimplência"]
        coluna_saldo = list(tabela.columns).index("Saldo devedor (R$)") + 1
        for linha in planilha.iter_rows(min_row=2, min_col=coluna_saldo, max_col=coluna_saldo):
            linha[0].number_format = '"R$" #,##0.00'
        for coluna in planilha.columns:
            largura = max(len(str(c.value or "")) for c in coluna) + 2
            planilha.column_dimensions[coluna[0].column_letter].width = min(largura, 45)
    return saida.getvalue()


st.set_page_config(page_title="Inadimplência Caprem", page_icon="📋", layout="wide")

try:
    _, qualidade = carregar()
except FileNotFoundError:
    st.error(
        "Não encontrei o arquivo de parcelas. Coloque o CSV na pasta `data` "
        f"({tratamento.ARQUIVO_PADRAO}) e atualize a página."
    )
    st.stop()
except ValueError as erro:
    st.error(f"Não foi possível ler o arquivo de parcelas: {erro}")
    st.stop()

inad, resumo = calcular(regras.DATA_REF_PADRAO)

st.title("Inadimplência — Cobrança")
st.caption(f"Data de referência: **{resumo['data_ref'].strftime('%d/%m/%Y')}** (data do arquivo)")

with st.sidebar:
    st.header("Filtros")
    empreendimentos = st.multiselect("Empreendimento", sorted(inad["EMPREENDIMENTO"].unique()))
    faixas = st.multiselect("Faixa de atraso (dias)", regras.FAIXAS)
    tipos = st.multiselect("Tipo de parcela", sorted(inad["TIPO_PARCELA"].unique()))

filtrado = inad
if empreendimentos:
    filtrado = filtrado[filtrado["EMPREENDIMENTO"].isin(empreendimentos)]
if faixas:
    filtrado = filtrado[filtrado["FAIXA_ATRASO"].isin(faixas)]
if tipos:
    filtrado = filtrado[filtrado["TIPO_PARCELA"].isin(tipos)]

if filtrado.empty:
    st.info(
        "Nenhuma parcela em atraso com esses filtros. "
        "Tire algum filtro na barra lateral para ver mais resultados."
    )
else:
    total = sum(filtrado["SALDO"], Decimal("0"))
    clientes = filtrado[["NUM_CONTRATO", "CLIENTE"]].drop_duplicates().shape[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total em atraso", moeda(total))
    c2.metric("Clientes inadimplentes", f"{clientes:,}".replace(",", "."))
    c3.metric("Parcelas em atraso", f"{len(filtrado):,}".replace(",", "."))
    c4.metric("Atraso médio", f"{filtrado['DIAS_ATRASO'].mean():.0f} dias")

    esquerda, direita = st.columns(2)
    por_emp = (
        filtrado.assign(VALOR=filtrado["SALDO"].astype(float))
        .groupby("EMPREENDIMENTO", as_index=False)["VALOR"]
        .sum()
    )
    esquerda.subheader("Saldo por empreendimento")
    esquerda.altair_chart(
        alt.Chart(por_emp)
        .mark_bar(color=COR_BARRAS)
        .encode(
            x=alt.X("EMPREENDIMENTO:N", title="Empreendimento", sort="-y"),
            y=alt.Y("VALOR:Q", title="Saldo em atraso (R$)"),
            tooltip=[
                alt.Tooltip("EMPREENDIMENTO:N", title="Empreendimento"),
                alt.Tooltip("VALOR:Q", title="Saldo (R$)", format=",.2f"),
            ],
        ),
        width="stretch",
    )

    por_faixa = (
        filtrado.assign(VALOR=filtrado["SALDO"].astype(float))
        .groupby("FAIXA_ATRASO", as_index=False)["VALOR"]
        .sum()
    )
    direita.subheader("Saldo por faixa de atraso")
    direita.altair_chart(
        alt.Chart(por_faixa)
        .mark_bar(color=COR_BARRAS)
        .encode(
            x=alt.X("FAIXA_ATRASO:N", title="Dias de atraso", sort=regras.FAIXAS),
            y=alt.Y("VALOR:Q", title="Saldo em atraso (R$)"),
            tooltip=[
                alt.Tooltip("FAIXA_ATRASO:N", title="Faixa (dias)"),
                alt.Tooltip("VALOR:Q", title="Saldo (R$)", format=",.2f"),
            ],
        ),
        width="stretch",
    )

    st.subheader("Clientes em atraso")
    contratos = tabela_por_contrato(filtrado)
    tabela = pd.DataFrame(
        {
            "Cliente": contratos["CLIENTE"],
            "Contrato": contratos["NUM_CONTRATO"],
            "Empreendimento": contratos["EMPREENDIMENTO"],
            "Unidade": contratos["UNIDADE"],
            "Telefone": contratos["TELEFONE"],
            "Parcelas em atraso": contratos["PARCELAS"],
            "Parcela mais antiga (dias de atraso)": contratos["MAIOR_ATRASO"],
            "Saldo devedor (R$)": contratos["SALDO"].astype(float),
        }
    ).reset_index(drop=True)
    exibicao = tabela.copy()
    exibicao["Saldo devedor (R$)"] = contratos["SALDO"].map(moeda).to_numpy()
    st.dataframe(exibicao, hide_index=True, width="stretch")
    st.download_button(
        "Baixar tabela em Excel",
        data=excel(tabela),
        file_name="inadimplencia.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

with st.expander("Qualidade dos dados e valores fora da cobrança"):
    st.markdown("**Leitura do arquivo**")
    st.write(
        f"- Linhas lidas: {qualidade['linhas_lidas']}\n"
        f"- Linhas repetidas removidas: {qualidade['duplicatas_removidas']}\n"
        f"- Linhas usadas: {qualidade['linhas_finais']}\n"
        f"- Datas de vencimento inválidas: {qualidade['datas_vencimento_invalidas']}\n"
        f"- Valores inválidos: {qualidade['valores_invalidos']}"
    )
    st.caption(
        "Dado inválido interrompe a leitura com aviso, por isso estes dois "
        "contadores são sempre 0 quando o painel abre."
    )
    st.write(
        pd.DataFrame(
            {
                "Empreendimento": list(qualidade["linhas_por_empreendimento"]),
                "Linhas": list(qualidade["linhas_por_empreendimento"].values()),
            }
        )
    )
    st.markdown("**Fora da cobrança (parcelas abertas com 4+ dias de atraso)**")
    nomes = {
        "inadimplente": "Em cobrança (total do painel, sem filtros)",
        "em_compensacao": "Em compensação (1 a 3 dias)",
        "distratados": "Contratos distratados",
        "quitados": "Contratos quitados",
        "financiamento": "Financiamento (Repasse)",
        "acordo_original": "Parcelas originais de acordo",
    }
    st.table(
        pd.DataFrame(
            [
                {
                    "Grupo": nome,
                    "Parcelas": resumo[chave]["parcelas"],
                    "Saldo": moeda(resumo[chave]["saldo"]),
                }
                for chave, nome in nomes.items()
            ]
        )
    )
