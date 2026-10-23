# Passo 8 — resposta e resultado (dashboard inicial)

Criei [`app.py`](../../app.py) em Streamlit. Não alterei `regras.py`,
`tratamento.py`, `conferir.py`, `tests/` nem `docs/premissas.md`. Não reimplementei
nenhuma regra: o app usa `tratamento.carregar_dados()`,
`tratamento.relatorio_qualidade()` e `regras.calcular_inadimplencia()`.

## Como funciona

1. Carrega e calcula com `st.cache_data`, na data padrão `regras.DATA_REF_PADRAO`
   (25/09/2026, nunca hoje), mostrada no topo em dd/mm/aaaa.
2. Usa só as parcelas com `INADIMPLENTE = True`. Os filtros (empreendimento,
   faixa de atraso e tipo de parcela) são aplicados em sequência e valem para
   os cartões, os gráficos e a tabela.
3. Cartões: total em atraso, clientes (distintos por contrato + cliente),
   parcelas e atraso médio. O saldo é somado em `Decimal`; só vira número
   (`float`) para os gráficos e para o Excel.
4. Gráficos (Altair): saldo por empreendimento e por faixa, na ordem das faixas.
5. Tabela por contrato, em ordem decrescente de saldo, sem CPF/CNPJ.
6. Excel (openpyxl): mesmas colunas da tela, saldo numérico com formato
   `"R$" #,##0.00`.
7. Seção recolhível com a qualidade dos dados e os grupos fora da cobrança.
8. Sem resultado nos filtros: mensagem amigável e sem botão de Excel. Erro de
   carga (arquivo ausente ou dado inválido): mensagem clara, sem traceback.

## O que rodei

- `python -m py_compile app.py`: passou.
- Execução automática com `streamlit.testing.v1.AppTest`: sem exceções.
- Sem filtros: R$ 625.114,94, 134 parcelas, 30 clientes, atraso médio de 140 dias.
- Parque Azul: R$ 558.485,81, 104 parcelas, 18 clientes.
- Faixa >180: R$ 224.419,06, 44 parcelas. Faixa >180 + tipo MENSAL: R$ 139.294,06,
  39 parcelas.
- Filtros sem resultado (Jardim das Palmeiras + >180 + ACORDO): mensagem amigável,
  sem cartões e sem botão de download.
- Excel gerado pela função do app: 30 linhas (contratos), saldo numérico, soma
  R$ 625.114,94.
- Suíte de testes: 30 OK.

## O que não consegui verificar

- Não abri o app no navegador: sem prints e sem conferir o visual real.
- Não testei o clique de download nem abri o `.xlsx` no Excel; só li a planilha
  com `openpyxl`.
- Os 30 clientes não foram conferidos contra o gabarito.

## Correções durante a execução

- O Streamlit avisou que `use_container_width` será removido; troquei por
  `width="stretch"`.
- Ao reescrever o arquivo, um BOM foi adicionado no início e quebrava a leitura
  por `exec`; removi e o arquivo ficou em UTF-8 sem BOM.
