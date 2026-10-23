"""Painel de inadimplência da Caprem para a Cobrança (streamlit run app.py)."""

import re
import unicodedata
from datetime import date
from decimal import Decimal
from io import BytesIO

import altair as alt
import pandas as pd
import streamlit as st

import regras
import tratamento

CHAVE_CONTRATO = ["EMPREENDIMENTO", "NUM_CONTRATO", "UNIDADE", "CLIENTE", "TELEFONE"]

# Cores só visuais: não mudam as faixas da regra (4-30, 31-60, 61-90, 91-180, >180).
GRAVIDADE = {
    "4-30": "Até 30 dias",
    "31-60": "31 a 90 dias",
    "61-90": "31 a 90 dias",
    "91-180": "Mais de 90 dias",
    ">180": "Mais de 90 dias",
}
ORDEM_GRAVIDADE = ["Até 30 dias", "31 a 90 dias", "Mais de 90 dias"]
COR_GRAVIDADE = {
    "Até 30 dias": "#95A5A6",
    "31 a 90 dias": "#E6A23C",
    "Mais de 90 dias": "#C0392B",
}
ESCALA_COR = alt.Scale(
    domain=ORDEM_GRAVIDADE, range=[COR_GRAVIDADE[g] for g in ORDEM_GRAVIDADE]
)


def moeda(valor) -> str:
    """Formata no padrão brasileiro: R$ 1.234,56 (só para exibir)."""
    texto = f"{Decimal(valor):,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def inteiro(valor) -> str:
    return f"{valor:,}".replace(",", ".")


def sem_acento(texto: str) -> str:
    decomposto = unicodedata.normalize("NFKD", str(texto))
    return "".join(c for c in decomposto if not unicodedata.combining(c)).casefold()


@st.cache_data(show_spinner="Carregando os dados...")
def carregar():
    df = tratamento.carregar_dados()
    return df, tratamento.relatorio_qualidade(df)


@st.cache_data(show_spinner="Calculando a inadimplência...")
def calcular(data_ref: date):
    df, _ = carregar()
    resultado = regras.calcular_inadimplencia(df, data_ref)
    parcelas = resultado["parcelas"]
    return parcelas[parcelas["INADIMPLENTE"]].copy(), resultado["resumo"]


def buscar(inad: pd.DataFrame, termo: str) -> pd.DataFrame:
    """Nome (sem acento e sem diferenciar caixa) ou CPF/CNPJ (com ou sem pontuação)."""
    termo = termo.strip()
    if not termo:
        return inad
    if re.search(r"[^\W\d_]", termo):
        alvo = sem_acento(termo)
        nomes = inad["CLIENTE"].astype(str).map(sem_acento)
        return inad[nomes.str.contains(alvo, regex=False)]
    digitos = re.sub(r"\D", "", termo)
    if not digitos:
        return inad
    docs = inad["CPF_CNPJ"].astype(str).str.replace(r"\D", "", regex=True)
    return inad[docs.str.contains(digitos, regex=False)]


def tabela_por_contrato(inad: pd.DataFrame) -> pd.DataFrame:
    return (
        inad.groupby(CHAVE_CONTRATO, sort=False)
        .agg(
            SALDO=("SALDO", lambda s: sum(s, Decimal("0"))),
            PARCELAS=("SALDO", "size"),
            MAIOR_ATRASO=("DIAS_ATRASO", "max"),
        )
        .reset_index()
        .sort_values("SALDO", ascending=False)
    )


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


def cor_atraso(dias) -> str:
    if dias > 90:
        cor = COR_GRAVIDADE["Mais de 90 dias"]
        return f"background-color: {cor}; color: white"
    if dias > 30:
        cor = COR_GRAVIDADE["31 a 90 dias"]
        return f"background-color: {cor}; color: black"
    cor = COR_GRAVIDADE["Até 30 dias"]
    return f"background-color: {cor}; color: black"


def limpar_filtros():
    st.session_state.update(
        f_emp=[], f_faixa=[], f_tipo=[], f_busca="", f_data=regras.DATA_REF_PADRAO
    )


st.set_page_config(page_title="Inadimplência — Caprem", page_icon="📋", layout="wide")

try:
    df_base, qualidade = carregar()
except FileNotFoundError:
    st.error(
        "Não encontrei o arquivo de parcelas. Coloque o CSV na pasta `data` "
        f"({tratamento.ARQUIVO_PADRAO}) e atualize a página."
    )
    st.stop()
except ValueError as erro:
    st.error(f"Não foi possível ler o arquivo de parcelas: {erro}")
    st.stop()

if "f_data" not in st.session_state:
    st.session_state["f_data"] = regras.DATA_REF_PADRAO

with st.sidebar:
    st.header("Filtros")
    st.subheader("Data de referência")
    escolhida = st.date_input(
        "Calcular o atraso até",
        key="f_data",
        format="DD/MM/YYYY",
        min_value=date(2020, 1, 1),
        max_value=date(2035, 12, 31),
    )
    st.subheader("Buscar")
    termo = st.text_input(
        "Nome do cliente ou CPF/CNPJ",
        key="f_busca",
        placeholder="Ex.: maria ou 123.456.789-00",
    )
    st.subheader("Filtrar por")
    empreendimentos = st.multiselect(
        "Empreendimento", sorted(df_base["EMPREENDIMENTO"].unique()), key="f_emp"
    )
    faixas = st.multiselect("Faixa de atraso (dias)", regras.FAIXAS, key="f_faixa")
    tipos = st.multiselect(
        "Tipo de parcela",
        sorted(set(df_base["TIPO_PARCELA"].unique()) - {"FINANCIAMENTO"}),
        key="f_tipo",
    )
    st.button("Limpar filtros", on_click=limpar_filtros, width="stretch")

data_ref = escolhida or regras.DATA_REF_PADRAO
inad, resumo = calcular(data_ref)

st.title("Inadimplência — Cobrança")
st.caption(f"Data de referência: **{data_ref.strftime('%d/%m/%Y')}**")
if data_ref != regras.DATA_REF_PADRAO:
    st.caption(
        ":orange[Você está vendo outra data que não a do arquivo "
        f"({regras.DATA_REF_PADRAO.strftime('%d/%m/%Y')}).]"
    )

filtrado = buscar(inad, termo)
if empreendimentos:
    filtrado = filtrado[filtrado["EMPREENDIMENTO"].isin(empreendimentos)]
if faixas:
    filtrado = filtrado[filtrado["FAIXA_ATRASO"].isin(faixas)]
if tipos:
    filtrado = filtrado[filtrado["TIPO_PARCELA"].isin(tipos)]

if filtrado.empty:
    st.info(
        "Nenhuma parcela encontrada com esses filtros. "
        "Clique em “Limpar filtros” na barra lateral para ver tudo de novo."
    )
else:
    total = sum(filtrado["SALDO"], Decimal("0"))
    clientes = filtrado[["NUM_CONTRATO", "CLIENTE"]].drop_duplicates().shape[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total em atraso", moeda(total))
    c2.metric(
        "Clientes inadimplentes",
        inteiro(clientes),
        help="Conta cada contrato de cada cliente; quem tem dois contratos em atraso aparece duas vezes.",
    )
    c3.metric("Parcelas em atraso", inteiro(len(filtrado)))
    c4.metric("Atraso médio", f"{filtrado['DIAS_ATRASO'].mean():.0f} dias")
    st.caption(
        "Cores pelo tempo de atraso: :gray[cinza, até 30 dias] · "
        ":orange[âmbar, de 31 a 90 dias] · :red[vermelho, mais de 90 dias]."
    )

    graf = filtrado.assign(
        VALOR=filtrado["SALDO"].astype(float),
        GRAVIDADE=filtrado["FAIXA_ATRASO"].map(GRAVIDADE),
    )
    cor = alt.Color(
        "GRAVIDADE:N",
        scale=ESCALA_COR,
        sort=ORDEM_GRAVIDADE,
        legend=alt.Legend(title="Atraso"),
    )
    esquerda, direita = st.columns(2)

    esquerda.subheader("Saldo por empreendimento")
    por_emp = graf.groupby(["EMPREENDIMENTO", "GRAVIDADE"], as_index=False)["VALOR"].sum()
    esquerda.altair_chart(
        alt.Chart(por_emp)
        .mark_bar()
        .encode(
            y=alt.Y("EMPREENDIMENTO:N", title=None, sort="-x", axis=alt.Axis(labelLimit=260)),
            x=alt.X("VALOR:Q", title="Saldo em atraso (R$)"),
            color=cor,
            tooltip=[
                alt.Tooltip("EMPREENDIMENTO:N", title="Empreendimento"),
                alt.Tooltip("GRAVIDADE:N", title="Atraso"),
                alt.Tooltip("VALOR:Q", title="Saldo (R$)", format=",.2f"),
            ],
        ),
        width="stretch",
    )

    direita.subheader("Saldo por faixa de atraso")
    por_faixa = graf.groupby(["FAIXA_ATRASO", "GRAVIDADE"], as_index=False)["VALOR"].sum()
    direita.altair_chart(
        alt.Chart(por_faixa)
        .mark_bar()
        .encode(
            x=alt.X("FAIXA_ATRASO:N", title="Dias de atraso", sort=regras.FAIXAS),
            y=alt.Y("VALOR:Q", title="Saldo em atraso (R$)"),
            color=cor,
            tooltip=[
                alt.Tooltip("FAIXA_ATRASO:N", title="Faixa (dias)"),
                alt.Tooltip("VALOR:Q", title="Saldo (R$)", format=",.2f"),
            ],
        ),
        width="stretch",
    )

    st.subheader("Clientes em atraso")
    contratos = tabela_por_contrato(filtrado)
    saldos = contratos["SALDO"].astype(float)
    tabela = pd.DataFrame(
        {
            "Cliente": contratos["CLIENTE"],
            "Contrato": contratos["NUM_CONTRATO"],
            "Empreendimento": contratos["EMPREENDIMENTO"],
            "Unidade": contratos["UNIDADE"],
            "Telefone": contratos["TELEFONE"],
            "Parcelas em atraso": contratos["PARCELAS"],
            "Parcela mais antiga (dias de atraso)": contratos["MAIOR_ATRASO"],
            "Saldo devedor (R$)": saldos,
        }
    ).reset_index(drop=True)

    parte = (saldos / saldos.sum() * 100).to_numpy()
    exibicao = tabela.copy()
    exibicao["Saldo devedor (R$)"] = contratos["SALDO"].map(moeda).to_numpy()
    exibicao["Parte do total"] = parte
    estilo = exibicao.style.map(cor_atraso, subset=["Parcela mais antiga (dias de atraso)"])
    st.dataframe(
        estilo,
        hide_index=True,
        width="stretch",
        column_config={
            "Parte do total": st.column_config.ProgressColumn(
                "Parte do total",
                help="Quanto esse contrato representa do total em atraso mostrado.",
                format="%.1f%%",
                min_value=0.0,
                max_value=float(parte.max()),
            ),
            "Saldo devedor (R$)": st.column_config.TextColumn("Saldo devedor (R$)"),
        },
    )
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
    st.markdown(
        f"**Fora da cobrança (parcelas abertas com 4+ dias de atraso em "
        f"{data_ref.strftime('%d/%m/%Y')})**"
    )
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
