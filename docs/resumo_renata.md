# Painel de inadimplência: resumo para a Cobrança

Para: Renata Oliveira, Coordenação de Cobrança

## 1. O problema que entendi

Todo mês você tira o relatório do sistema e filtra na mão para saber quem está
devendo, quanto e de qual empreendimento. Isso demora e dá margem a erro,
principalmente porque a planilha mistura acordos, contratos distratados e
parcelas de financiamento.

## 2. O que a solução faz

O painel lê a mesma planilha que você exporta e mostra a inadimplência numa
tela só.

- **No topo:** total em atraso, clientes em atraso, parcelas em atraso e atraso
  médio em dias.
- **Filtros:** empreendimento, faixa de atraso (4 a 30, 31 a 60, 61 a 90, 91 a
  180 e mais de 180 dias) e tipo de parcela. Dá para combinar, e há um botão
  para limpar tudo.
- **Busca:** por nome do cliente ou por CPF/CNPJ. O CPF/CNPJ só serve para
  achar a pessoa. Ele não aparece na tela nem no Excel.
- **Gráficos:** saldo por empreendimento e por faixa de atraso. Cinza é até 30
  dias, âmbar de 31 a 90 e vermelho mais de 90.
- **Tabela por contrato**, do maior saldo para o menor: cliente, contrato,
  unidade, telefone, saldo, número de parcelas e a parcela mais antiga em atraso.
- **Excel:** um botão baixa a tabela como está na tela.
- **Conferência dos dados:** uma área que abre e fecha mostra o que foi lido e o
  que ficou fora da cobrança (em compensação, distratados, quitados,
  financiamento e parcelas originais de acordo). Serve para você comparar com o
  sistema.

Com a planilha de 25/09/2026, o painel mostra **134 parcelas em atraso, somando
R$ 625.114,94**. Fiz um segundo cálculo à parte, por outro caminho, e deu o mesmo
resultado.

**Para usar:**

1. Abra o painel (as instruções de instalação estão no README).
2. Escolha os filtros ou digite um nome.
3. Olhe a tabela ou clique em "Baixar tabela em Excel".

## 3. Premissas que adotei

**O que você confirmou:**

- A data de referência é 25/09/2026, a do arquivo. O atraso é contado a partir
  dela, e não do dia em que alguém abre o painel. Na tela dá para trocar a data,
  só para consulta.
- A parcela só conta como atraso a partir de 4 dias depois do vencimento. De 1 a
  3 dias ficam de fora, porque o boleto leva até 2 dias úteis para compensar. O
  painel mostra essas parcelas à parte, só como informação.
- Nos acordos, valem só as parcelas novas. As antigas ficam de fora para a dívida
  não contar duas vezes. Se o cliente não pagar o acordo, a cobrança continua nas
  parcelas do acordo.
- Contratos distratados ficam fora, porque já foram para o jurídico.
- Financiamento fica fora, porque é do Repasse.
- No contrato 2020156 (Vista do Horto), as parcelas repetidas contam uma vez só.

**O que decidi:**

- O valor em atraso é o valor da parcela menos o que já foi pago. Se o cliente
  pagou uma parte, entra só o que falta.
- Parcela que vence no dia da referência ainda não é atraso.
- Contratos quitados ficam fora. No arquivo, eles não têm parcela em aberto.
- "Clientes em atraso" conta cada contrato de cada cliente. Quem tem dois
  contratos em atraso aparece duas vezes.

**O que ainda precisa da sua confirmação:**

- Juros, multa e correção não entram. O valor mostrado é o da parcela, sem
  acréscimo. Se a Cobrança quiser incluir, precisamos combinar a regra.

## 4. O que ficou de fora desta versão

- Juros, multa e correção monetária.
- Percentual de inadimplência. Falta definir sobre qual valor calcular.
- Carência ajustável na tela. Hoje são 4 dias, fixos. Também não há telas
  separadas para cada tipo de acordo.
- Senha de acesso e regras de proteção de dados. O painel roda no computador de
  quem abre. Isso está na nota técnica para a TI.
- Padronização dos nomes de clientes. No Loteamento Vista do Horto os nomes vêm
  em maiúsculas, e a mesma pessoa pode aparecer escrita de dois jeitos. Por isso
  o número de clientes pode estar um pouco acima do real.
