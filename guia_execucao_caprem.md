# Guia de execução: Case Caprem

Prazo: **segunda, 26/10/2026, 9h**. Meta: terminar no domingo à noite.
Quem codifica: o Copilot. Quem decide, confere e escreve os textos finais: você.

---

## Como documentar o uso de IA (sem prints)

Prints de respostas longas não funcionam. Use **texto**, que é mais fácil de ler e mais difícil de contestar.

Para cada passo, crie dois arquivos em `docs/ia/`:

- `passoN_prompt.md`: o prompt exato que você enviou (copie e cole)
- `passoN_resposta_copilot.md`: a resposta completa do Copilot, **sem editar nada**

Como copiar a resposta do Copilot:

- Passe o mouse sobre a resposta e use o botão de copiar, ou selecione tudo e `Ctrl+C`
- No VS Code, a paleta de comandos (`Ctrl+Shift+P`) costuma ter **"Chat: Export Chat..."**, que salva a conversa inteira. Se existir na sua versão, use no final de cada passo

Depois:

1. `git add docs/ia` e `git commit -m "ia: passoN saída crua do Copilot"`
2. **Só então** corrija ou mude qualquer coisa

O commit com a saída crua é a sua prova. O `git diff` entre ele e o commit da correção mostra exatamente o que a IA errou.

**Prints só onde fazem sentido:** a tela do dashboard rodando (2 ou 3 prints em `docs/evidencias/`) e a saída de um teste falhando.

### Modelo de entrada no `docs/registro_ia.md` (um por erro ou acerto relevante)

```
## Passo N: título
Prompt: (resumo em 1 linha + link para docs/ia/passoN_prompt.md)
O que a IA fez: (resumo)
Onde errou / acertou: (ex.: converteu 4.406 datas em vazio)
Como percebi: (ex.: contagem de nulos depois do tratamento não era zero)
Correção: (o que mudei e por quê)
Commit: (hash)
```

Se a IA acertar de primeira, registre também, com a forma como você conferiu.

---

## Antes de começar (uma vez só)

- [x] Criar a pasta `caprem-inadimplencia/` e rodar `git init`
- [x] Criar as pastas: `data/`, `docs/`, `docs/ia/`, `docs/evidencias/`, `tests/`
- [x] Copiar o CSV para `data/` e o PDF do case para `docs/`
- [x] Criar os arquivos vazios: `docs/registro_ia.md`, `docs/premissas.md`, `docs/gabarito.md`
- [x] Primeiro commit: `chore: estrutura inicial`
- [x] Não apagar o histórico do chat do Copilot até o fim

Estrutura final esperada:

```
caprem-inadimplencia/
  app.py            # dashboard
  tratamento.py     # leitura e limpeza
  regras.py         # regras de negócio
  perfil.py         # diagnóstico dos dados
  conferir.py       # conferência independente
  tests/test_regras.py
  data/             # o CSV (não suba dados reais em repositório público)
  docs/             # resumo, nota técnica, premissas, gabarito, registro_ia, ia/, evidencias/
  README.md
  requirements.txt
```

---

## Passo 1: Ambiguidades de negócio (VOCÊ ESTÁ AQUI)

**Enviar ao Copilot:** Prompt 1.

```
Vou construir um dashboard de inadimplência em Python (pandas + Streamlit)
para a área de Cobrança de uma construtora. Entrada: CSV separado por ";",
uma linha por parcela, campos: COLIGADA, EMPREENDIMENTO, UNIDADE,
NUM_CONTRATO, SITUACAO_CONTRATO (ATIVO/QUITADO/DISTRATADO), CLIENTE,
CPF_CNPJ, TELEFONE, TIPO_PARCELA (MENSAL/INTERMEDIARIA/CHAVES/
FINANCIAMENTO/ACORDO), NUM_PARCELA, DT_VENCIMENTO, VALOR_PARCELA,
VALOR_PAGO, DT_PAGAMENTO, STATUS_PARCELA, NUM_ACORDO.
O usuário final é uma coordenadora de Cobrança, não técnica: quer ver quem
deve, quanto e de qual empreendimento. Antes de escrever código, liste as
ambiguidades de regra de negócio que você enxerga (ex.: o que é
inadimplente, tratamento de acordos, distratos, pagamento parcial) e
proponha uma premissa para cada. Não gere código ainda.
```

**Fazer**

- [x] Enviar o prompt (já feito)
- [x] Salvar o prompt em `docs/ia/passo1_prompt.md`
- [x] Salvar a resposta do Copilot em `docs/ia/passo1_resposta_copilot.md`
- [x] Commit: `ia: passo 1 saída crua do Copilot`
- [ ] Triar a resposta (veja a tabela abaixo)
- [x] Escrever o `docs/premissas.md` com **suas** decisões
- [ ] Registrar no `registro_ia.md` os erros do Copilot (tabela abaixo)
- [ ] Commit: `docs: premissas iniciais de negócio`

### Triagem da resposta do Copilot

**Entra como está**

- Saldo devedor = valor da parcela − valor pago
- Parcela vencida = vencimento anterior à data de referência e saldo maior que zero
- Faixas de atraso: 1–30, 31–60, 61–90, 91–180, mais de 180 dias
- Contratos distratados fora da cobrança, mostrados à parte
- Parcelas futuras fora do "devido"
- Financiamento separado do total (confirmar com a Renata)
- Exportar para Excel e usar linguagem sem jargão
- Sem juros e multa, com aviso na tela

**Está errado ou fraco (vai para o registro de IA)**

| O Copilot disse                            | Problema                                                       |
| ------------------------------------------ | -------------------------------------------------------------- |
| Data de referência padrão "hoje"           | O arquivo é de 25/09/2026. O padrão deve ser a data do arquivo |
| Datas em dd/mm/aaaa                        | O Loteamento vem em `aaaa-mm-dd`                               |
| Valores com vírgula decimal                | O Loteamento vem com ponto (`2000.00`)                         |
| Ler em latin-1 ou utf-8-sig                | O arquivo é utf-8 com BOM. Latin-1 estraga acentos sem avisar  |
| `NUM_CONTRATO` único só dentro da coligada | Conferi: nenhum contrato aparece em duas coligadas             |
| Procurar status "RENEGOCIADA"              | O status só tem ABERTA e PAGA (em caixas diferentes)           |
| Duplicatas: manter a última                | As 46 são idênticas, basta remover                             |

Como registrar: "O Copilot não viu o arquivo e supôs formatos genéricos. Percebi ao comparar com o perfilamento." Isso é verdade e mostra que você aprendeu a dar contexto.

**Fica fora (anote em "o que ficou de fora")**

- Carência configurável, percentual de inadimplência, correção monetária
- Telas separadas de "acordo em dia" e "acordo quebrado" (basta uma marcação)
- LGPD e controle de acesso (vai para a nota técnica)

**Os dados já respondem (não perguntar para a Renata)**

- O acordo é identificado pelo campo `NUM_ACORDO`, preenchido nas parcelas originais e nas parcelas do tipo ACORDO
- Quitados com parcela aberta: zero
- Há 8 contratos com acordo. Somar tudo conta a dívida em dobro

### Modelo do `docs/premissas.md`

```
| Regra | Decisão | Fonte |
|---|---|---|
| Data de referência | 25/09/2026 (data do arquivo), alterável na tela | dados |
| Saldo devedor | valor da parcela − valor pago | decisão |
| Parcela inadimplente | ABERTA e vencimento < data de referência | decisão |
| Contratos distratados | fora do total, listados à parte | decisão, confirmar com Renata |
| Financiamento | filtro separado | decisão, confirmar com Renata |
| Acordos | só as parcelas do acordo; originais com NUM_ACORDO ficam de fora | decisão, confirmar com Renata |
| Duplicatas | removidas (46 linhas idênticas) | dados |
| Juros, multa, correção | fora do escopo, aviso na tela | decisão |
```

Fonte: `dados` = você conferiu no arquivo; `decisão` = sua escolha; `Renata` = ainda a confirmar.

### Perguntas para a Renata (só estas 4; guarde, o e-mail vem depois)

1. Acordo: devo contar só as parcelas do acordo e ignorar as originais? Se o cliente quebrar o acordo, volta a valer a dívida original?
2. Contratos distratados com parcelas abertas: ficam fora da cobrança?
3. Parcelas de financiamento (banco): entram na inadimplência do cliente ou ficam separadas?
4. Existe carência oficial (dias de tolerância depois do vencimento)?

---

## Passo 2: Perfilamento dos dados

**Enviar ao Copilot:** Prompt 2. **Anexe o CSV** ou cole 3 linhas de cada empreendimento antes.

```
Atenção: os empreendimentos podem usar formatos diferentes de data e de
valor. Não assuma um padrão único; descubra por empreendimento.

Escreva um script de diagnóstico (perfil.py) que leia o CSV com todas as
colunas como string e, por empreendimento, mostre: formatos de data
encontrados, formatos de valor numérico, valores distintos de
STATUS_PARCELA e SITUACAO_CONTRATO, linhas duplicadas, nulos por coluna,
parcelas ABERTAS com VALOR_PAGO > 0, e contratos com mais de um CPF ou
CPFs com mais de um nome. Não corrija nada, apenas reporte.
```

**Fazer**

- [ ] Salvar prompt e resposta em `docs/ia/passo2_*.md`
- [ ] Commit cru: `ia: passo 2 perfil.py versão inicial`
- [ ] Rodar o script e salvar a saída em `docs/evidencias/perfil_saida.txt`

**Conferir** (cada item que falhar é erro real da IA, anote)

- [ ] Reportou o formato diferente do Loteamento (data `2023-04-23`, valor `2000.00`)?
- [ ] Encontrou 46 duplicatas?
- [ ] Encontrou 12 parcelas abertas com valor pago?
- [ ] Reportou `Paga` e `Aberta` além de `PAGA` e `ABERTA`?
- [ ] Leu o arquivo com `utf-8-sig` (sem `ï»¿` no nome da primeira coluna)?
- [ ] Commit das correções: `fix: ...`

> Depois deste passo você já tem dúvidas reais: **envie o e-mail para a Renata agora** (1 e-mail com as 4 perguntas), porque a resposta dela pode mudar o Passo 5.

---

## Passo 3: Gabarito manual (SEU, sem IA)

Este passo dá credibilidade a todo o resto.

- [ ] Abrir o CSV no Excel (ou Python simples)
- [ ] Escolher o contrato **1010533** (tem acordo) e um contrato ativo sem acordo
- [ ] Calcular na mão, com data de referência 25/09/2026: parcelas vencidas em aberto, saldo (valor − pago) e total
- [ ] No contrato com acordo, fazer **as duas contas**: contando as originais e contando só as parcelas do acordo, e anotar a diferença
- [ ] Salvar em `docs/gabarito.md` com os valores e como chegou neles
- [ ] Commit: `docs: gabarito manual para validação`

---

## Passo 4: Tratamento

**Enviar:** Prompt 3.

```
Com base no diagnóstico, crie tratamento.py com funções puras e testáveis:
- leitura com encoding utf-8-sig e dtype=str;
- parse de data e de valor tolerando os dois formatos (dd/mm/yyyy e
  yyyy-mm-dd; "1.234,56" e "1234.56"), decidindo por padrão de string,
  nunca por dayfirst global;
- normalização de STATUS_PARCELA e do nome do empreendimento;
- remoção de duplicatas exatas, registrando quantas foram removidas;
- retornar também um relatório de qualidade (linhas lidas, descartadas,
  datas inválidas) para exibir no dashboard.
Falhe de forma explícita se uma data ou valor não puder ser interpretada,
em vez de converter silenciosamente para nulo.
```

**Fazer**

- [ ] Salvar prompt e resposta em `docs/ia/passo4_*.md`
- [ ] Commit cru: `ia: passo 4 tratamento versão inicial`

**Conferir**

- [ ] Datas nulas depois do parse = 0 (se o Copilot usou `dayfirst=True` ou `errors='coerce'` em tudo, você achou o erro clássico)
- [ ] Os valores do Loteamento estão corretos (`2000.00` não virou `200000`)?
- [ ] Status unificado em `PAGA` e `ABERTA`?
- [ ] 46 duplicatas removidas, e o relatório mostra isso?
- [ ] Total de linhas depois do tratamento = 10.715
- [ ] Falha explícita para dado inválido, como pedido?
- [ ] Registrar cada erro no `registro_ia.md`; commit por correção: `fix: ...`

---

## Passo 5: Regras de negócio

**Enviar:** Prompt 4.

```
Crie regras.py com a função calcular_inadimplencia(df, data_ref) onde
data_ref é um parâmetro (default: data do arquivo, 25/09/2026, e não hoje).
Premissas:
- Parcela inadimplente: STATUS ABERTA, DT_VENCIMENTO < data_ref.
- Saldo devedor = VALOR_PARCELA - VALOR_PAGO (cobre pagamento parcial).
- Excluir contratos DISTRATADO e QUITADO do total cobrável, mas mostrar
  o valor dos distratados em separado.
- Acordos: parcelas originais com NUM_ACORDO preenchido são substituídas
  pelas parcelas de TIPO_PARCELA = ACORDO; contar apenas uma das duas
  para não duplicar a dívida.
- Faixas de atraso: 1-30, 31-60, 61-90, 91-180, >180 dias.
Documente cada premissa em docstring. Retorne um DataFrame por parcela e
agregações por cliente/contrato e por empreendimento.
```

> Se a Renata já respondeu, ajuste as premissas do prompt antes de enviar.

**Fazer**

- [ ] Salvar em `docs/ia/passo5_*.md`; commit cru: `ia: passo 5 regras versão inicial`

**Conferir contra o gabarito do Passo 3**

- [ ] O saldo do contrato 1010533 bate com a sua conta manual?
- [ ] O acordo foi contado uma vez só?
- [ ] Os 12 pagamentos parciais usam o saldo, e não o valor cheio?
- [ ] Distratados ficaram fora do total e aparecem à parte?
- [ ] Parcela que vence na data de referência **não** é inadimplente, e a do dia anterior é?
- [ ] A data de referência é 25/09/2026, e não `datetime.today()`?
- [ ] Faixas corretas nas fronteiras (30, 31, 90, 91 dias)?
- [ ] Registrar erros; commits: `fix: ...`; atualizar `premissas.md` se alguma regra mudou

---

## Passo 6: Testes

**Enviar:** Prompt 5.

```
Escreva testes pytest para regras.py com um DataFrame pequeno e feito à
mão cobrindo: parcela paga, aberta futura, aberta vencida, pagamento
parcial, contrato distratado, parcela original de acordo vs parcela de
acordo, e a fronteira exata data_ref == vencimento. Depois rode e mostre
as falhas, sem ajustar os testes para passar.
```

**Fazer**

- [ ] Salvar em `docs/ia/passo6_*.md`; commit cru
- [ ] Rodar `pytest -v` e salvar a saída em `docs/evidencias/pytest.txt`

**Conferir**

- [ ] Os testes cobrem os 7 casos pedidos?
- [ ] Algum teste foi escrito para confirmar um bug em vez de pegá-lo?
- [ ] Quebre uma regra de propósito **no seu código** (ex.: trocar `<` por `<=`). Se nenhum teste falhar, o teste é fraco
- [ ] Desfaça a quebra
- [ ] Commit: `test: casos de regra de negócio`

---

## Passo 7: Conferência independente

**Enviar:** Prompt 7.

```
Escreva um script conferir.py que recalcule o total em atraso por
empreendimento de forma independente (sem importar regras.py, usando
apenas pandas básico) e compare com o resultado do dashboard. Liste
qualquer divergência.
```

**Fazer e conferir**

- [ ] Salvar em `docs/ia/passo7_*.md`; commit cru
- [ ] Abrir o arquivo e confirmar que **não** importa `regras.py`
- [ ] Rodar e comparar os totais por empreendimento
- [ ] Se divergir, descobrir **qual dos dois** está errado (use o gabarito). Esse costuma ser o melhor item do registro
- [ ] Salvar a saída em `docs/evidencias/conferencia.txt`
- [ ] Commit: `test: conferência independente dos totais`

---

## Passo 8: Dashboard (Streamlit, roda local no navegador)

Rodar com `streamlit run app.py` (abre em `localhost:8501`).

**Enviar:** Prompt 6.

```
Crie app.py em Streamlit para a coordenadora de Cobrança. Topo: total em
atraso, nº de clientes inadimplentes, nº de parcelas, atraso médio.
Filtros: empreendimento, faixa de atraso, tipo de parcela. Visões: gráfico
por empreendimento, gráfico por faixa de atraso e tabela de clientes com
contrato, unidade, telefone, saldo devedor e parcela mais antiga em atraso,
ordenada por saldo. Botão para exportar a tabela filtrada em Excel. Rótulos
em português claro, valores em R$, sem jargão técnico. Mostrar a data de
referência e o relatório de qualidade dos dados em uma seção recolhível.
```

Depois, o prompt de refinamento visual:

```
Refine app.py: layout wide, filtros na barra lateral agrupados com títulos,
estado vazio amigável quando os filtros não retornam dados, formatação
brasileira de moeda e data, cores consistentes (um vermelho para atraso
grave, âmbar para médio, neutro para o resto), tabela com barra de
progresso de saldo e botão para exportar. Priorize clareza para uma
pessoa não técnica. Adicione também busca por nome ou CPF e seletor de
data de referência.
```

**Fazer**

- [ ] Salvar prompts e respostas em `docs/ia/passo8_*.md`; commit cru
- [ ] Prints do app rodando (antes e depois do refinamento) em `docs/evidencias/`

**Conferir**

- [ ] `streamlit run app.py` abre sem erro
- [ ] Os cartões do topo batem com `conferir.py`
- [ ] Cada filtro funciona sozinho e combinado
- [ ] Filtro sem resultado mostra mensagem amigável
- [ ] Valores em R$ e datas em dd/mm/aaaa
- [ ] A exportação para Excel abre e tem os mesmos dados da tela
- [ ] Data de referência e relatório de qualidade visíveis
- [ ] Mostrar para alguém não técnico por 2 minutos: ele entende sem explicação?
- [ ] Commits: `ia: dashboard inicial`, `fix: ...`, `style: refinamento de interface`

---

## Passo 9: README e execução do zero

**Enviar (pequeno):**

```
Crie o README.md com: o que o projeto faz, requisitos, como instalar
(venv + requirements.txt), como rodar o dashboard, como rodar os testes e
a conferência, estrutura de pastas, e onde colocar o CSV.
```

**Fazer**

- [ ] Gerar `requirements.txt` com versões fixadas (`pip freeze` filtrado)
- [ ] Clonar o repositório **em outra pasta**, criar ambiente virtual novo e seguir só o README
- [ ] Se travar em algum passo, corrigir o README
- [ ] Commit: `docs: readme e requirements`

---

## Passo 10: Documentos

**Enviar em dois pedidos separados** (resumo e nota técnica).

```
Redija a partir do código final: (a) resumo de até 2 páginas para a
coordenadora, sem termos técnicos: problema, o que a solução faz,
premissas, o que ficou de fora; (b) nota técnica curta para o TI: como
funciona e o que mudar para rodar todo dia em produção (leitura direto
do banco em vez de CSV, agendamento, logs, validação de schema, testes
automatizados, autenticação, LGPD para CPF e telefone).
```

**Fazer (seu)**

- [ ] Reescrever o **resumo da Renata** com a sua voz: máximo 2 páginas, sem jargão
- [ ] Conferir os 4 itens: problema, o que a solução faz, premissas, o que ficou de fora
- [ ] Atualizar premissas com as respostas dela
- [ ] Reescrever a **nota técnica**; deve citar: leitura do banco, agendamento, logs, validação, testes, acesso e LGPD
- [ ] Ler em voz alta; o que soar como texto de IA, reescreva
- [ ] Commit: `docs: resumo e nota técnica`

---

## Passo 11: Registro de IA (final)

- [ ] Ordenar as entradas por passo
- [ ] Cada erro tem: prompt, o que a IA fez, onde errou, **como você percebeu**, correção e hash do commit
- [ ] Incluir também o que a IA acertou de primeira e como você validou
- [ ] Resumo no topo: quantos prompts, quantos erros reais, qual foi o mais grave
- [ ] Se algum erro só foi percebido por acaso, escreva assim mesmo

---

## Passo 12: Pacote final

- [ ] `git log --oneline` mostra um histórico legível
- [ ] Compactar (ou subir no GitHub **privado**, com acesso para quem enviou o case)
- [ ] Enviar para **quem enviou o case**, nunca para a Renata
- [ ] Entregar até segunda, 26/10, 9h (meta: domingo à noite)

---

## Cenários de mudança na conversa (resumo)

| Cenário                                       | Resposta curta                                                                                                                     |
| --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Rodar todo dia com dados do sistema           | Consulta SQL somente leitura no lugar do CSV; tratamento e regras já são independentes da fonte; agendar com log e alerta de falha |
| Entrou um 4º empreendimento com outro formato | Parser decide por padrão de texto, não por empreendimento; o que não parsear vai para quarentena visível                           |
| Multa e juros                                 | Regras parametrizáveis; confirmar percentuais com a Cobrança; coluna "valor atualizado" à parte                                    |
| Cliente quebrou o acordo                      | Parcela de acordo vencida marca "acordo quebrado"; decidir com a Cobrança se as originais voltam a valer                           |
| Priorizar quem cobrar                         | Score simples e explicável (valor, dias de atraso, nº de parcelas, histórico)                                                      |
| Dados 100 vezes maiores                       | Pré-agregar no banco, cache, Parquet ou DuckDB                                                                                     |
| Vários usuários                               | SSO, perfis de acesso, CPF e telefone mascarados, log de exportações (LGPD)                                                        |
| Power BI em vez de código                     | A camada de tratamento vira uma tabela pronta; o BI só visualiza                                                                   |
| Números não batem com o sistema               | Relatório de reconciliação: lidas, descartadas, duplicatas, distratos excluídos                                                    |
| Mudar a data de referência                    | Já é parâmetro; o seletor refaz o retrato de qualquer dia                                                                          |
| Integrar WhatsApp                             | Fora do escopo; evoluir com fila de cobrança, consentimento e histórico de contato                                                 |
| "Explique esta linha"                         | Defender sem olhar o código: parse por padrão de texto, regra de acordos, função de faixas de atraso                               |

Ao responder: primeiro o que você perguntaria, depois a solução mínima, por último o que deixaria para depois.
