Crie regras.py com a função calcular_inadimplencia(df, data_ref=DATA_REF_PADRAO),
com DATA_REF_PADRAO = date(2026, 9, 25) (a data do arquivo, nunca hoje).
O df é o resultado de tratamento.carregar_dados(): datas em datetime e
valores monetários em Decimal. Não altere o df recebido, nem tratamento.py,
app.py ou docs/premissas.md.

Regras confirmadas pela Cobrança (documente cada uma em docstring):
- Dias de atraso = data_ref − DT_VENCIMENTO, em dias corridos.
- Saldo devedor = VALOR_PARCELA − VALOR_PAGO. Use Decimal; não converta para float.
- Cada parcela recebe UM motivo, avaliado nesta ordem (o primeiro que valer):
  1. SITUACAO_CONTRATO diferente de ATIVO (DISTRATADO e QUITADO) → fora da cobrança.
  2. TIPO_PARCELA = FINANCIAMENTO → fora da cobrança (é do Repasse).
  3. TIPO_PARCELA diferente de ACORDO e NUM_ACORDO preenchido → fora
     (parcela original renegociada; vale só a dívida das parcelas ACORDO).
  4. STATUS_PARCELA = PAGA → fora.
  5. Dias de atraso <= 0 (vence hoje ou no futuro) → fora, ainda não venceu.
  6. Dias de atraso de 1 a 3 → fora do total, "em compensação".
  7. Dias de atraso >= 4 → inadimplente: entra no total.
- Faixas de atraso, só para as inadimplentes: 4-30, 31-60, 61-90, 91-180, >180.
  Cuidado com as fronteiras (30/31, 60/61, 90/91, 180/181).

Retorno: um dicionário com
- "parcelas": DataFrame por parcela, com as colunas originais mais
  DIAS_ATRASO, SALDO, MOTIVO (texto), INADIMPLENTE (bool) e FAIXA_ATRASO.
- "por_contrato": uma linha por contrato inadimplente (EMPREENDIMENTO,
  NUM_CONTRATO, UNIDADE, CLIENTE, TELEFONE), com quantidade de parcelas,
  saldo total e maior atraso.
- "por_empreendimento": quantidade de parcelas, de contratos e saldo total.
- "resumo": total inadimplente e, à parte, quantidade e saldo de: em
  compensação (1 a 3 dias), distratados, quitados e financiamento. Nos
  grupos "fora da cobrança", some só parcelas ABERTAS com atraso >= 4,
  para ser comparável ao total e sem contar parcelas futuras.

Ao final, rode a função no CSV real e mostre os totais dos contratos
1010533, 1010638, 1010436 e 2020156. Reporte exatamente o que saiu,
mesmo que diferente do esperado. Não ajuste nada para forçar um resultado.
Não crie testes neste passo.
