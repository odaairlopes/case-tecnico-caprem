Implemente o passo 4 do case Caprem no arquivo `tratamento.py`: leitura,
validação e normalização do CSV `data/parcelas_cobranca_2026-09-25_4.csv`.

Antes de codificar, confira as premissas em `docs/premissas.md`, a estrutura
do CSV e os scripts de perfilamento existentes. Não implemente regras de
cobrança neste passo; isso ficará em `regras.py`.

Requisitos:

- Leia CSV separado por `;`, em UTF-8 com BOM, mantendo os campos textuais
  como texto na leitura e sem transformar campos vazios em valores NaN.
- Valide o cabeçalho esperado e campos obrigatórios; erros de leitura ou de
  dados inválidos devem ser explícitos e indicar coluna e linha quando
  possível. Não substitua valores inválidos por vazio nem ignore erros.
- Aceite datas `dd/mm/aaaa` e `aaaa-mm-dd`; `DT_PAGAMENTO` pode ficar vazia.
- Aceite valores no padrão brasileiro (`3.625,00`) ou decimal com ponto
  (`2200.00`) e preserve precisão monetária, sem converter para float.
- Normalize `STATUS_PARCELA`, `SITUACAO_CONTRATO` e `TIPO_PARCELA` para
  maiúsculas, validando os valores observados nas premissas/dados.
- Remova linhas integralmente duplicadas e deixe a quantidade removida
  disponível para conferência.
- Use caminho padrão independente do diretório de trabalho e permita passar
  outro caminho para testes.
- Não imprima nem registre dados pessoais.

Adicione testes automatizados cobrindo os dois formatos, normalização,
precisão monetária, datas vazias/opcionais, duplicatas e falhas explícitas.
Não altere `regras.py`, `app.py` ou as premissas. Execute os testes do novo
módulo e reporte exatamente os resultados.
