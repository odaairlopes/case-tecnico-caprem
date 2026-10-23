# Passo 7 — resposta e resultado

Criei [`conferir.py`](../../conferir.py) na raiz. Não alterei `regras.py`,
`tratamento.py`, `app.py` nem as premissas.

## Como funciona

1. Lê o CSV com `tratamento.carregar_dados()` e calcula **sem usar `regras.py`**:
   filtra em sequência contrato ATIVO, tipo diferente de FINANCIAMENTO, status
   ABERTA, fora as parcelas originais de acordo e atraso de 4 dias ou mais
   (data de referência 25/09/2026). O saldo é `VALOR_PARCELA − VALOR_PAGO` em
   `Decimal`. Soma parcelas, contratos distintos e saldo por empreendimento.
2. Só depois importa `calcular_inadimplencia` de `regras.py` (importação dentro
   de `main`, após o cálculo) e compara, por empreendimento e no total geral.
3. Imprime a tabela conferir | regras | diferença, lista as divergências e
   sai com código 0 (sem divergência) ou 1 (com divergência).

## Resultado (executado no CSV real)

Sem divergência. Código de saída 0.

| Empreendimento | Parcelas | Contratos | Saldo |
|---|---:|---:|---:|
| Edifício Parque Azul | 104 | 18 | R$ 558.485,81 |
| Loteamento Vista do Horto | 22 | 9 | R$ 50.802,67 |
| Residencial Jardim das Palmeiras | 8 | 3 | R$ 15.826,46 |
| **Total** | **134** | | **R$ 625.114,94** |

Evidência: [`docs/evidencias/conferencia.txt`](../evidencias/conferencia.txt).

## Limites

- A conferência usa as mesmas regras escritas por mim (Copilot), a partir do
  mesmo texto de premissas; se a premissa estiver errada, os dois erram juntos.
  A prova independente continua sendo o gabarito manual do passo 3.
- Os dois lados usam o mesmo `tratamento.py`; erro de leitura do CSV não seria
  detectado aqui.
- A divergência foi testada depois, de propósito: `CARENCIA` 4→3 não divergiu
  (o CSV não tem parcelas com 3 dias; as 17 em compensação têm 2); 4→2 divergiu
  (151 contra 134 parcelas, diferença de R$ 93.746,39), com código de saída 1.
  Evidência em [`conferencia_mutacao.txt`](../evidencias/conferencia_mutacao.txt).
