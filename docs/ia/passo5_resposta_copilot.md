# Passo 5 — resposta e resultado

Criei [`regras.py`](../../regras.py) com `calcular_inadimplencia(df, data_ref=DATA_REF_PADRAO)`.
`DATA_REF_PADRAO` é `date(2026, 9, 25)`; a função nunca usa a data de hoje.
Não alterei `tratamento.py`, `app.py`, `docs/premissas.md` nem criei testes.

## Como funciona

1. Copia o DataFrame (o original não é alterado) e calcula `DIAS_ATRASO`
   (data de referência menos vencimento, em dias corridos) e `SALDO`
   (valor da parcela menos valor pago, em `Decimal`).
2. Atribui **um motivo por parcela**, na ordem pedida: contrato não ativo,
   financiamento, parcela original de acordo, paga, ainda não venceu, em
   compensação (1 a 3 dias) e inadimplente (4 dias ou mais). Os motivos são
   aplicados da última regra para a primeira, para que a de maior prioridade
   prevaleça.
3. Para as inadimplentes, define a faixa: 4-30, 31-60, 61-90, 91-180 e >180.
4. Devolve um dicionário com `parcelas`, `por_contrato`, `por_empreendimento`
   e `resumo`. Nos grupos "fora da cobrança" do resumo, só entram parcelas
   ABERTAS com 4 dias de atraso ou mais.

## Resultado no CSV real (data de referência 25/09/2026)

Total inadimplente: 134 parcelas, R$ 625.114,94.

| Contrato | Saldo inadimplente | Gabarito |
|---|---:|---:|
| 1010533 | R$ 0,00 | R$ 0,00 |
| 1010638 | R$ 15.932,32 | R$ 15.932,32 |
| 1010436 | R$ 0,00 | R$ 0,00 |
| 2020156 | R$ 2.750,00 | R$ 2.750,00 |

Por empreendimento: Edifício Parque Azul 104 parcelas (R$ 558.485,81);
Loteamento Vista do Horto 22 (R$ 50.802,67); Residencial Jardim das Palmeiras
8 (R$ 15.826,46).

À parte: em compensação 17 parcelas (R$ 93.746,39); distratados 68
(R$ 644.329,32); quitados 0; financiamento 6 (R$ 1.201.500,00); parcelas
originais de acordo 31 (R$ 138.099,99).

## Verificações feitas

- O DataFrame de entrada ficou com as mesmas colunas após a chamada.
- Todos os saldos são `Decimal`.
- O menor atraso entre as inadimplentes é 5 dias.
- Fronteiras das faixas: no CSV real só o atraso de 181 dias aparece (faixa
  `>180`, correto). Os atrasos 30, 31, 60, 61, 90 e 91 **não existem nos dados**,
  então essas fronteiras e a de 3/4 dias **ainda não foram testadas**. Isso fica
  para o passo 6, com testes feitos à mão.
