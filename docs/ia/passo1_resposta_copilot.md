# Ambiguidades de regra de negócio e premissas propostas

Não gerei código, como você pediu. Todas as premissas abaixo são propostas para a Cobrança validar. Cada uma deve ficar configurável ou documentada em premissas.md.

## 1. Definição de inadimplência

| Ambiguidade                            | Premissa proposta                                                                                                                     |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| O que é parcela vencida?               | DT_VENCIMENTO < data de referência e saldo em aberto > 0.                                                                             |
| Data de referência                     | Parâmetro, com padrão "hoje". Permite também uma data de corte (ex.: fechamento do mês).                                              |
| Tolerância                             | Atraso de 0 dias = vencida. Aceitar um parâmetro de carência (ex.: 5 dias) que fica desligado por padrão.                             |
| Vencimento em fim de semana ou feriado | Não ajustar. Usa-se a data do arquivo.                                                                                                |
| Cliente inadimplente                   | Cliente com pelo menos uma parcela vencida em aberto. A unidade de análise principal é o contrato, e o cliente agrega seus contratos. |
| Faixas de atraso                       | 1–30, 31–60, 61–90, 91–180 e mais de 180 dias. Faixas editáveis.                                                                      |

## 2. Pagamento parcial

| Ambiguidade                      | Premissa proposta                                                                                                                   |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Valor em aberto                  | VALOR_PARCELA − VALOR_PAGO (nulo = 0). O valor devido é o saldo, não o valor cheio.                                                 |
| Pago a mais                      | Saldo negativo vira 0. Sinalizar como "crédito" em uma lista de exceções.                                                           |
| Tolerância de centavos           | Saldo ≤ R$ 0,01 conta como quitado.                                                                                                 |
| STATUS_PARCELA contra os valores | Os valores e datas são a fonte da verdade. O status é apenas conferência. Divergências vão para um relatório de qualidade de dados. |
| Parcela paga em atraso           | Não é inadimplência atual, mas serve para histórico de pontualidade.                                                                |

## 3. Juros, multa e correção

O arquivo não traz encargos. Premissa: o dashboard mostra o valor de face em aberto, sem juros, multa ou correção monetária (INCC, IGP-M). Isso fica explícito na tela, porque o valor para negociação será maior. Se a Cobrança quiser valor atualizado, precisa informar o índice e as regras do contrato.

## 4. Acordos

| Ambiguidade                                       | Premissa proposta                                                                                                                                                                                   |
| ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Parcelas originais renegociadas e parcelas ACORDO | Há risco de dupla contagem. As parcelas originais que entraram em acordo (têm NUM_ACORDO ou status "renegociada") saem da inadimplência. Passa a valer a dívida das parcelas TIPO_PARCELA = ACORDO. |
| Acordo em dia                                     | A parcela do acordo não vencida não é inadimplente, e o contrato aparece como "em acordo".                                                                                                          |
| Acordo quebrado                                   | Parcela de acordo vencida e em aberto é inadimplência, com marcação "acordo quebrado".                                                                                                              |
| Como identificar a parcela original renegociada   | Preciso confirmar com você. Verificar se STATUS_PARCELA tem um valor como "RENEGOCIADA" ou "CANCELADA POR ACORDO". Sem isso, a regra depende apenas de NUM_ACORDO preenchido na própria parcela.    |
| Visão separada                                    | Mostrar três blocos: inadimplência "pura", em acordo em dia e acordo quebrado.                                                                                                                      |

## 5. Contratos distratados e quitados

| Ambiguidade                   | Premissa proposta                                                                                                                                                           |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DISTRATADO                    | Excluído da inadimplência. O contrato foi encerrado e as parcelas em aberto não são cobráveis. Pode aparecer em uma aba à parte, "Distratados com saldo", para conferência. |
| QUITADO com parcela em aberto | É inconsistência de dados. Excluir do cálculo e listar nas exceções.                                                                                                        |
| ATIVO                         | Único escopo de cobrança.                                                                                                                                                   |

## 6. Tipos de parcela

| Ambiguidade            | Premissa proposta                                                                                                                                                                                                 |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| FINANCIAMENTO          | A parcela é paga pelo banco, não pelo cliente. Atraso aqui é do repasse ou da liberação, não do cliente. Separar do total de inadimplência de clientes, ou ao menos permitir filtrar. Padrão: exibir em separado. |
| CHAVES e INTERMEDIARIA | Contam como inadimplência normal. Permitir o filtro por tipo, pois o perfil de cobrança é diferente.                                                                                                              |
| Parcelas futuras       | Não entram em "devido". Podem aparecer em um indicador à parte, "a vencer", como contexto.                                                                                                                        |

## 7. Qualidade de dados e identificação

| Ambiguidade                                 | Premissa proposta                                                                                                                                 |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Chave única da parcela                      | COLIGADA + NUM_CONTRATO + TIPO_PARCELA + NUM_PARCELA. Duplicatas são sinalizadas, e o padrão é manter a última ocorrência.                        |
| Identidade do contrato                      | NUM_CONTRATO só é único dentro da coligada. Usar COLIGADA + NUM_CONTRATO.                                                                         |
| Cliente com vários contratos                | Agrupar por CPF_CNPJ normalizado (apenas dígitos). Se o CPF estiver vazio, agrupar por nome e sinalizar.                                          |
| Formatos                                    | Datas em dd/mm/aaaa. Valores com vírgula decimal e possível separador de milhar. Ler o CSV em latin-1 ou utf-8-sig e tentar as duas codificações. |
| DT_PAGAMENTO sem VALOR_PAGO, ou o contrário | Vai para o relatório de exceções. O valor pago prevalece.                                                                                         |
| Telefone                                    | Exibir como veio, sem validar. Contém dado pessoal, então a tela deve ser de acesso restrito (LGPD).                                              |

## 8. Visão para a coordenadora

Indicadores principais: total em atraso (R$), nº de clientes, nº de contratos e faixa de atraso mais comum.
Quebras: por empreendimento (e coligada), por faixa de atraso e por tipo de parcela.
Ranking: clientes por valor devido, com telefone, empreendimento, unidade e dias de atraso máximo.
Percentual de inadimplência: vencido em aberto ÷ total vencido no período. Isso exige confirmar a base de cálculo, que pode ser a carteira vencida ou o total faturado.
Exportação: botão para baixar Excel/CSV da lista filtrada, que será o uso mais frequente.
Linguagem: sem termos técnicos nem siglas na tela.

## Perguntas que mais mudam o resultado

Quais valores existem em STATUS_PARCELA, e como uma parcela renegociada é marcada?
Parcelas de FINANCIAMENTO devem entrar no total de inadimplência ou ficar separadas?
Distratados ficam fora de vez, ou a Cobrança quer vê-los?
Existe carência (dias de tolerância) oficial?
O dashboard deve mostrar valor de face ou valor atualizado com encargos?
Você tem um CSV de exemplo (mesmo anonimizado) para validar formatos e valores reais?
Confirme ou ajuste essas premissas, principalmente as perguntas 1 a 3, e eu registro tudo em docs\premissas.md antes de começar o código.
