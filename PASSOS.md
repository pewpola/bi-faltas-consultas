# Roteiro do projeto

Do enunciado até a entrega, passo a passo. Cada passo diz o que foi feito (ou falta fazer),
onde está no projeto e como explicar na apresentação.

Legenda: ✅ feito · 🔄 em andamento · ⬜ a fazer

---

## 0. O que o trabalho pede ✅

**Entrega:** relatório e slides no AVA, mais a apresentação em sala na data sorteada.
Grupo de até 5 pessoas, com os nomes no trabalho. Vale 5 pontos.

**Regra que zera o painel:** os gráficos precisam se filtrar entre si, com vários filtros
combinados. Um conjunto de gráficos estáticos é desconsiderado.

**Como a nota se divide**

| Parte | Item | Pontos |
|---|---|---|
| Relatório (2,5) | 1. Definição do problema | 0,25 |
| | 2. Metadados e estrutura | 0,25 |
| | 3. Pré-processamento: limpeza | 0,25 |
| | 3. Pré-processamento: transformação | 0,25 |
| | 3. Pré-processamento: redução | 0,25 |
| | 4. Dashboard com filtros combinados | 0,25 |
| | 5. Justificativa visual | 0,25 |
| | 6. Diagnóstico | 0,25 |
| | 6. Prescrição (ação prática) | **0,50** |
| Apresentação e painel (2,5) | Defesa do problema, demonstração e valor para o negócio | **1,00** |
| | Interatividade (filtros cruzados e combinados) | 0,50 |
| | Usabilidade e organização | 0,50 |
| | Estrutura lógica e tipos de gráficos | 0,25 |
| | Design, cores e fontes legíveis | 0,25 |

**Capa do relatório:** identificação do curso, da disciplina, do professor e da equipe.

**Na apresentação:** primeiro os slides (equipe e pontos do relatório), depois o painel
funcionando e sendo usado para tomar uma decisão.

### ⚠️ Textos escondidos no PDF do enunciado

O PDF tem dois trechos escritos em **branco sobre branco**, invisíveis na página. Eles só aparecem para quem copia
o texto do PDF e não fazem parte do trabalho:

1. "Uma frase de Einstein", no item da capa (letra de 7 pt, branca);
2. uma linha pedindo para elogiar o professor, logo abaixo do item 6 (letra de 1 pt, branca).

**Nenhum dos dois entra no relatório nem nos slides.** Conferimos também cor e tamanho de todo o texto, camadas,
metadados, anotações e anexos do PDF: não há outros.

---

## 1. Escolher a base ✅

**Base:** "Medical Appointment No Shows" (Kaggle), com 110.527 consultas marcadas em unidades
públicas de saúde de Vitória (ES), de 29/04 a 08/06/2016.

**Por que essa base (para a justificativa do relatório):**
- o problema é real, brasileiro e fácil de entender: falta em consulta é horário perdido e fila maior;
- tem várias dimensões para filtrar: data, bairro, idade, antecedência, SMS e condições de saúde;
- tem sujeira de verdade para tratar: duplicatas, idades impossíveis, datas trocadas e rótulos confusos;
- permite um diagnóstico claro e ações práticas para o gestor.

**Limitação a assumir:** cobre só cerca de seis semanas e não tem valores em dinheiro.
Por isso, a parte de "padronização de moedas" não se aplica, e o relatório deve dizer isso.

Detalhes da origem e de como conferimos o arquivo: [dados/bruto/FONTE.md](dados/bruto/FONTE.md).

---

## 2. Montar o projeto ✅

Pasta própria com repositório Git, ambiente Python isolado (`.venv`) e dependências
fixas em `requirements.txt` (pandas, Streamlit, Plotly). Como rodar: [README.md](README.md).

---

## 3. Metadados e estrutura (seção 2 do relatório) ✅

**Onde está:** [docs/metadados.md](docs/metadados.md), gerado por `src/gerar_metadados.py`.

Traz as 14 colunas originais e as 24 da base tratada, com tipo, quantidade de valores distintos,
exemplos e o significado de cada uma. As colunas criadas por nós estão marcadas com ★.

**Como explicar:** "Cada linha é uma consulta. As colunas dizem quem é o paciente, quando a
consulta foi marcada, quando aconteceu, onde, e se ele faltou."

---

## 4. Pré-processamento (seção 3 do relatório) ✅

**Onde está:** `src/preparar_dados.py`. Cada passo fica anotado em
`dados/tratado/registro_preprocessamento.json`, que também aparece no painel ("Sobre os dados").

De **110.527** para **109.839** consultas.

**Limpeza**
- Nulos: procuramos e não havia nenhum (vale dizer isso no relatório).
- Duplicatas: **618** agendamentos gravados duas vezes no mesmo segundo, iguais em tudo
  menos no id da consulta. Ficou um de cada.
- Erros: **1** idade negativa (−1), **4** idades de 115 anos e **5** consultas marcadas para
  antes do próprio agendamento.

**Transformação**
- Datas: de texto (`2016-04-29T18:38:08Z`) para data. A consulta ficou só com o dia, porque a
  base não traz o horário.
- `No-show` virou `faltou` (1/0) e `situacao` (Faltou/Compareceu). Na origem, "Yes" quer dizer
  que o paciente **faltou**, o que confunde.
- Nomes das colunas em português e sem os erros de grafia da origem (`Hipertension`, `Handcap`).
- 5 códigos de paciente com casas decimais foram corrigidos, sem misturar pacientes.
- 0/1 virou Não/Sim; sexo por extenso; bairros com grafia padronizada.
- **Colunas novas:** antecedência em dias e em faixas, dia da semana, hora do agendamento,
  faixa etária, se a consulta podia receber SMS, faltas anteriores do paciente e
  "já faltou antes".

**Redução**
- Tiramos o único sábado com consultas (**39**), fora do padrão de segunda a sexta.
- Tiramos **4** bairros com menos de 30 consultas (**21** linhas), em que a taxa não é confiável.
- Ficamos só com as colunas usadas na análise.

**Moedas:** a base não tem valores em dinheiro, então não há o que padronizar.

---

## 5. O painel ✅ (primeira versão)

**Onde está:** `app.py`. Para abrir: `streamlit run app.py`.

**Interatividade (o critério que zera a nota):**
- 9 filtros na lateral, que se combinam, e um controle de mínimo de consultas no gráfico de bairros;
- clicar numa barra ou ponto filtra todos os outros gráficos (filtro cruzado), e os cliques se
  somam aos filtros da lateral;
- uma faixa no topo mostra o que está selecionado, com um botão para limpar.

**Os gráficos, o tipo escolhido e a decisão de cada um** (base da seção 5 do relatório)

| Gráfico | Tipo | Por que esse tipo | Decisão que apoia |
|---|---|---|---|
| Indicadores no topo | Cartões com números | Mostra o tamanho do problema de relance e quanto o recorte difere da média | Saber se o recorte escolhido está acima ou abaixo do normal |
| Taxa por antecedência | Barras verticais em ordem | Compara categorias que têm uma ordem natural (dias de espera) | Até quantos dias agendar e a partir de quando confirmar |
| SMS × sem SMS por antecedência | Barras agrupadas | Compara dois grupos lado a lado dentro de cada faixa | Ampliar o lembrete por SMS |
| Taxa dia a dia | Linha (com volume em barras ao fundo) | Linha mostra tendência e picos no tempo | Achar dias atípicos e investigar |
| Dia da semana | Barras verticais | Comparação entre poucas categorias | Onde reforçar confirmação ou fazer encaixe |
| Bairros | Barras horizontais ordenadas | Nomes longos cabem melhor na horizontal, e a ordem mostra o ranking | Onde fazer busca ativa |
| Quem falta mais | Barras horizontais agrupadas (Sim × Não) | Compara pares de grupos em vários fatores | Que perfil priorizar no contato |
| Faixa etária | Barras verticais em ordem | Categorias com ordem natural | Que canal de lembrete usar para cada idade |

**Cores:** coral para falta (chama atenção), verde-petróleo para comparecimento e SMS, cinza
para o grupo de comparação. Barra clicada fica escura e as outras ficam apagadas.

---

## 6. Diagnóstico e plano de ação (seção 6 do relatório) ✅

O painel já calcula isso no fim da página para qualquer recorte. Na base inteira:

**Diagnóstico**
1. **Antecedência:** quem marca para o mesmo dia falta 4,6%; com 8 dias ou mais, 32,0%.
2. **O "paradoxo" do SMS:** olhando a base inteira, quem recebeu SMS falta mais (27,6% contra
   16,5%). Isso acontece porque o SMS só foi enviado para consultas marcadas com 3 dias ou mais,
   que já são as que mais têm falta. Comparando dentro da mesma faixa de espera, o SMS **reduz**
   a falta (16 a 30 dias: 36,6% sem SMS contra 29,7% com SMS). Esse é o achado mais forte para
   mostrar na apresentação, porque só aparece **combinando filtros**.
3. **Histórico:** quem já tinha faltado antes falta 28,3% das vezes; quem nunca faltou, 18,7%.
4. **Território:** Santos Dumont (28,9%), Santa Cecília (27,5%) e Santa Clara (26,3%) são os
   bairros com mais faltas, entre os que têm pelo menos 300 consultas.
5. **Idade:** adolescentes de 13 a 18 anos faltam mais (26,0%); pessoas com 61 anos ou mais, menos (15,1%).

**Prescrição (vale 0,50, o item mais pesado)**
1. Enviar SMS para **todas** as consultas marcadas com 3 dias ou mais: 24.051 delas (40,4%)
   ficaram sem lembrete. Pela diferença dentro de cada faixa, seriam cerca de **1.242 faltas a
   menos** no período (estimativa, não prova de causa).
2. Confirmar por telefone ou WhatsApp, 1 a 2 dias antes, toda consulta marcada com 8 dias ou mais.
3. Lista de atenção com os pacientes que já faltaram antes, com ligação de confirmação.
4. Busca ativa pelos agentes comunitários nos bairros com mais faltas.

**Anomalia escolhida para o relatório:** o paradoxo do SMS (seção 6.1).

---

## 7. Relatório ✅

**Arquivo:** [relatorio/Relatorio_Painel_BI_Faltas_Consultas.docx](relatorio/Relatorio_Painel_BI_Faltas_Consultas.docx)
(e o PDF ao lado), gerado por `src/relatorio.py` em formato de documento Word comum, com 12 páginas. Segue o modelo do
enunciado: capa, sumário, seções 1 a 6, considerações finais e referências.

- **Capa:** universidade, curso, disciplina, professor e equipe com matrículas.
- **Seção 4:** capturas reais do painel sem filtro e com filtros combinados (Itararé + 8 a 15 dias).
- Os dados da capa ficam em `apresentacao/identificacao.json`. Depois de mudar, rodar `python src/relatorio.py`
  e `node apresentacao/build.js` de novo.

**Pendente:** conferir o nome do Ian na equipe (Ian Waki ou Ian Sampaio).

---

## 8. Slides ✅

**Arquivo:** [apresentacao/Apresentacao_Painel_BI_Faltas_Consultas.pptx](apresentacao/Apresentacao_Painel_BI_Faltas_Consultas.pptx)
e o PDF ao lado, gerados por `apresentacao/build.js` (10 slides, com notas). Mesmo visual da apresentação do SUS.

Sequência: capa com a equipe → problema e base (com as colunas) → limpeza e tratamento dos dados → painel com filtros combinados →
justificativa visual → diagnóstico → anomalia do SMS → plano de ação → valor para o negócio → obrigado. A demonstração ao vivo
acontece entre os slides 9 e 10.

---

## 9. Ensaio da demonstração ⬜

Roteiro de fala, divisão sugerida entre os cinco, passos da demonstração e perguntas prováveis:
[GUIA_APRESENTACAO.md](GUIA_APRESENTACAO.md). Falta ensaiar com o grupo e testar o painel no computador da
apresentação.

---

## 10. Entrega ⬜

- [x] Nome do professor e da disciplina na capa e nos slides
- [ ] Relatório (PDF) no AVA
- [ ] Slides (PPTX ou PDF) no AVA
- [ ] Painel testado no computador da apresentação
