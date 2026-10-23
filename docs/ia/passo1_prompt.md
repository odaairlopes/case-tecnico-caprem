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
