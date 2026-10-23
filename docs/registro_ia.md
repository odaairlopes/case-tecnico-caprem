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

# Passo 3: Gabarito manual

**IA:** não usada. Conferi à mão os 4 contratos de teste, com apoio do
`data/conferir_parcelas.py` e das saídas em `docs/evidencias/`. O resultado
está em `docs/gabarito.md`.

**Resultados:** 1010533 = R$ 0,00 (acordo); 1010638 = R$ 15.932,32
(pagamento parcial); 1010436 = R$ 0,00 (2 dias de atraso); 2020156 =
R$ 2.750,00 (duplicatas contadas uma vez).

**Commit:** 0bf4957

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
os 8 testes passaram. Também carreguei o CSV completo: 10.761 linhas na
origem, 10.715 após remover 46 duplicatas exatas, datas normalizadas e
valores monetários como `Decimal`. Os valores distintos de status,
situação do contrato e tipo de parcela ficaram nos conjuntos esperados.
Não imprimi dados pessoais.

**Resposta registrada:** [`docs/ia/passo4_resposta_copilot.md`](ia/passo4_resposta_copilot.md).

**Commit:** não realizado nesta etapa.
