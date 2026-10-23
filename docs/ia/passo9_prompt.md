Crie o README.md na raiz, em português, para o avaliador de um case técnico
(Caprem, dashboard de inadimplência) rodar a solução sem ajuda. Leia os
arquivos reais antes de escrever; não invente comandos, arquivos nem
resultados. Não altere nenhum outro arquivo. Seja curto e direto.

Conteúdo:
1. O que faz: painel local para a Cobrança ver quem deve, quanto e de qual
   empreendimento, a partir do CSV exportado. Data de referência fixa em
   25/09/2026 (nunca hoje). CPF/CNPJ só serve para busca e não aparece na
   tela nem no Excel.
2. Requisitos: versão do Python e Windows/PowerShell.
3. Instalação: criar venv, ativar e `pip install -r requirements.txt`.
4. CSV: já está em `data/parcelas_cobranca_2026-09-25_4.csv` (separador `;`,
   UTF-8; dados fictícios). Diga que, para usar outro arquivo, ele deve ter
   o mesmo nome e ficar em `data/`, e o que o app mostra se o arquivo faltar.
5. Rodar o dashboard: `streamlit run app.py`.
6. Testes: `python -m unittest discover -s tests -v`. Conferência
   independente: `python conferir.py` (código 0 = sem divergência).
7. Resultado esperado (data padrão, sem filtros): 134 parcelas e
   R$ 625.114,94, para conferir que funcionou.
8. Estrutura de pastas, só o que existe, uma linha cada.
9. Links para docs/premissas.md e docs/registro_ia.md.

Cada comando deve poder ser copiado e colado. Ao final, liste o que você
rodou e o que não conseguiu verificar.

(Prompt do guia, passo 9, revisado: o original era só "Crie o README.md com:
o que o projeto faz, requisitos, como instalar, como rodar o dashboard, os
testes e a conferência, estrutura de pastas e onde colocar o CSV". Acrescentei
o comando real dos testes, a conferência com código de saída, o resultado
esperado, a regra de não inventar comandos e o pedido de listar o que foi
verificado.)
