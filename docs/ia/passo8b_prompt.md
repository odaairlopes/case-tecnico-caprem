Refine o app.py que já existe (passo anterior). Não altere regras.py,
tratamento.py, conferir.py, tests/ nem docs/premissas.md, e não mude nenhuma
regra de cálculo. Tudo que já funciona (cartões, filtros, gráficos, tabela,
exportação e seção de qualidade) deve continuar igual em números: com a data
padrão e sem filtros, 134 parcelas e R$ 625.114,94.

Layout e filtros:
- st.set_page_config com layout "wide" e título da página em português.
- Barra lateral com os filtros agrupados sob títulos: "Data de referência",
  "Buscar" e "Filtrar por" (empreendimento, faixa de atraso, tipo de parcela).
  Botão "Limpar filtros" que volta ao estado inicial.

Data de referência:
- Seletor de data (st.date_input) com padrão regras.DATA_REF_PADRAO
  (25/09/2026), nunca hoje. Ao mudar, recalcule com
  regras.calcular_inadimplencia(df, data_ref); não reimplemente regras.
  Exiba a data no topo em dd/mm/aaaa. Se a data escolhida for diferente da
  padrão, mostre um aviso discreto: "Você está vendo outra data que não a do
  arquivo (25/09/2026)".

Busca:
- Campo de texto para buscar por nome do cliente (sem diferenciar maiúsculas,
  minúsculas e acentos) ou por CPF/CNPJ (aceite com ou sem pontos e traços).
  Ela se combina com os demais filtros.
- Não exiba CPF/CNPJ em nenhuma tela nem na exportação; use-o só para buscar.

Formatação e cores:
- Moeda sempre em R$ no padrão brasileiro (R$ 1.234,56), datas em dd/mm/aaaa.
  Decimal só vira número para exibir, nunca nos cálculos.
- Cores consistentes em todo o app: vermelho para atraso grave (mais de 90
  dias), âmbar para médio (31 a 90 dias) e cinza neutro para o restante
  (4 a 30 dias). Use as mesmas cores nos gráficos por faixa e na tabela, e
  uma legenda curta explicando. Isso é só visual; não altera as faixas de
  atraso da regra (4-30, 31-60, 61-90, 91-180, >180).
- Tabela com barra de progresso na coluna de saldo (st.column_config), ordenada
  por saldo e com cabeçalhos em português claro. Mantenha o botão de exportar
  para Excel com os mesmos dados da tela (saldo como número, formato de moeda).

Estados e clareza:
- Quando os filtros ou a busca não retornarem nada, mostre uma mensagem amigável
  (ex.: "Nenhuma parcela encontrada com esses filtros") com a sugestão de limpar
  os filtros, no lugar de gráficos e tabela vazios, e desabilite a exportação.
- Rótulos e textos sem jargão técnico, pensando em uma pessoa não técnica.
- Mantenha o tratamento de erro de carga (mensagem clara, sem traceback) e a
  seção recolhível de qualidade dos dados.

Ao final, rode `python -m py_compile app.py`, confirme se o app sobe sem erro e
reporte exatamente o que rodou e o que não conseguiu verificar.

(Prompt de refinamento do guia, passo 8, revisado: o do guia não dizia para
manter os números, não exibir CPF, nem que as cores não alteram as faixas da
regra.)
