Pedido A (resumo para a Renata):

Redija docs/resumo_renata.md, em português, para a Renata Oliveira
(Coordenação de Cobrança), que não é da área técnica. No máximo 2 páginas
(cerca de 600 palavras), tom direto e cordial, sem termos técnicos (nada de
CSV, DataFrame, Decimal, cache, venv, código, nomes de colunas do banco).

Base: leia app.py, regras.py, docs/premissas.md, docs/gabarito.md e
docs/conversas/. Não invente números, funções nem respostas dela; use só o
que existe nesses arquivos e o que o painel de fato faz.

Estrutura, com estes quatro títulos:
1. O problema que entendi: ela filtra o relatório na mão todo mês para ver
   quem deve, quanto e de qual empreendimento.
2. O que a solução faz: cartões, filtros, gráficos, tabela por contrato,
   busca por nome ou CPF, exportação para Excel, data de referência. Cite o
   resultado de 25/09/2026 (134 parcelas e R$ 625.114,94 em atraso) e
   como usar, em 3 passos simples.
3. Premissas que adotei, em linguagem de negócio (data de referência, a
   partir de quantos dias conta como atraso, como calculei o saldo, o que fica
   fora da cobrança, acordos, contratos distratados e quitados). Marque o que
   ainda precisa da confirmação dela.
4. O que ficou de fora desta versão, com base em docs/premissas.md.

Não use markdown pesado (tabelas grandes, muitos aninhados). Ao final, liste
quais afirmações você não conseguiu confirmar nos arquivos.

Pedido B (nota técnica para o TI):

Redija docs/nota_tecnica.md, em português, curta (até 2 páginas), para o
time de TI. Leia o código real (app.py, regras.py, tratamento.py,
conferir.py, tests/, requirements.txt) e descreva só o que existe; não
invente módulos nem comportamento.

Parte 1: Como funciona hoje: fluxo (CSV, tratamento, regras, painel),
onde ficam as regras, decisões principais (Decimal para valores, data de
referência fixa, carência de 4 dias, CPF só para busca), os testes (30) e a
conferência independente (conferir.py).

Parte 2: O que mudar para rodar todo dia em produção, cada item com o
motivo e uma sugestão concreta e proporcional (sem exagero):
- leitura direto do banco do sistema, em vez de CSV
- agendamento da atualização
- logs e monitoramento de erros
- validação de schema dos dados de entrada
- testes automatizados no pipeline
- autenticação e controle de acesso ao painel
- LGPD para CPF/CNPJ e telefone (minimização, acesso, retenção)
- data de referência = dia da execução, em vez da data fixa

Parte 3: Limitações conhecidas desta versão (use docs/registro_ia.md:
nomes de clientes não normalizados, "clientes" conta contratos, e outras que
estiverem lá).

Ao final, liste o que você afirmou sem poder confirmar no código.

(Prompt do guia, passo 10, revisado: o original era um pedido único com os dois
documentos. Separei em dois, passei as fontes reais, o tamanho, o tom e a regra
de não inventar, e pedi a lista do que não foi confirmado.)
