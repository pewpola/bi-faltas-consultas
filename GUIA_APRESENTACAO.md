# Guia da apresentação

Roteiro de fala, slide a slide, para a apresentação fluir sem leitura de slide. Tempo total previsto:
**cerca de 11 minutos de slides e 4 minutos de painel ao vivo**.

Painel publicado: **https://bi-faltas-consultas.streamlit.app/** (ou local, com `streamlit run app.py`, em http://localhost:8501).

Arquivos: [apresentacao/Apresentacao_Painel_BI_Faltas_Consultas.pptx](apresentacao/Apresentacao_Painel_BI_Faltas_Consultas.pptx)
(as notas de cada slide estão no próprio PowerPoint) e o PDF ao lado dele.

## Quem apresenta cada slide

O número de cada slide aparece no topo dele, junto com o tema (ex.: "03 · Pré-processamento").

| Slide | Tema | Quem | Tempo |
|---|---|---|---|
| 1 | Capa e equipe | Eduardo | 0,5 min |
| 2 | O problema e a base | Eduardo | 1,5 min |
| 3 | Pré-processamento | Eduardo | 1,5 min |
| 4 | Painel interativo | Diego | 1 min |
| 5 | Justificativa visual | Davi | 1 min |
| 6 | Diagnóstico | Davi | 1,5 min |
| 7 | Diagnóstico: a anomalia | Ian | 1,5 min |
| 8 | Prescrição (plano de ação) | Larissa | 1,5 min |
| 9 | Valor para o negócio | Larissa | 1 min |
| Ao vivo | Demonstração do painel (entre os slides 9 e 10) | Eduardo, no computador | 4 min |
| 10 | Obrigado e perguntas | todos | |

## Roteiro

**Slide 1 · Capa e equipe (Eduardo).** Apresentar os cinco integrantes. Depois: "De cada cinco consultas marcadas na
rede pública de Vitória, uma termina em falta. Vamos mostrar quem falta, onde, em que situação e o que fazer."

**Slide 2 · O problema e a base (Eduardo).** Os três números: 22.084 faltas, 20,1% e 849 horários perdidos por dia.
As três decisões que o painel apoia: lembrete, confirmação e prioridade. Fechar com a base: pública, do Kaggle, dados
reais e anonimizados de 2016, uma linha por consulta (quem, quando, onde, saúde, SMS e se faltou), escolhida por ter
um problema real, muitas dimensões e sujeira de verdade para tratar. Alertar sobre o rótulo "No-show": "Yes" quer
dizer que faltou.
→ *Ligação:* "Antes de analisar, foi preciso limpar e tratar os dados."

**Slide 3 · Pré-processamento (Eduardo).** Dizer que são dados estruturados: uma tabela, colunas fixas. Depois as três
colunas do slide: limpeza (sem nulos, 618 duplicatas, idades impossíveis, consultas antes do agendamento),
transformação (arquivo de CSV para Parquet, texto para data, No-show em 1/0, moedas não se aplicam, 9 colunas novas)
e redução (sábado isolado, bairros pequenos e só as colunas úteis). Fechar: de 110.527 para 109.839 consultas, 0,6%
das linhas retiradas, tudo registrado.
→ *Passa para o Diego:* "Com a base limpa, construímos o painel. O Diego mostra como ele funciona."

**Slide 4 · Painel interativo (Diego).** "Todos os gráficos se filtram entre si." Mostrar na captura os dois filtros
somados: Itararé na lateral e o clique em "8 a 15 dias". A taxa vai a 37,1%, e a falta com SMS fica em 33,0%, contra
43,8% sem SMS, no mesmo recorte. "É isso que vamos fazer ao vivo no final."
→ *Passa para o Davi:* "O Davi explica por que escolhemos cada gráfico e o que eles mostraram."

**Slide 5 · Justificativa visual (Davi).** Barras para comparar, linha para tempo, cartões para os números-chave; as
cores têm função (coral = falta, verde = SMS, cinza = comparação). Não usamos pizza nem 3D.
→ *Ligação:* "Agora, o que o painel nos mostrou."

**Slide 6 · Diagnóstico (Davi).** A espera: 4,6% no mesmo dia contra 32,0% com 8 dias ou mais. A reincidência: 28,3%
contra 18,7%. Onde e quem: os bairros do topo, adolescentes e Bolsa Família acima da média.
→ *Passa para o Ian:* "Mas o achado mais curioso foi com o SMS. O Ian mostra."

**Slide 7 · Diagnóstico: a anomalia (Ian).** O ponto alto da apresentação. Primeiro o gráfico da esquerda: "parece
que o SMS aumenta a falta". Depois o da direita: "na mesma espera, o SMS reduz a falta em todas as faixas". Explicar o
porquê: o SMS só vai para consultas com 3 dias ou mais, que já faltam mais. "Esse achado só aparece combinando filtros."
→ *Passa para a Larissa:* "Com isso, propomos um plano de ação. A Larissa apresenta."

**Slide 8 · Prescrição (Larissa).** As cinco ações em ordem de prioridade, destacando as duas primeiras. Fechar com
"o próprio painel mede cada ação".

**Slide 9 · Valor para o negócio (Larissa).** 1.242 faltas evitáveis, cerca de 48 por dia, com um canal que a rede já
tem. Ser honesto: é associação, por isso a proposta de começar por alguns bairros e comparar.
→ *Passa para o Eduardo:* "Agora o Eduardo mostra o painel funcionando."

**Ao vivo · Demonstração (Eduardo, entre os slides 9 e 10).** Trocar para o navegador com o painel **já aberto** e
seguir os passos:
1. Mostrar os indicadores gerais (20,1%) e o gráfico de antecedência.
2. Clicar em "8 a 15 dias": a taxa vai a 30,8% e todo o painel se refaz.
3. Escolher Itararé em "Bairro da unidade" na lateral: 37,1%; no gráfico de SMS, 43,8% sem e 33,0% com.
4. Descer até "Diagnóstico e plano de ação" e ler a recomendação do recorte em voz alta.
5. Voltar ao início com "Limpar todos os filtros".

Depois, voltar para os slides.

**Slide 10 · Obrigado (todos).** Agradecer e abrir para perguntas. Os passos da demonstração também estão nas notas
deste slide.

## Antes de apresentar

- [ ] Painel aberto no computador da apresentação e testado com os passos acima: o link publicado
  (https://bi-faltas-consultas.streamlit.app/) ou o local (`streamlit run app.py`).
- [ ] Abrir o link publicado **alguns minutos antes**: depois de dias sem acesso, o Streamlit Cloud "dorme" e leva
  cerca de 30 segundos para acordar.
- [ ] Navegador com zoom em que os gráficos caibam na tela do projetor.
- [ ] PowerPoint em modo apresentador, para ver as notas de cada slide.
- [ ] Plano B: se a internet falhar, usar a versão local; se o computador falhar, o slide 4 mostra a mesma
  demonstração em captura de tela.

## Perguntas prováveis

**Os dados são reais?** Sim, agendamentos reais e anonimizados de Vitória (ES), publicados no Kaggle. A fonte é quem
publicou no Kaggle, não um portal oficial do governo. Conferimos duas cópias independentes do arquivo, idênticas.

**Os dados são estruturados?** Sim: uma única tabela, com 14 colunas de esquema fixo e uma linha por consulta. Não há
texto livre, imagem nem JSON. No tratamento, convertemos os tipos (texto para data, rótulos para números) e o arquivo,
de CSV para Parquet.

**Por que não há padronização de moeda?** A base não tem nenhum valor em dinheiro. Dissemos isso no relatório.

**Como vocês sabem que o SMS reduz a falta?** Comparando consultas com a mesma espera, quem recebe SMS falta menos em
todas as faixas. É uma associação, não uma prova de causa; por isso propomos começar por alguns bairros e comparar.

**De onde vêm as 1.242 faltas evitáveis?** Para cada faixa de espera, aplicamos às consultas sem SMS a diferença de
falta entre quem recebeu e quem não recebeu, e somamos.

**Por que tiraram o sábado e alguns bairros?** O sábado era um único dia, fora do padrão de segunda a sexta. Os
bairros tinham menos de 30 consultas, e com tão poucas consultas a taxa não é confiável.

**Por que Streamlit e não Power BI?** O enunciado deixa a ferramenta livre. Em Python, o tratamento e o painel ficam
no mesmo projeto e qualquer pessoa consegue refazer tudo do zero com três comandos.
