# Registro de uso de IA

Ferramenta: GitHub Copilot (chat no VS Code). Prompts e respostas completas
em `docs/ia/`, com a saída crua commitada antes de qualquer correção.

---

## Passo 1: Ambiguidades de regra de negócio

**Prompt:** descrevi o problema, o formato do CSV e a usuária (coordenadora
não técnica) e pedi para listar as ambiguidades e propor premissas, sem gerar
código. Arquivo: `docs/ia/passo1_prompt.md`.

**O que a IA fez:** devolveu uma lista longa e bem organizada de ambiguidades
(inadimplência, pagamento parcial, acordos, distratos, tipos de parcela,
qualidade dos dados), com uma premissa para cada.

**O que aproveitei:** saldo devedor como valor da parcela menos o valor pago;
faixas de atraso; distratados fora da cobrança; parcelas futuras fora do
"devido"; separar parcelas de financiamento (a observação de que quem paga é
o banco foi boa e vai para confirmação com a Cobrança).

**Onde errou ou supôs sem base:** a IA não tinha visto o arquivo, então
assumiu um formato genérico. Conferi cada ponto com o relatório do `perfil.py`
e com a contagem independente:

| O que a IA disse                 | O que o arquivo mostra                                                    |
| -------------------------------- | ------------------------------------------------------------------------- |
| Data de referência padrão "hoje" | O arquivo é de 25/09/2026; "hoje" mudaria os números sem os dados mudarem |
| Datas em dd/mm/aaaa              | O Loteamento Vista do Horto usa aaaa-mm-dd                                |
| Valores com vírgula decimal      | O Loteamento usa ponto (`2000.00`)                                        |
| Ler em latin-1 ou utf-8-sig      | O arquivo é utf-8 com BOM; latin-1 não dá erro, mas estraga acentos       |
| Procurar um status "RENEGOCIADA" | O status só tem ABERTA e PAGA (em caixas diferentes)                      |
| Manter a última duplicata        | Todas as duplicatas são idênticas, não há diferença em qual manter.       |

**Como percebi:** comparei cada premissa dele com o relatório do `perfil.py`
(passo 2) e com uma contagem independente (`contagem_rapida.py`). A causa
comum dos erros: pedi a lista sem enviar os dados. Nos prompts seguintes passei
a anexar o CSV e a avisar que os formatos variam por empreendimento.

**Correção:** não aceitei as premissas dele. Escrevi `docs/premissas.md` com
as minhas decisões, marcando a origem de cada uma (dados, decisão ou
confirmar com a Cobrança), e descartei o que era excesso (carência
configurável, percentual de inadimplência, telas separadas de acordos).

**Commit:** 33231f5

## Passo 2: Perfilamento dos dados

**Prompt:** pedi um script de diagnóstico por empreendimento (formatos de
data e valor, status, duplicatas, nulos, parcelas abertas com valor pago,
CPFs inconsistentes), sem corrigir nada. `docs/ia/passo2_prompt.md`

**O que a IA fez:** gerou o `perfil.py`. O relatório identificou que só o
Loteamento Vista do Horto usa datas aaaa-mm-dd, valores com ponto e status
como "Paga"/"Aberta"; achou 46 linhas duplicadas e 12 parcelas abertas com
valor já pago.

**Ajuste necessário:** ao redirecionar a saída pelo PowerShell, os acentos
foram gravados errados no arquivo (ex.: "repetições"). Pedi que o script
gravasse o arquivo direto em UTF-8, e o resultado saiu correto.
`docs/ia/passo2_resposta_copilot.md`

**Como validei:** não registrei quais linhas do CSV olhei manualmente.
A validação confiável é uma contagem independente, escrita por mim
(`contagem_rapida.py`, saída em `docs/evidencias/contagem_rapida_saida.txt`),
rodada em 22/10/2026. Os números bateram com o relatório do `perfil.py`:
46 duplicatas, 12 parcelas abertas com valor pago, e formatos diferentes
só no Loteamento (4.406 de 4.406 linhas).

**Commit:** a1f9eb2

## Passo 3: Gabarito manual

**IA:** não usada. Conferi à mão os 4 contratos de teste, com apoio do
`data/conferir_parcelas.py` e das saídas em `docs/evidencias/`. O resultado
está em `docs/gabarito.md`.

**Resultados:** 1010533 = R$ 0,00 (acordo); 1010638 = R$ 15.932,32
(pagamento parcial); 1010436 = R$ 0,00 (2 dias de atraso); 2020156 =
R$ 2.750,00 (duplicatas contadas uma vez).

**Commit:** d9032a2

## Passo 4: Leitura, validação e normalização

**Prompt:** solicitei a implementação de `tratamento.py`, com leitura do CSV
em UTF-8 com BOM, suporte aos formatos observados, validação explícita,
valores monetários exatos e remoção de duplicatas, sem aplicar regras de
cobrança. O prompt está em [`docs/ia/passo4_prompt.md`](ia/passo4_prompt.md).

**O que a IA fez:** criou `carregar_dados()` e `normalizar_dados()` em
[`tratamento.py`](../tratamento.py), além de testes em
[`tests/test_tratamento.py`](../tests/test_tratamento.py). Datas são
normalizadas para datetime, valores monetários para `Decimal`, e status,
situação do contrato e tipo de parcela para maiúsculas. A quantidade de
duplicatas removidas fica disponível em `DataFrame.attrs`.

**Revisão:** antes da validação final, ajustei a ordem para remover
duplicatas comparando os valores originais, antes de retirar espaços. Assim,
linhas diferentes apenas por espaços não são tratadas indevidamente como
duplicatas exatas. Também ampliei a cobertura dos testes de 6 para 8.

**Como validei:** rodei
`.venv\Scripts\python.exe -m unittest discover -s tests -p test_tratamento.py -v`;
os 8 testes passaram (execução feita na sessão do Copilot). Também carreguei o CSV completo: 10.761 linhas na
origem, 10.715 após remover 46 duplicatas exatas, datas normalizadas e
valores monetários como `Decimal`. Os valores distintos de status,
situação do contrato e tipo de parcela ficaram nos conjuntos esperados.
Não imprimi dados pessoais.

**Resposta registrada:** [`docs/ia/passo4_resposta_copilot.md`](ia/passo4_resposta_copilot.md).

**Commit:** 0bf4957

## Passo 4b: Ajustes do tratamento (conforme o guia)

**Prompt:** o guia pedia normalização do nome do empreendimento e um
relatório de qualidade, que a primeira versão não tinha. Pedi os dois ajustes.
[`docs/ia/passo4b_prompt.md`](ia/passo4b_prompt.md)

**O que a IA fez:** criou `normalizar_empreendimento()` (`LOTEAMENTO VISTA DO
HORTO` passa a `Loteamento Vista do Horto`, com de/da/do/das/dos em minúsculas)
e `relatorio_qualidade()` (linhas lidas, duplicatas removidas, linhas finais,
datas e valores inválidos, linhas por empreendimento). Adicionou 3 testes.

**Observação:** datas e valores inválidos interrompem a carga com erro; por isso
os contadores de inválidos no relatório são sempre 0. O relatório confirma que
nada inválido passou, mas não "descarta" linhas.

**Como validei:** a suíte completa teve 11 testes aprovados (execução na sessão
do Copilot). No CSV real: 10.761 linhas lidas, 46 duplicatas, 10.715 finais;
Loteamento Vista do Horto com 4.360 linhas. Resposta:
[`docs/ia/passo4b_resposta_copilot.md`](ia/passo4b_resposta_copilot.md).

**Minha conferência (23/10/2026):** rodei a suíte completa
(`python -m unittest discover -s tests -v`): 11 testes aprovados. Rodei
`relatorio_qualidade` no CSV real: 10.761 lidas, 46 duplicatas, 10.715 finais,
0 datas e 0 valores inválidos. Contra o meu `contagem_rapida.py`, que mostra
2.633 / 4.406 / 3.722 linhas por empreendimento e 46 duplicatas exatas, os
números batem: o Loteamento tem 4.406 − 46 = 4.360 linhas depois da limpeza.
O nome `LOTEAMENTO VISTA DO HORTO` (maiúsculas no CSV) aparece padronizado como
`Loteamento Vista do Horto`.

**Commit:** 09832da

## Passo 5: Regras de negócio

**Prompt:** o prompt do guia estava desatualizado em relação às minhas
premissas (limite de 4 dias, faixas, financiamento). Usei uma versão revisada,
com a ordem das exclusões, uso de `Decimal` e formato do retorno definidos.
[`docs/ia/passo5_prompt.md`](ia/passo5_prompt.md)

**O que a IA fez:** criou `calcular_inadimplencia()` em
[`regras.py`](../regras.py). Cada parcela recebe um motivo, na ordem: contrato
não ativo, financiamento, original de acordo, paga, ainda não venceu, em
compensação (1 a 3 dias) e inadimplente (4 dias ou mais). Devolve parcelas, total
por contrato, total por empreendimento e resumo.

**Resultado no CSV real (25/09/2026):** 134 parcelas inadimplentes,
R$ 625.114,94. Os quatro contratos do gabarito bateram: 1010533 = R$ 0,00;
1010638 = R$ 15.932,32; 1010436 = R$ 0,00; 2020156 = R$ 2.750,00. Resposta:
[`docs/ia/passo5_resposta_copilot.md`](ia/passo5_resposta_copilot.md).

**Onde a IA errou:** nada encontrado nesta versão. Os acertos foram confirmados
contra o gabarito, que foi feito antes e sem IA.

**Limite da validação:** o CSV não tem atrasos de 30, 31, 60, 61, 90 e 91 dias,
e a fronteira de 3/4 dias não foi testada de forma controlada. Essas fronteiras
ficam para os testes do passo 6.

**Minha conferência (23/10/2026):** rodei o código na minha máquina e comparei
com o gabarito do passo 3 (feito antes, sem IA):

- `resumo`: 134 inadimplentes (R$ 625.114,94), 17 em compensação, 68
  distratados, 6 de financiamento e 31 originais de acordo, com data de
  referência 2026-09-25 (não "hoje").
- Os 4 contratos do gabarito: 1010533 = 0; 1010638 = 15.932,32; 1010436 = 0;
  2020156 = 2.750,00. Todos bateram.
- Pagamento parcial (contrato 1010638, parcela 2): valor 6.117,65, pago
  2.420,63, saldo 3.697,02 e 41 dias de atraso. O saldo é usado, não o valor cheio.
- Acordo (1010533): as 3 originais ficam como "Parcela original renegociada em
  acordo" (R$ 2.812,50, R$ 2.812,50 e R$ 13.500,00); as parcelas ACORDO pagas têm
  saldo 0 e as futuras estão "Ainda não venceu". Nenhuma entra no total.
- Todos os 134 inadimplentes são de contratos ATIVO; os distratados aparecem só
  no resumo à parte.
- Parcelas com atraso 0 não aparecem como inadimplentes.
- 12 pagamentos parciais conferidos, saldo = parcela - pago em todos

**Commit:** dcb5973

## Passo 6: Testes das regras

**Prompt:** o guia pedia testes em `pytest`; o projeto já usava `unittest`
(e o `pytest` não estava instalado), então a IA escreveu em `unittest`, que o
`pytest` também executa. Acrescentei a fronteira de 3/4 dias e as das faixas,
que o prompt do guia não cobria (ele previa carência de 1 dia). Prompt do guia:
[`docs/ia/passo6_prompt.md`](ia/passo6_prompt.md).

**O que a IA fez:** criou 19 testes em
[`tests/test_regras.py`](../tests/test_regras.py), com DataFrames feitos à mão:
parcela paga, aberta futura, aberta vencida, pagamento parcial (6.117,65 −
2.420,63 = 3.697,02), contrato distratado e quitado, financiamento, original de
acordo versus parcela ACORDO, vence na data de referência (0 dia), 1 dia (em
compensação), 3/4 dias, fronteiras das faixas (30/31, 60/61, 90/91, 180/181),
faixa só para inadimplentes, prioridade entre motivos, totais por contrato e
empreendimento, saldo em `Decimal`, DataFrame de entrada não alterado e data de
referência padrão 25/09/2026.

**Resultado:** suíte inteira com 30 testes OK (19 novos e 11 de
`tratamento.py`). Nenhum teste foi ajustado para passar e o `regras.py` não foi
alterado. Evidências: [`testes_passo6.txt`](evidencias/testes_passo6.txt) e
[`pytest_passo6.txt`](evidencias/pytest_passo6.txt).

Resposta: [`docs/ia/passo6_resposta_copilot.md`](ia/passo6_resposta_copilot.md).

**Teste de mutação:** troquei `dias < CARENCIA_DIAS` por `dias <=
CARENCIA_DIAS` (erro de fronteira entre 3 e 4 dias). Dois testes falharam:
`test_fronteira_carencia_3_dias_fora_e_4_dias_dentro` e
`test_fronteiras_das_faixas` (caso de 4 dias). Voltei a regra ao original e a
suíte voltou a passar. Evidência:
[`pytest_passo6_mutacao.txt`](evidencias/pytest_passo6_mutacao.txt).

**Onde a IA errou:** nada encontrado. Observação: uma primeira execução da
mutação feita pela IA não valeu, porque o teste e a restauração rodaram no mesmo
bloco; foi refeita em sequência.

**Limite da validação:** os testes usam dados pequenos e criados à mão; não
provam a lista inteira do CSV real, que foi conferida no passo 5 contra o
gabarito. A mutação cobriu uma regra; as demais não foram quebradas de propósito.

**Minha conferência (23/10/2026):** rodei a suíte na minha máquina com
`unittest` e com `pytest`, e repeti a mutação 2 failed, 29 passed, 8 subtests passed.

**Commit:** (preencher)
