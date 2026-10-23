## Passo 4 - Ajuste tratamento.py (sem alterar o que já funciona):

1. Normalize EMPREENDIMENTO: "LOTEAMENTO VISTA DO HORTO" deve virar
   "Loteamento Vista do Horto", no mesmo padrão dos demais (título, com
   de/da/do/das/dos em minúsculas). Remova espaços duplicados. Assim os três
   empreendimentos não aparecem duplicados nem com caixa diferente.
2. Crie relatorio_qualidade(df) -> dict, com: linhas lidas, duplicatas
   removidas, linhas finais, datas de vencimento inválidas, valores
   inválidos e linhas por empreendimento. Como dado inválido já interrompe
   a carga, esses dois contadores devem ser 0 e isso deve ser dito.
   Guarde "linhas_lidas" em df.attrs dentro de normalizar_dados.
   Adicione testes em tests/test_tratamento.py para os dois itens e rode a
   suíte inteira. Não altere regras.py, app.py ou as premissas.
