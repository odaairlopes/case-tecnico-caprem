# Gabarito manual dos contratos

## Critérios da conferência

Os valores abaixo foram conferidos manualmente com apoio do script `conferir_parcelas.py` e revisão das linhas indicadas nas evidências. A data de referência é **25/09/2026**. Para este gabarito, entram na cobrança parcelas em aberto com pelo menos **4 dias corridos de atraso**; quando há pagamento parcial, considera-se o saldo da parcela (valor da parcela menos valor pago).

As evidências detalhadas de cada contrato estão em [`docs/evidencias/`](./evidencias/).

## Contrato 1010533 — acordo AC-2026-0046

**Total em atraso: R$ 0,00.**

As linhas 1118, 1119 e 1139 são parcelas originais em aberto, vencidas e renegociadas no acordo AC-2026-0046. Por isso, não são cobradas junto com as parcelas do acordo: a dívida original foi substituída. Das 7 parcelas do acordo, 3 já foram pagas e a próxima vence em 05/10/2026; portanto, nenhuma parcela do acordo estava vencida na data de referência.

**Conferência do risco:** se as três parcelas originais fossem contadas indevidamente, o total seria R$ 19.125,00 (R$ 2.812,50 + R$ 2.812,50 + R$ 13.500,00). Esse é o erro que a implementação de `regras.py` deve evitar.

Evidência: [`gabarito_1010533.txt`](./evidencias/gabarito_1010533.txt).

## Contrato 1010638

**Total em atraso: R$ 15.932,32.**

As três parcelas abertas e vencidas passam do limite mínimo de atraso e entram pelo saldo devido:

| Linha | Parcela  | Vencimento | Dias de atraso |       Valor |        Pago | Saldo considerado |
| ----: | -------- | ---------- | -------------: | ----------: | ----------: | ----------------: |
|  1983 | MENSAL 1 | 15/07/2026 |             72 | R$ 6.117,65 |     R$ 0,00 |       R$ 6.117,65 |
|  1984 | MENSAL 2 | 15/08/2026 |             41 | R$ 6.117,65 | R$ 2.420,63 |       R$ 3.697,02 |
|  1985 | MENSAL 3 | 15/09/2026 |             10 | R$ 6.117,65 |     R$ 0,00 |       R$ 6.117,65 |

**Soma conferida:** R$ 6.117,65 + R$ 3.697,02 + R$ 6.117,65 = **R$ 15.932,32**. A linha 1984 tem pagamento parcial, então apenas o saldo de R$ 3.697,02 é contado. As linhas 1986 a 2002 ainda não venceram; a linha 2003 é financiamento e fica fora da cobrança por pertencer ao Repasse.

Evidência: [`gabarito_1010638.txt`](./evidencias/gabarito_1010638.txt).

## Contrato 1010436

**Total em atraso: R$ 0,00.**

Nenhuma linha entra na cobrança. A única parcela aberta já vencida é a linha 248 (MENSAL 7), com vencimento em 23/09/2026 e **2 dias de atraso** na data de referência. Como o mínimo para cobrança é 4 dias, ela fica fora.

As linhas 242 a 247 e 263 já foram pagas; as linhas 249 a 266 ainda não venceram; e a linha 267 é financiamento, excluído por pertencer ao Repasse.

Evidência: [`gabarito_1010436.txt`](./evidencias/gabarito_1010436.txt).

## Contrato 2020156

**Total em atraso: R$ 2.750,00.**

A linha 6464 (MENSAL 36), com vencimento em 23/08/2026, está aberta e tem **33 dias de atraso**. Seu saldo de R$ 2.750,00 entra integralmente na cobrança.

A linha 6465 também está aberta, mas tem apenas **2 dias de atraso**, abaixo do mínimo de 4 dias, e não entra. As linhas 6429 a 6463 já foram pagas e as linhas 6466 a 6500 ainda não venceram. A exportação também contém cópias duplicadas das linhas 6435 a 6480 (linhas 10717 a 10762); essas repetições devem ser contadas uma única vez, inclusive a cópia da linha 6464.

**Soma conferida:** R$ 2.750,00.

Evidência: [`gabarito_2020156.txt`](./evidencias/gabarito_2020156.txt).
