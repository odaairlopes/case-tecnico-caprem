# Premissas adotadas

Cada regra mostra de onde veio:

- **dados**: conferi no arquivo
- **decisão**: escolha minha, com motivo
- **confirmar**: depende da resposta da Cobrança (vale a decisão até lá)

Base: `parcelas_cobranca_2026-09-25.csv` (10.761 linhas, 3 empreendimentos).

## 1. Data de referência

| Regra                           | Decisão                                                                                   | Fonte   |
| ------------------------------- | ----------------------------------------------------------------------------------------- | ------- |
| Data usada para calcular atraso | 25/09/2026 (data do arquivo), alterável na tela                                           | dados   |
| Motivo                          | O arquivo é um retrato daquele dia. Usar "hoje" muda os números sem os dados terem mudado | decisão |

## 2. O que é inadimplência

| Regra                             | Decisão                                                        | Fonte   |
| --------------------------------- | -------------------------------------------------------------- | ------- |
| Parcela inadimplente              | ABERTA, com **4 ou mais dias de atraso** na data de referência | Renata  |
| Dias de atraso                    | data de referência − vencimento (dias corridos)                | decisão |
| Parcelas com 1 a 3 dias de atraso | Fora do total ("em compensação"); só informativo               | Renata  |
| Faixas de atraso                  | 4–30, 31–60, 61–90, 91–180 e mais de 180 dias                  | decisão |

## 3. Quanto o cliente deve

| Regra                   | Decisão                                                      | Fonte   |
| ----------------------- | ------------------------------------------------------------ | ------- |
| Valor em atraso         | Saldo = valor da parcela − valor pago                        | decisão |
| Pagamento parcial       | Existem parcelas abertas com valor já pago; só o saldo conta | dados   |
| Juros, multa e correção | Fora. O valor mostrado é o de face, e a tela avisa isso      | decisão |

## 4. Situação do contrato

| Regra      | Decisão                                                 | Fonte   |
| ---------- | ------------------------------------------------------- | ------- |
| ATIVO      | Único escopo de cobrança                                | decisão |
| DISTRATADO | Fora da cobrança (já no jurídico)                       | Renata  |
| QUITADO    | Fora do total. Não há parcelas abertas nesses contratos | dados   |

## 5. Acordos de renegociação

| Regra                                                | Decisão                                                                             | Fonte     |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------- | --------- |
| Identificação                                        | Campo NUM_ACORDO preenchido, tanto nas parcelas originais quanto nas do tipo ACORDO | dados     |
| Dupla contagem                                       | Somar tudo contaria a dívida em dobro                                               | dados     |
| Regra adotada                                        | Só as parcelas do tipo ACORDO; as originais com NUM_ACORDO ficam de fora            | Renata    |
| Acordo quebrado                                      | A cobrança continua nas parcelas do acordo; a dívida original não volta             | Renata    |
| Se o acordo quebra, a dívida original volta a valer? | Não tratado nesta versão                                                            | confirmar |

- O Residencial Jardim das Palmeiras não tem acordos.

## 6. Tipos de parcela

| Regra                         | Decisão                                                                         | Fonte   |
| ----------------------------- | ------------------------------------------------------------------------------- | ------- |
| MENSAL, INTERMEDIARIA, CHAVES | Contam normalmente; dá para filtrar por tipo                                    | decisão |
| FINANCIAMENTO                 | Fora da cobrança (é do Repasse; o cliente não pode receber ligação da Cobrança) | Renata  |

## 7. Qualidade dos dados

| Problema encontrado                                 | Tratamento                                                           | Fonte   |
| --------------------------------------------------- | -------------------------------------------------------------------- | ------- |
| Datas em dois formatos (dd/mm/aaaa e aaaa-mm-dd)    | Apenas no 'Loteamento Vista do Horto'; detectar pelo padrão do texto | dados   |
| Valores em dois formatos ("3.625,00" e "2000.00")   | Apenas no 'Loteamento Vista do Horto'; detectar pelo padrão do texto | dados   |
| Status com caixa mista (PAGA, Paga, ABERTA, Aberta) | Apenas no 'Loteamento Vista do Horto'; detectar pelo padrão do texto | dados   |
| Duplicata do contrato 2020156                       | Contar uma vez só (colagem repetida na exportação)                   | Renata  |
| Arquivo em utf-8 com BOM                            | Ler com `utf-8-sig`                                                  | dados   |
| Dado que não consegue ser lido                      | Para com erro claro, em vez de virar vazio                           | decisão |
| Telefones começam todos com (00)                    | Mostrados como vieram, sem validar (dado fictício)                   | dados   |

## 8. O que ficou de fora desta versão

- Juros, multa e correção monetária
- Percentual de inadimplência (falta definir a base de cálculo)
- Carência configurável e telas separadas para cada tipo de acordo
- Controle de acesso e LGPD (vai na nota técnica)
