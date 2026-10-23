Crie app.py em Streamlit para a coordenadora de Cobrança (pessoa não técnica).
Rodará localmente com `streamlit run app.py`. Não altere regras.py,
tratamento.py, conferir.py, tests/ nem docs/premissas.md. Se precisar de algo
que falta neles, avise em vez de mudar.

Dados e regras:
- Carregue com tratamento.carregar_dados() e calcule com
  regras.calcular_inadimplencia(df, data_ref). Não reimplemente nenhuma regra.
  Use só as parcelas com INADIMPLENTE = True e as colunas que o retorno de
  "parcelas" já traz (DIAS_ATRASO, SALDO, FAIXA_ATRASO, MOTIVO).
- Data de referência padrão: regras.DATA_REF_PADRAO (25/09/2026), nunca hoje.
  Mostre-a de forma visível no topo, em dd/mm/aaaa.
- Valores monetários são Decimal: não converta para float nos cálculos.
  Converta só para exibir, e formate em R$ no padrão brasileiro (R$ 1.234,56).
- Use st.cache_data para carregar e calcular, para os filtros ficarem rápidos.

Topo (cartões): total em atraso (R$), nº de clientes inadimplentes (clientes
distintos, por NUM_CONTRATO + CLIENTE), nº de parcelas e atraso médio em dias.
Com os filtros sem seleção, devem bater com o resumo: 134 parcelas e
R$ 625.114,94.

Filtros (barra lateral): empreendimento, faixa de atraso (4-30, 31-60, 61-90,
91-180, >180) e tipo de parcela (TIPO_PARCELA). Cada um deve funcionar sozinho
e combinado com os outros. Os cartões, os gráficos e a tabela refletem os filtros.

Visões:
- Gráfico de saldo por empreendimento.
- Gráfico de saldo por faixa de atraso, na ordem natural das faixas.
- Tabela por contrato, ordenada por saldo (maior primeiro), com: cliente,
  contrato, unidade, telefone, saldo devedor (R$), nº de parcelas e a parcela
  mais antiga em atraso (maior atraso, em dias). Não mostre CPF_CNPJ.

Exportação: botão para baixar em Excel (openpyxl) a tabela filtrada, com os
mesmos dados e colunas da tela. No Excel, saldo como número (não texto) e
formato de moeda.

Mensagens e estados:
- Rótulos em português claro, sem jargão técnico (nada de "DataFrame", "MOTIVO"
  ou nomes de coluna do banco).
- Se os filtros não retornarem nada, mostre uma mensagem amigável no lugar de
  gráficos e tabela vazios, e desabilite a exportação.
- Se o CSV não for encontrado ou tratamento.py levantar erro, mostre uma
  mensagem clara com a causa (linha e coluna, se houver) e pare, sem
  traceback.

Seção recolhível (st.expander): relatório de qualidade dos dados, usando
tratamento.relatorio_qualidade(df) (linhas lidas, duplicatas removidas, linhas
finais, datas e valores inválidos, linhas por empreendimento) e, à parte, o
resumo de "fora da cobrança" de regras (em compensação, distratados, quitados,
financiamento e originais de acordo), para a coordenadora conferir com o sistema.

Ao final, rode `python -m py_compile app.py` e, se possível, confirme que o app
sobe sem erro. Reporte o que rodou e o que não conseguiu verificar.

(Prompt do guia, passo 8, revisado: o guia pedia busca por CPF e seletor de
data só no refinamento; aqui os dados e as regras vêm de tratamento.py e
regras.py, com os totais esperados do passo 5.)
