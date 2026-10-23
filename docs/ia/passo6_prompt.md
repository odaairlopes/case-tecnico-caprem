Escreva testes para regras.py com um DataFrame pequeno e feito à mão cobrindo:
parcela paga, aberta futura, aberta vencida, pagamento parcial, contrato
distratado, parcela original de acordo vs parcela de acordo, e a fronteira
exata data_ref == vencimento. Depois rode e mostre as falhas, sem ajustar os
testes para passar.

(Prompt do guia, passo 6. O guia pede pytest; o projeto usa unittest e o pytest
não estava instalado, então os testes foram escritos em unittest, que o pytest
também executa. As regras de carência de 4 dias e de faixas seguem as
premissas confirmadas, e não o prompt antigo do guia.)

Cobrir também, além do prompt do guia:

- 1 dia de atraso: "em compensação"; 3 dias: em compensação; 4 dias: inadimplente.
- Fronteiras das faixas 4-30, 31-60, 61-90, 91-180, >180 (30/31, 60/61, 90/91, 180/181).
- Contrato quitado e parcela de financiamento: fora e mostradas à parte.
- Prioridade entre motivos (distratado + financiamento = contrato não ativo).
- Faixa só para inadimplentes; saldo continua Decimal.
- Totais por contrato e por empreendimento.
- O DataFrame recebido não é alterado; data de referência padrão 25/09/2026.
  Não altere regras.py, tratamento.py, app.py nem as premissas.
