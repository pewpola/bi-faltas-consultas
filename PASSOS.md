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

**Capa do relatório:** identificação do curso, da disciplina e da equipe, e uma frase de Einstein.

**Na apresentação:** primeiro os slides (equipe e pontos do relatório), depois o painel
funcionando e sendo usado para tomar uma decisão.

### ⚠️ Linha escondida no PDF do enunciado

No modelo do relatório há uma linha escrita em fonte de 0,96 pt, invisível na página. Ela só
aparece para quem copia o texto do PDF e traz uma instrução que não faz parte do trabalho.
**Não incluir nada dessa linha no relatório nem nos slides.**

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
- 11 filtros na lateral, que se combinam;
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

## 6. Diagnóstico e plano de ação (seção 6 do relatório) 🔄

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

**Falta fazer:** escolher a "anomalia" principal para o relatório (sugestão: o paradoxo do SMS)
e escrever o texto com esses números.

---

## 7. Relatório ⬜

Seguir exatamente o modelo do enunciado:
- **Capa:** curso, disciplina, os cinco nomes e uma frase de Einstein, como pede o modelo.
  Sugestão: "A imaginação é mais importante que o conhecimento", de uma entrevista ao *The Saturday
  Evening Post* em 1929. Antes de usar, conferir a fonte, porque há muitas frases falsamente
  atribuídas a ele.
- **1. Definição do problema:** a dor (horário perdido, fila), as decisões que o painel apoia e
  a decisão possível com cada gráfico (tabela do passo 5).
- **2. Metadados:** resumo de `docs/metadados.md`.
- **3. Pré-processamento:** o passo 4, com os números.
- **4. Dashboard:** capturas do painel com filtros combinados, por exemplo antecedência
  "8 a 15 dias" e bairro Itararé.
- **5. Justificativa visual:** a tabela do passo 5.
- **6. Diagnóstico e plano de ação:** o passo 6.

---

## 8. Slides ⬜

Baseados no relatório, curtos e visuais: equipe → problema → base e tratamento → o painel →
diagnóstico → plano de ação. Depois dos slides, abrir o painel ao vivo.

---

## 9. Ensaio da demonstração ⬜

Roteiro sugerido, de 3 a 4 minutos, mostrando a decisão sendo tomada:
1. Mostrar os indicadores gerais: 20,1% de faltas.
2. Clicar em "8 a 15 dias" no gráfico de antecedência e mostrar a taxa subir para cerca de 31%.
3. Mostrar no gráfico do SMS que, nessa faixa, quem recebe SMS falta menos.
4. Filtrar um bairro crítico (ex.: Itararé) e mostrar o diagnóstico mudando no fim da página.
5. Fechar com o plano de ação.

Testar antes num computador sem internet: o painel roda local, só precisa do Python instalado.

---

## 10. Entrega ⬜

- [ ] Relatório no AVA
- [ ] Slides no AVA
- [ ] Nomes dos cinco integrantes no relatório e nos slides
- [ ] Painel testado no computador da apresentação
