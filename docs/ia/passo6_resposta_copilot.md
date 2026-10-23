# Passo 6 — resposta e resultado

Preenchi [`tests/test_regras.py`](../../tests/test_regras.py) com 19 testes em
`unittest`, usando DataFrames pequenos feitos à mão (função auxiliar
`parcela(dias, **campos)`). Não alterei `regras.py` nem ajustei teste para
passar. O `pytest` também executa estes testes.

## O que os testes cobrem

- Pedidos do guia: parcela paga, aberta futura, aberta vencida, pagamento
  parcial (6.117,65 − 2.420,63 = 3.697,02), contrato distratado, original de
  acordo versus parcela ACORDO e vence na data de referência (0 dia).
- Além do guia: contrato quitado, financiamento, 1 dia (em compensação),
  3 dias (em compensação) e 4 dias (inadimplente), fronteiras das faixas
  (30/31, 60/61, 90/91, 180/181), faixa só para inadimplentes, prioridade entre
  motivos, totais por contrato e empreendimento, saldo em `Decimal`,
  DataFrame de entrada não alterado e data de referência padrão 25/09/2026.

## Resultado

Suíte inteira: 30 testes OK (19 novos e 11 de `tratamento.py`). Nenhuma
falha na primeira execução.

## Teste de mutação

Troquei `dias < CARENCIA_DIAS` por `dias <= CARENCIA_DIAS` em `regras.py`.
Dois testes falharam:

- `test_fronteira_carencia_3_dias_fora_e_4_dias_dentro`
- `test_fronteiras_das_faixas` (caso de 4 dias)

Voltei a linha ao original e a suíte voltou a 30 OK. Uma primeira tentativa não
valeu, porque o teste e a restauração rodaram no mesmo comando; foi refeita em
sequência.

## Limites

- Os dados são pequenos e criados à mão; o CSV real foi conferido no passo 5.
- Só uma regra foi quebrada de propósito. As demais não foram testadas dessa forma.
- O `pytest` não estava instalado; foi instalado depois por você.
