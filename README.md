# Faltas em consultas: painel de BI interativo

Trabalho final da disciplina: um painel de BI interativo, feito em Python com Streamlit,
sobre as faltas em consultas nas unidades públicas de saúde de Vitória (ES).

**Equipe:** Davi Salgueiro, Diego Benevides, Eduardo Jorge, Ian Waki e Larissa Elias.

## O problema

Uma em cada cinco consultas marcadas termina em falta (20,1% na base tratada). Cada falta é um
horário de médico parado e uma pessoa a mais esperando na fila. O painel ajuda o gestor da rede
a responder três perguntas: **quem falta**, **onde** e **em que situação**. Com isso, ele decide
onde confirmar presença, para quem mandar lembrete e onde fazer busca ativa.

## Como rodar

Precisa de Python 3.12 ou mais novo.

```bash
python3 -m venv .venv
source .venv/bin/activate          # no Windows: .venv\Scripts\activate
pip install -r requirements.txt

python src/preparar_dados.py       # limpa e transforma a base (gera dados/tratado/)
python src/gerar_metadados.py      # gera o dicionário de dados (docs/metadados.md)
streamlit run app.py               # abre o painel no navegador
```

A base tratada já vem no repositório, então dá para pular direto para o `streamlit run app.py`.

## Como usar o painel

- **Filtros da lateral:** período, bairro, antecedência, idade, sexo, SMS, Bolsa Família,
  histórico de faltas e condições de saúde. Eles se combinam.
- **Clique nos gráficos:** clicar numa barra ou ponto filtra todos os outros gráficos.
  Segure Shift para escolher mais de um item. O botão "Limpar seleções" desfaz.
- **Diagnóstico e plano de ação:** no fim da página, os números e as recomendações se
  recalculam para o recorte escolhido.

## Relatório e slides

Os números do relatório e dos slides vêm da mesma base do painel:

```bash
python src/dados_apresentacao.py   # junta os números em apresentacao/dados.json
python src/capturas.py             # capturas do painel (precisa do painel aberto e do Playwright)
python src/relatorio.py            # gera relatorio/Relatorio_Painel_BI_Faltas_Consultas.docx
cd apresentacao && npm install && node build.js   # gera os slides (.pptx)
```

O PDF do relatório sai do Word (Salvar como PDF) ou do LibreOffice:
`soffice --headless --convert-to pdf --outdir relatorio relatorio/Relatorio_Painel_BI_Faltas_Consultas.docx`.
O Playwright (`pip install playwright && playwright install chromium`) só é necessário para as capturas de tela.

## Pastas

```
app.py                      o painel
src/preparar_dados.py       limpeza, transformação e redução da base
src/gerar_metadados.py      gera o dicionário de dados
dados/bruto/                base original e de onde ela veio (FONTE.md)
dados/tratado/              base pronta para o painel e o registro do tratamento
docs/metadados.md           dicionário de dados (seção 2 do relatório)
src/dados_apresentacao.py   números do relatório e dos slides
src/capturas.py             capturas de tela do painel
src/relatorio.py            gera o relatório em Word (.docx)
figuras/                    capturas do painel usadas no relatório e nos slides
relatorio/                  relatório final (.docx e .pdf)
apresentacao/               slides (build.js gera o .pptx) e os dados da capa
PASSOS.md                   roteiro do projeto, do enunciado até a entrega
GUIA_APRESENTACAO.md        roteiro de fala e da demonstração ao vivo
```

## Fonte dos dados

"Medical Appointment No Shows", publicada por Joni Hoppen no Kaggle:
https://www.kaggle.com/datasets/joniarroba/noshowappointments. Detalhes em
[dados/bruto/FONTE.md](dados/bruto/FONTE.md).
