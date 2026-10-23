Criei o perfil.py e rodei no CSV da pasta data. Ele só reporta, não corrige nada.

O arquivo que rodei não é o que você pediu. O CSV data/parcelas_cobranca_2026-09-25.csv não existe. Só existe parcelas_cobranca_2026-09-25_4.csv, com 10.761 linhas. Rodei nele passando o caminho como argumento: python perfil.py data\parcelas_cobranca_2026-09-25_4.csv. Sem argumento, o script procura o nome que você pediu.

### Como o script funciona

- Lê tudo como texto (dtype=str), com utf-8-sig e latin-1 como alternativa, e agrupa por empreendimento.
- Mostra o número da linha do arquivo nos achados (cabeçalho = linha 1).
- Formatos de data e de valor aparecem como máscaras, com 9 no lugar de cada dígito. Nas datas com /, mostra também o maior 1º e o maior 2º campo, para distinguir dd/mm de mm/dd.
- Cobre todos os itens que você pediu. Duplicatas saem em dois blocos: linhas idênticas e mesma chave com conteúdo diferente.
- Para ver se uma parcela está "aberta", procura "abert" no status, sem diferenciar maiúsculas e minúsculas.
- Para saber se VALOR_PAGO é maior que zero, usa uma leitura tolerante que aceita vírgula ou ponto como decimal. Ela só serve ao diagnóstico.
- Na comparação de nomes por CPF, ignora caixa e espaços repetidos. Não ignora acentos.

### O que apareceu

| Empreendimento                   | Linhas | Datas      | Valores  | Status       | Duplicadas              | Abertas com valor pago |
| -------------------------------- | ------ | ---------- | -------- | ------------ | ----------------------- | ---------------------- |
| Edifício Parque Azul             | 2.633  | dd/mm/aaaa | 3.625,00 | ABERTA, PAGA | 0                       | 8 (R$ 27.338,50)       |
| Residencial Jardim das Palmeiras | 3.722  | dd/mm/aaaa | 3.625,00 | ABERTA, PAGA | 0                       | 2 (R$ 2.591,54)        |
| LOTEAMENTO VISTA DO HORTO        | 4.406  | aaaa-mm-dd | 3625.00  | Aberta, Paga | 46 repetições idênticas | 2 (R$ 2.072,33)        |

- Vista do Horto é o único empreendimento fora do padrão: datas ISO, ponto decimal sem milhar e status em outra caixa. O nome também vem em maiúsculas. Isso bate com o perfil_saida.txt que já existia.
- Vista do Horto tem ainda 288 contratos QUITADO e 288 DISTRATADO, o que merece atenção na regra de negócio. O Parque Azul só tem ATIVO, e o Jardim das Palmeiras tem ATIVO e DISTRATADO.
- Parcelas abertas com valor pago são pagamento parcial ou erro de dado, e a Cobrança precisa decidir qual. Isso afeta direto o saldo devedor.
- NUM_ACORDO está quase todo vazio (98,6% a 100%), e nenhum status "renegociada" apareceu.
- DT_PAGAMENTO vazio está em torno de 1.448 linhas no Parque Azul, 242 no Jardim das Palmeiras e 2.467 no Vista do Horto, e coincide com as parcelas abertas.
- VALOR_PAGO sem valor vem como 0,00 ou 0.00, não como campo vazio.
- Não há contrato com mais de um CPF nem CPF com mais de um nome em nenhum empreendimento.
- Não há duplicatas com mesma chave e conteúdo diferente em nenhum empreendimento.
- Você confirma se o arquivo \_4 é o correto? Se for, posso renomeá-lo ou trocar o padrão do script para esse nome.

O perfil.py imprime o relatório na tela e grava o mesmo conteúdo em docs/evidencias/perfil_saida.txt, aberto com open(..., "w", encoding="utf-8"). A pasta é criada se não existir. Rodei com o .venv e o arquivo saiu com acentos corretos, por exemplo "repetições" na linha 81.

Sobrescrita: o arquivo perfil_saida.txt anterior tinha o relatório do outro analisador, e esta execução o substituiu. O relatorio_formatacao.txt tem o mesmo conteúdo do antigo, então nada se perdeu.
Caminho de saída: dá para trocar com --saida outro.txt.
Caminho padrão do CSV: mantive o \_4, porque você já tinha editado essa linha no arquivo.
Texto estranho que você selecionou: o "repetiÃ§Ãµes" na linha 81 do arquivo antigo era só o terminal do Windows gravando o redirecionamento em outra codificação. No arquivo novo isso não acontece.
