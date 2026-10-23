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
assumiu um formato genérico. Conferi abrindo o CSV:

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
rodada em [DATA]. Os números bateram com o relatório do `perfil.py`:
46 duplicatas, 12 parcelas abertas com valor pago, e formatos diferentes
só no Loteamento (4.406 de 4.406 linhas).

**Commit:** a1f9eb2
