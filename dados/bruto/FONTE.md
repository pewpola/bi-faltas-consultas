# De onde vem a base

**Arquivo:** `KaggleV2-May-2016.csv`

**Base original:** "Medical Appointment No Shows", publicada por Joni Hoppen no Kaggle:
https://www.kaggle.com/datasets/joniarroba/noshowappointments

Ela reúne 110.527 consultas marcadas em unidades públicas de saúde de Vitória (ES), com
datas de consulta entre 29/04/2016 e 08/06/2016. Cada linha é uma consulta, e a coluna
`No-show` diz se o paciente faltou.

## Como baixamos

O Kaggle exige login para baixar. Por isso, usamos cópias públicas do mesmo arquivo no GitHub.
Para garantir que a cópia é fiel, comparamos duas cópias independentes:

- `Kovyljan/sf_data_science` (`EDA-5.../data/KaggleV2-May-2016.csv`)
- `TokoniK/exploratory-data-analysis` (`data/Database_No_show_appointments/noshowappointments-kagglev2-may-2016.csv`)

As duas têm o mesmo conteúdo, célula por célula. A única diferença é a quebra de linha
(uma usa o padrão do Windows, a outra o do Linux). Usamos a segunda.

Os números também batem com o que a base original descreve: 110.527 consultas, 14 colunas,
22.319 faltas, 81 bairros e idades de −1 a 115.

Quem tiver conta no Kaggle pode baixar o arquivo oficial e substituir este. O código do
projeto funciona do mesmo jeito.
