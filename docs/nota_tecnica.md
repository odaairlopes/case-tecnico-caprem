# Nota técnica: painel de inadimplência da Cobrança

Para: time de TI. Explica como o painel funciona hoje e o que eu mudaria para
rodar todo dia, com dados do sistema.

## 1. Como funciona hoje

**Fluxo:** CSV exportado, `tratamento.py` (leitura e validação), `regras.py`
(cálculo) e `app.py` (painel em Streamlit, rodando local). O `conferir.py`
refaz os totais por outro caminho, só para conferir.

**Regras:** ficam todas em `calcular_inadimplencia`, no `regras.py`. O painel
não refaz regra nenhuma, só filtra e mostra. Cada parcela recebe um único motivo,
o primeiro que valer: contrato não ativo, financiamento, original de acordo, paga,
ainda não venceu, em compensação (1 a 3 dias) e inadimplente (4 dias ou mais). A
origem de cada premissa está em `docs/premissas.md`.

**Decisões principais:**

- Valores em `Decimal`, não `float`, para não errar centavos. Saldo é valor da
  parcela menos valor pago.
- Data de referência fixa em 25/09/2026, a do arquivo. Com "hoje", os números
  mudariam sem os dados mudarem. O painel deixa escolher outra data, só para
  consulta.
- Carência de 4 dias, por resposta da Cobrança (o boleto leva até 2 dias úteis
  para compensar). Está em `CARENCIA_DIAS`, fixa no código.
- CPF/CNPJ só para busca. Não aparece na tela nem no Excel.
- Dado inválido interrompe a carga, com erro de linha e coluna. Nada vira vazio
  nem é descartado em silêncio. A única remoção é de duplicatas exatas (46 linhas
  do contrato 2020156, confirmadas pela Cobrança). O painel mostra a mensagem sem
  traceback.
- Datas e valores em dois formatos, e status com caixa mista, vêm do Loteamento
  Vista do Horto. O `tratamento.py` resolve isso.

**Testes e conferência:**

- 30 testes em `unittest` (19 de `regras.py` e 11 de `tratamento.py`). Cobrem as
  fronteiras da carência e das faixas, acordos, distratados, pagamento parcial e
  erros de leitura. Também rodam no `pytest`.
- O `conferir.py` calcula o total em atraso por empreendimento sem importar o
  `regras.py` e depois compara. Em 25/09/2026 os dois dão 134 parcelas e
  R$ 625.114,94. O gabarito manual de 4 contratos (`docs/gabarito.md`) também
  bateu.
- Para ver se a conferência pega erro, troquei a carência de 4 para 2 dias. Ela
  apontou divergência e saiu com código 1.

## 2. O que mudar para rodar todo dia em produção

- **Banco em vez de CSV.** Hoje alguém exporta e salva o arquivo, que pode chegar
  velho ou errado. Eu trocaria `carregar_dados` por uma consulta de leitura numa
  view das parcelas, mantendo o mesmo formato de saída. Assim `regras.py` e o
  painel não mudam. O usuário do banco seria só de leitura.
- **Agendamento.** Uma carga por dia, de madrugada, no agendador que o TI já usa
  (cron, Agendador de Tarefas ou outro). O painel mostraria a hora da última
  atualização.
- **Logs e erros.** Hoje só existe a mensagem na tela. Eu registraria em log cada
  execução (início, fim, linhas lidas, duplicatas removidas, total calculado) e
  avisaria o TI quando a carga falhar. O relatório de qualidade que o painel já
  gera serve de base.
- **Validação de schema.** O código já confere colunas, tipos e valores válidos.
  Em produção, eu trataria também coluna nova ou renomeada. Se a carga falhar, o
  painel manteria os dados do dia anterior em vez de mostrar número parcial.
- **Testes no pipeline.** Rodar os 30 testes e o `conferir.py` a cada mudança, e
  barrar a publicação se algo falhar. Falta teste para o `app.py`, e faltam testes
  contra um banco de homologação.
- **Acesso.** Hoje abre para quem roda o comando. Em produção: login (de
  preferência o corporativo), perfis (por exemplo, só a Cobrança vê telefone) e
  acesso só pela rede interna.
- **LGPD (CPF/CNPJ e telefone).** O CPF/CNPJ já serve só para busca. Em produção,
  eu evitaria trazê-lo ao painel e buscaria por contrato ou nome, ou o
  mascararia no banco. Nome e telefone ficariam só para quem precisa, com registro
  de quem consultou e exportou. Os Excel exportados não devem ficar soltos, e
  precisa haver prazo de guarda.
- **Data de referência.** Hoje é fixa por causa do arquivo de exemplo. Em
  produção seria a data da última carga, e o seletor ficaria só para consulta.
  Falta combinar com a Cobrança o que mostrar quando a carga do dia falhar.
- **Carência e faixas em configuração**, para a Cobrança poder mudar sem mexer no
  código.

## 3. Limitações conhecidas

- "Clientes inadimplentes" conta contratos de cada cliente, não pessoas. Quem tem
  dois contratos aparece duas vezes (ex.: 1010422 e 1010418).
- Os nomes não são normalizados. O Vista do Horto traz nomes em maiúsculas, e a
  mesma pessoa pode aparecer de dois jeitos ("Márcia Teixeira Pereira" e "MARCIA
  TEIXEIRA PEREIRA", com o mesmo telefone). Não usei CPF para juntar.
- Acordo quebrado: a dívida original não volta, e a cobrança segue nas parcelas
  do acordo, como a Cobrança respondeu.
- Sem juros, multa e correção. O valor é o da parcela.
- Sem percentual de inadimplência, porque falta definir a base de cálculo.
- Só 4 contratos foram conferidos contra o gabarito. Os 30 "clientes" não foram.
  Não há teste automático do `app.py`, e o visual foi conferido por prints.
- Os telefones começam todos com (00) e aparecem como vieram, sem validação (dado
  fictício).
