# Painel de inadimplência — Caprem (case técnico)

Painel local para a área de Cobrança ver **quem está devendo, quanto e de qual
empreendimento**, a partir do CSV de parcelas exportado do sistema.

- A **data de referência é fixa em 25/09/2026** (a do arquivo), nunca a data de hoje.
  Pode ser trocada no painel, só para consulta.
- O **CPF/CNPJ só serve para a busca**: não aparece na tela nem no Excel exportado.
- Os dados são fictícios.

## Requisitos

- Windows com PowerShell
- Python 3.12 (testado com 3.12.6)

## Instalação

Na pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Se o PowerShell bloquear a ativação, rode antes
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.

## Onde fica o CSV

O arquivo já está em `data/parcelas_cobranca_2026-09-25_4.csv` (separador `;`, UTF-8).

Para usar outro arquivo, ele deve ter **esse mesmo nome** e ficar em `data/`.
Se o arquivo faltar, o painel mostra a mensagem "Não encontrei o arquivo de parcelas"
com o caminho esperado. Se o conteúdo tiver problema, mostra a causa
(linha e coluna, quando houver), sem erro técnico na tela.

## Rodar o painel

```powershell
streamlit run app.py
```

O navegador abre em `http://localhost:8501`.

## Testes e conferência

```powershell
python -m unittest discover -s tests -v
python conferir.py
```

`conferir.py` recalcula o total em atraso por empreendimento por um caminho
independente de `regras.py` e compara os dois. Termina com código **0** (sem
divergência) ou **1** (há divergência).

## Resultado esperado

Com a data padrão e sem filtros, o painel e o `conferir.py` devem mostrar
**134 parcelas** e **R$ 625.114,94** em atraso.

## Estrutura de pastas

| Caminho | O que é |
|---|---|
| `app.py` | Painel em Streamlit |
| `tratamento.py` | Leitura e limpeza do CSV, relatório de qualidade dos dados |
| `regras.py` | Regras de inadimplência (carência, faixas de atraso, saldo) |
| `conferir.py` | Conferência independente dos totais |
| `perfil.py` | Diagnóstico inicial do CSV (só relata, não corrige) |
| `contagem_rapida.py` | Contagem rápida de linhas e duplicatas do CSV |
| `tests/` | Testes automáticos de `tratamento.py` e `regras.py` |
| `data/` | CSV de parcelas e `conferir_parcelas.py` (conferência manual do gabarito) |
| `docs/` | Premissas, gabarito, registro de uso de IA, prompts (`docs/ia/`), conversas com a Cobrança (`docs/conversas/`), evidências (`docs/evidencias/`) e o enunciado do case |
| `requirements.txt` | Dependências, com versões fixadas |

## Documentos

- [Premissas adotadas](docs/premissas.md)
- [Gabarito manual](docs/gabarito.md)
- [Registro de uso de IA](docs/registro_ia.md)
- [Conversas com a Cobrança](docs/conversas/)
