# Premissas adotadas

Documento vivo. Cada regra mostra de onde veio:

- **dados**: conferi no arquivo
- **decisão**: escolha minha, com motivo
- **confirmar**: depende da resposta da Cobrança (vale a decisão até lá)

Base: `parcelas_cobranca_2026-09-25.csv` (10.761 linhas, 3 empreendimentos).

## 1. Data de referência

| Regra                           | Decisão                                                                                   | Fonte   |
| ------------------------------- | ----------------------------------------------------------------------------------------- | ------- |
| Data usada para calcular atraso | 25/09/2026 (a data do arquivo), alterável na tela                                         | dados   |
| Motivo                          | O arquivo é um retrato daquele dia. Usar "hoje" muda os números sem os dados terem mudado | decisão |

## 2. O que é inadimplência

| Regra                                           | Decisão                                                      | Fonte     |
| ----------------------------------------------- | ------------------------------------------------------------ | --------- |
| Parcela inadimplente                            | Status ABERTA e vencimento **anterior** à data de referência | decisão   |
| Parcela que vence na própria data de referência | Não é inadimplente (ainda está no prazo)                     | decisão   |
| Parcela futura                                  | Não entra no "em atraso"                                     | decisão   |
| Carência (dias de tolerância)                   | Nenhuma. Atraso começa no dia seguinte ao vencimento         | confirmar |
| Faixas de atraso                                | 1–30, 31–60, 61–90, 91–180 e mais de 180 dias                | decisão   |

## 3. Quanto o cliente deve

| Regra                   | Decisão                                                      | Fonte   |
| ----------------------- | ------------------------------------------------------------ | ------- |
| Valor em atraso         | Saldo = valor da parcela − valor pago                        | decisão |
| Pagamento parcial       | Existem parcelas abertas com valor já pago; só o saldo conta | dados   |
| Juros, multa e correção | Fora. O valor mostrado é o de face, e a tela avisa isso      | decisão |

## 4. Situação do contrato

| Regra      | Decisão                                                         | Fonte     |
| ---------- | --------------------------------------------------------------- | --------- |
| ATIVO      | Único escopo de cobrança                                        | decisão   |
| DISTRATADO | Fora do total cobrável; valor mostrado à parte para conferência | confirmar |
| QUITADO    | Fora do total. Não há parcelas abertas nesses contratos         | dados     |

## 5. Acordos de renegociação

| Regra                                                | Decisão                                                                                      | Fonte     |
| ---------------------------------------------------- | -------------------------------------------------------------------------------------------- | --------- |
| Identificação                                        | Campo NUM_ACORDO preenchido, tanto nas parcelas originais quanto nas parcelas do tipo ACORDO | dados     |
| Dupla contagem                                       | Somar tudo contaria a dívida em dobro                                                        | dados     |
| Regra adotada                                        | Vale só a dívida das parcelas do tipo ACORDO; as originais com NUM_ACORDO ficam de fora      | confirmar |
| Acordo quebrado                                      | Parcela de acordo vencida e aberta é inadimplente, com marcação "acordo quebrado"            | decisão   |
| Se o acordo quebra, a dívida original volta a valer? | Não tratado nesta versão                                                                     | confirmar |

## 6. Tipos de parcela

| Regra                         | Decisão                                                                                  | Fonte     |
| ----------------------------- | ---------------------------------------------------------------------------------------- | --------- |
| MENSAL, INTERMEDIARIA, CHAVES | Contam normalmente; dá para filtrar por tipo                                             | decisão   |
| FINANCIAMENTO                 | Quem paga é o banco, não o cliente. Fica em filtro separado, fora do total "de clientes" | confirmar |

## 7. Qualidade dos dados

| Problema encontrado                                 | Tratamento                                            | Fonte   |
| --------------------------------------------------- | ----------------------------------------------------- | ------- |
| Datas em dois formatos (dd/mm/aaaa e aaaa-mm-dd)    | Detectar pelo padrão do texto; nunca assumir um só    | dados   |
| Valores em dois formatos ("3.625,00" e "2000.00")   | Idem                                                  | dados   |
| Status com caixa mista (PAGA, Paga, ABERTA, Aberta) | Padronizar para maiúsculas                            | dados   |
| 46 linhas duplicadas idênticas                      | Removidas e contadas no relatório de qualidade        | dados   |
| Arquivo em utf-8 com BOM                            | Ler com `utf-8-sig`                                   | dados   |
| Dado que não consegue ser lido                      | Para o processo com erro claro, em vez de virar vazio | decisão |
| Telefones começam todos com (00)                    | Mostrados como vieram, sem validar (dado fictício)    | dados   |

## 8. O que ficou de fora desta versão

- Juros, multa e correção monetária
- Percentual de inadimplência (falta definir a base de cálculo)
- Carência configurável e telas separadas para cada tipo de acordo
- Controle de acesso e LGPD (vai na nota técnica)

## 9. Perguntas em aberto para a Renata

1. Acordo: contar só as parcelas do acordo? Se o cliente quebrar, a dívida original volta a valer?
2. Contratos distratados com parcelas abertas ficam fora da cobrança?
3. Parcelas de financiamento (banco) entram na inadimplência do cliente ou ficam separadas?
4. Existe carência oficial depois do vencimento?
