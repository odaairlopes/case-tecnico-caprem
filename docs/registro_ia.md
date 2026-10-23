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

**Como percebi:** abri o arquivo e comparei com as premissas dele, linha a
linha. A causa comum: pedi a lista sem enviar os dados. Para os próximos
prompts passo a anexar o CSV e avisar que os formatos podem variar por
empreendimento.

**Correção:** não aceitei as premissas dele. Escrevi `docs/premissas.md` com
as minhas decisões, marcando a origem de cada uma (dados, decisão ou
confirmar com a Cobrança), e descartei o que era excesso (carência
configurável, percentual de inadimplência, telas separadas de acordos).

**Commit:** (cole aqui o hash do commit `ia: passo 1 saída crua do Copilot`)

| O Copilot disse                            | Problema                                                                |
| ------------------------------------------ | ----------------------------------------------------------------------- |
| Data de referência padrão "hoje"           | O arquivo é de 25/09/2026. O padrão deve ser a data do arquivo          |
| Datas em dd/mm/aaaa                        | O Loteamento vem em `aaaa-mm-dd` e também em `dd/mm/aaaa`               |
| Valores com vírgula decimal                | O Loteamento vem com ponto (`2000.00`) e também vem com vírgula decimal |
| Ler em latin-1 ou utf-8-sig                | O arquivo é utf-8 com BOM. Latin-1 estraga acentos sem avisar           |
| `NUM_CONTRATO` único só dentro da coligada | Conferi: nenhum contrato aparece em duas coligadas                      |
| Procurar status "RENEGOCIADA"              | O status só tem ABERTA e PAGA (em caixas diferentes)                    |
| Duplicatas: manter a última                | As 46 são idênticas, então escolher qual manter não importa             |

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

**Como validei:** [conferi linhas do CSV: diga quais] e rodei uma contagem
independente (`contagem_rapida.py`, escrita por mim) que bateu com o relatório:
[escreva os números].

**Commit:** (hash)
