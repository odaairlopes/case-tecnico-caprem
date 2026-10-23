Escreva conferir.py na raiz do projeto, para conferir de forma independente o
total em atraso por empreendimento.

Independência:

- Para o cálculo, NÃO importe regras.py. Use só pandas básico e o CSV tratado
  por tratamento.carregar_dados() (datas em datetime, valores em Decimal).
- Escreva a lógica do seu jeito (filtros e somas diretas), sem copiar a
  estrutura de regras.py.

Regras confirmadas pela Cobrança (data de referência 25/09/2026, nunca hoje):

- Dias de atraso = data_ref − DT_VENCIMENTO. Saldo = VALOR_PARCELA − VALOR_PAGO (Decimal).
- Entra: contrato ATIVO, TIPO_PARCELA diferente de FINANCIAMENTO, STATUS ABERTA,
  atraso >= 4 dias, e que não seja parcela original de acordo
  (TIPO_PARCELA diferente de ACORDO com NUM_ACORDO preenchido).
- Fora: distratado, quitado, financiamento, original de acordo, paga, a vencer,
  e 1 a 3 dias (em compensação).

Comparação:

- Só depois de calcular, importe calcular_inadimplencia de regras.py e compare,
  por empreendimento: nº de parcelas, nº de contratos e saldo total, mais o total geral.
- Imprima uma tabela lado a lado (conferir | regras | diferença) e liste cada
  divergência. Se não houver, diga "sem divergência" e mostre os totais.
- Saia com código 1 se houver divergência e 0 se não houver.
- Não altere regras.py, tratamento.py, app.py nem as premissas. Não ajuste nada
  para forçar a igualdade; reporte exatamente o que sair.
