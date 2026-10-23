Atenção: os empreendimentos podem usar formatos diferentes de data e de
valor. Não assuma um padrão único; descubra por empreendimento.

Escreva um script de diagnóstico (perfil.py) que leia o CSV
data/parcelas_cobranca_2026-09-25.csv com todas as colunas como string e,
por empreendimento, mostre: formatos de data encontrados, formatos de
valor numérico, valores distintos de STATUS_PARCELA e SITUACAO_CONTRATO,
linhas duplicadas, nulos por coluna, parcelas ABERTAS com VALOR_PAGO > 0,
e contratos com mais de um CPF ou CPFs com mais de um nome. Não corrija
nada, apenas reporte.
No perfil.py, faça o relatório ser gravado diretamente no arquivo
docs/evidencias/perfil_saida.txt com open(..., "w", encoding="utf-8"),
além de imprimir na tela. Assim não dependo do redirecionamento do terminal.
