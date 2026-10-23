# Painel de inadimplência: resumo para a Cobrança

Para: Renata Oliveira, Coordenação de Cobrança

## 1. O problema que entendi

Todo mês você tira o relatório do sistema e filtra tudo na mão para descobrir
quem está devendo, quanto e de qual empreendimento. Isso toma tempo e é fácil
errar, principalmente com acordos, contratos distratados e parcelas de
financiamento misturados na mesma planilha.

## 2. O que a solução faz

Montei um painel que lê a mesma planilha que você exporta e mostra, de uma vez,
a situação da inadimplência. Ele traz:

- **Quatro números no topo:** total em atraso (em R$), clientes em atraso,
  parcelas em atraso e atraso médio em dias.
- **Filtros** por empreendimento, faixa de atraso (4 a 30, 31 a 60, 61 a 90,
  91 a 180 e mais de 180 dias) e tipo de parcela. Eles funcionam sozinhos ou
  combinados, e há um botão para limpar tudo.
- **Busca** por nome do cliente ou por CPF/CNPJ. O CPF/CNPJ serve só para
  encontrar a pessoa e nunca aparece na tela nem no arquivo exportado.
- **Dois gráficos:** saldo em atraso por empreendimento e por faixa de atraso.
  As cores indicam a gravidade: cinza até 30 dias, âmbar de 31 a 90 e vermelho
  acima de 90.
- **Tabela por contrato**, do maior saldo para o menor, com cliente, contrato,
  unidade, telefone, saldo devedor, quantidade de parcelas e o tempo da parcela
  mais antiga em atraso.
- **Botão para baixar a tabela em Excel**, com os mesmos dados da tela.
- **Uma área recolhível** com a conferência dos dados lidos e os valores que
  ficam fora da cobrança (em compensação, distratados, quitados, financiamento
  e originais de acordo), para você comparar com o sistema.

Com a planilha de 25/09/2026, o painel aponta **134 parcelas em atraso, num
total de R$ 625.114,94**. Conferi esse total por um segundo cálculo feito
separadamente, e os dois deram o mesmo resultado.

**Como usar, em 3 passos:**

1. Abra o painel (quem instalou o projeto faz isso pelas instruções do arquivo
   `README.md`).
2. Escolha os filtros ou busque pelo nome do cliente.
3. Consulte a tabela ou clique em "Baixar tabela em Excel".

## 3. Premissas que adotei

Usei as suas respostas e marquei o que ainda precisa de confirmação.

**Confirmadas por você:**

- **Data de referência:** 25/09/2026, a data do arquivo. O atraso é contado a
  partir dela, e não do dia em que alguém abre o painel. Dá para escolher outra
  data na tela, só para consulta.
- **Quando conta como atraso:** a partir de 4 dias depois do vencimento. As
  parcelas com 1 a 3 dias ficam de fora, porque o boleto leva até 2 dias úteis
  para compensar. O painel mostra essas parcelas à parte, só para informação.
- **Acordos:** contam só as parcelas novas do acordo. As parcelas antigas
  renegociadas ficam de fora para a dívida não aparecer em dobro. Se o cliente
  deixar de pagar o acordo, a cobrança segue nas parcelas do acordo.
- **Contratos distratados:** ficam fora, porque já foram para o jurídico.
- **Financiamento:** fica fora, porque é do Repasse.
- **Contrato 2020156 (Vista do Horto):** as parcelas repetidas na exportação
  foram contadas uma vez só.

**Decisões minhas:**

- **Valor em atraso:** é o valor da parcela menos o que o cliente já pagou.
  Parcelas pagas em parte entram só pelo que falta.
- **Parcela que vence na data de referência** ainda não é atraso.
- **Contratos quitados:** ficam fora. No arquivo, eles não têm parcelas em
  aberto.
- **"Clientes em atraso"** conta cada contrato de cada cliente. Quem tem dois
  contratos em atraso aparece duas vezes.

**Ainda precisa de confirmação:**

- Juros, multa e correção: não entram. O valor mostrado é o valor original da
  parcela. Se a Cobrança quiser incluí-los, precisamos combinar a regra.

## 4. O que ficou de fora desta versão

- **Juros, multa e correção monetária.** O painel mostra o valor de face.
- **Percentual de inadimplência.** Falta definir sobre qual valor ele seria
  calculado.
- **Prazo de carência ajustável na tela** e telas separadas para cada tipo de
  acordo. Hoje a carência é fixa em 4 dias.
- **Acesso por senha e regras de proteção de dados.** O painel roda no
  computador de quem o abre. Esse ponto vai na nota técnica para a TI.
- **Padronização de nomes de clientes.** No Loteamento Vista do Horto, os
  nomes vêm em maiúsculas, e uma mesma pessoa pode aparecer escrita de duas
  formas. Por isso o número de clientes pode estar um pouco maior que o real.
