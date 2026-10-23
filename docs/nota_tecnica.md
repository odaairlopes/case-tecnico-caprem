# Nota técnica: painel de inadimplência da Cobrança

Para: time de TI. Esta nota descreve o que existe hoje e o que eu mudaria para
rodar todos os dias com dados do sistema.

## 1. Como funciona hoje

**Fluxo:** CSV exportado → `tratamento.py` (leitura, validação e normalização)
→ `regras.py` (cálculo da inadimplência) → `app.py` (painel em Streamlit, local).
O `conferir.py` recalcula os totais por outro caminho, para conferência.

**Onde ficam as regras:** todas em `calcular_inadimplencia` (`regras.py`). O
painel não reimplementa regra nenhuma; só filtra e exibe o resultado. Cada
parcela recebe um único motivo, o primeiro que valer, nesta ordem: contrato não
ativo, financiamento, original de acordo, paga, ainda não venceu, em compensação
(1 a 3 dias) e inadimplente (4 dias ou mais). As premissas e a origem de cada uma
(dados, decisão minha ou resposta da Cobrança) estão em `docs/premissas.md`.

**Decisões principais:**

- **Valores em `Decimal`**, nunca `float`, para não acumular erro de centavos. O
  saldo é valor da parcela menos valor pago.
- **Data de referência fixa em 25/09/2026**, a data do arquivo, e não "hoje". O
  arquivo é um retrato; usar o dia atual mudaria os números sem os dados mudarem.
  O painel permite escolher outra data só para consulta.
- **Carência de 4 dias** (resposta da Cobrança: o boleto leva até 2 dias úteis
  para compensar). Está em `CARENCIA_DIAS`, fixa no código.
- **CPF/CNPJ só para busca:** não é exibido nem exportado.
- **Dado inválido interrompe a carga** com erro de linha e coluna, em vez de virar
  vazio ou ser descartado. Só as duplicatas exatas são removidas (46 linhas do
  contrato 2020156, confirmado pela Cobrança). O painel mostra a mensagem sem
  traceback.
- **Formatos mistos** (datas e valores em dois formatos, status com caixa mista)
  vêm do Loteamento Vista do Horto e são tratados em `tratamento.py`.

**Testes e conferência:**

- 30 testes em `unittest` (19 de `regras.py`, 11 de `tratamento.py`): fronteiras
  da carência e das faixas, acordos, distratados, pagamento parcial e erros de
  leitura. Também rodam com `pytest`.
- `conferir.py` calcula o total em atraso por empreendimento sem importar
  `regras.py` e depois compara. Em 25/09/2026 as duas contas dão 134 parcelas e
  R$ 625.114,94, e o gabarito manual de 4 contratos (`docs/gabarito.md`) também
  bateu. Para confirmar que o teste enxerga um erro, mudei a carência de 4 para 2
  dias e ele apontou divergência (código de saída 1).

## 2. O que mudar para rodar todo dia em produção

- **Leitura direto do banco.** Hoje alguém exporta e salva o CSV, e o arquivo
  pode chegar velho ou errado. Trocar `carregar_dados` por uma consulta
  somente leitura (uma view das parcelas), mantendo a saída no mesmo formato, de
  modo que `regras.py` e o painel não mudem. Usar usuário de banco só de leitura.
- **Agendamento.** Rodar a carga uma vez ao dia, de madrugada, com um agendador
  do próprio ambiente (cron, Agendador de Tarefas ou o orquestrador que o TI já
  use), gravando o resultado calculado e com a hora da atualização visível no
  painel.
- **Logs e monitoramento de erros.** Hoje só há a mensagem na tela. Registrar em
  log cada execução (início, fim, linhas lidas, duplicatas removidas, total
  calculado) e avisar o TI por e-mail ou canal da equipe quando a carga falhar.
  O relatório de qualidade que o painel já gera serve de base.
- **Validação de schema.** Hoje o código confere colunas, tipos e valores
  válidos (status, situação, tipo de parcela). Em produção, tratar também colunas
  novas ou renomeadas, e rejeitar a carga inteira, mantendo os dados do dia
  anterior, em vez de mostrar números parciais.
- **Testes no pipeline.** Rodar os 30 testes e o `conferir.py` a cada alteração e
  antes de publicar, bloqueando a publicação se houver falha. Acrescentar um teste
  para o `app.py`, que hoje não tem, e testes de integração contra o banco de
  homologação.
- **Autenticação e controle de acesso.** O painel hoje abre para quem roda o
  comando. Em produção: login (idealmente o acesso corporativo já existente),
  perfis (por exemplo, só a Cobrança vê telefone) e acesso só pela rede interna.
- **LGPD para CPF/CNPJ e telefone.**
  - Minimização: o CPF/CNPJ já só serve para busca. Em produção, evitar trazê-lo
    ao painel; buscar pelo contrato ou nome, ou mascarar (parcial) no banco.
  - Acesso: limitar telefone e nome a quem precisa, com registro de quem
    consultou e exportou.
  - Retenção: não guardar cópias do CSV e do Excel exportado fora de áreas
    controladas; definir por quanto tempo os arquivos exportados são mantidos.
- **Data de referência = dia da execução.** Hoje é fixa por causa do arquivo de
  exemplo. Em produção deve ser a data da execução, ou da última carga, mantendo o
  seletor só para consulta. Convém decidir com a Cobrança o que fazer quando a
  carga do dia falhar.
- **Regras na configuração.** Mover a carência e as faixas de atraso para um
  arquivo de configuração, para a Cobrança poder mudar sem alterar código.

## 3. Limitações conhecidas desta versão

- **"Clientes inadimplentes" conta contratos de cada cliente**, não pessoas: quem
  tem dois contratos aparece duas vezes (ex.: contratos 1010422 e 1010418).
- **Nomes de clientes não normalizados.** O Loteamento Vista do Horto traz nomes
  em maiúsculas, e a mesma pessoa pode aparecer escrita de duas formas (ex.:
  "Márcia Teixeira Pereira" e "MARCIA TEIXEIRA PEREIRA", com o mesmo telefone).
  Não usei CPF para unificar.
- **Acordo quebrado:** a dívida original não volta; segue a cobrança nas parcelas
  do acordo, conforme a resposta da Cobrança.
- **Sem juros, multa e correção**; o valor é o de face.
- **Sem percentual de inadimplência**, pois falta definir a base de cálculo.
- **Os 30 "clientes"** não foram conferidos contra o gabarito (só 4 contratos
  foram), e não há testes automatizados do `app.py`; o visual foi conferido por
  prints.
- **Telefones** começam todos com (00) e são mostrados como vieram, sem validação
  (dado fictício).
