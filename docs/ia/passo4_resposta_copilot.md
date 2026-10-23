# Passo 4 — resposta e resultado

Implementei a leitura, validação e normalização em
[`tratamento.py`](../../tratamento.py). O módulo disponibiliza:

- `carregar_dados(caminho=ARQUIVO_PADRAO)`: lê CSV separado por `;` em UTF-8
  com BOM, mantendo texto sem converter campos vazios em NaN.
- `normalizar_dados(dados)`: valida o esquema, os campos obrigatórios, os
  status/situações/tipos, as datas e os valores; não executa regras de
  cobrança.
- Datas nos formatos `dd/mm/aaaa` e `aaaa-mm-dd`, com `DT_PAGAMENTO` vazio
  representado por `NaT`.
- Valores monetários como `Decimal`, sem conversão para `float`.
- Remoção apenas de linhas exatamente duplicadas nos dados de origem; a
  contagem removida fica em `DataFrame.attrs["duplicatas_removidas"]`.
- Erros explícitos com linha e coluna quando o conteúdo permite essa
  identificação.

Os testes estão em [`tests/test_tratamento.py`](../../tests/test_tratamento.py).
Na validação final, **8 testes passaram**. A leitura do CSV completo encontrou
10.761 linhas de origem e removeu 46 duplicatas, resultando em 10.715 linhas.
Os status, situações de contrato e tipos de parcela foram normalizados para
os valores esperados; datas ficaram em dtype datetime e os dois campos
monetários foram mantidos como `Decimal`. Nenhum dado pessoal foi impresso.

Durante a revisão, garanti que a deduplicação ocorre antes da remoção de
espaços, para não classificar como duplicatas exatas linhas que diferem no
conteúdo bruto. A bateria foi executada novamente após esse ajuste.
