# Dicionário de dados

Gerado por `src/gerar_metadados.py`. Não edite à mão: rode o script de novo se a base mudar.

## Base original

Um arquivo CSV (`KaggleV2-May-2016.csv`) com **110.527 linhas** e **14 colunas**. Cada linha é uma consulta marcada em unidades públicas de saúde de Vitória (ES).

| Coluna original | Tipo | Valores distintos | Exemplos | O que significa |
|---|---|---|---|---|
| `PatientId` | decimal | 62.299 | de 39217.8 a 9.99982e+14 | Código do paciente. O mesmo paciente pode ter várias consultas. |
| `AppointmentID` | inteiro | 110.527 | de 5030230 a 5790484 | Código da consulta. Um por linha. |
| `Gender` | texto | 2 | F, M | Sexo do paciente (F ou M). |
| `ScheduledDay` | texto | 103.549 | 2016-05-06T07:09:54Z, 2016-05-06T07:09:53Z, 2016-04-25T17:18:27Z, 2016-04-25T17:17:46Z ... | Dia e hora em que a consulta foi marcada. |
| `AppointmentDay` | texto | 27 | 2016-06-06T00:00:00Z, 2016-05-16T00:00:00Z, 2016-05-09T00:00:00Z, 2016-05-30T00:00:00Z ... | Dia da consulta. Vem sempre com hora 00:00, ou seja, sem horário. |
| `Age` | inteiro | 104 | de -1 a 115 | Idade do paciente em anos. |
| `Neighbourhood` | texto | 81 | JARDIM CAMBURI, MARIA ORTIZ, RESISTÊNCIA, JARDIM DA PENHA ... | Bairro de Vitória (ES) onde fica a unidade de saúde. |
| `Scholarship` | inteiro | 2 | 0, 1 | Se a família recebe Bolsa Família (1) ou não (0). |
| `Hipertension` | inteiro | 2 | 0, 1 | Se o paciente tem hipertensão (1) ou não (0). Nome original com erro de grafia. |
| `Diabetes` | inteiro | 2 | 0, 1 | Se o paciente tem diabetes (1) ou não (0). |
| `Alcoholism` | inteiro | 2 | 0, 1 | Se o paciente tem alcoolismo (1) ou não (0). |
| `Handcap` | inteiro | 5 | 0, 1, 2, 3 ... | Grau de deficiência, de 0 (nenhuma) a 4. Nome original com erro de grafia. |
| `SMS_received` | inteiro | 2 | 0, 1 | Se o paciente recebeu SMS de lembrete (1) ou não (0). |
| `No-show` | texto | 2 | No, Yes | Se o paciente faltou. Atenção: 'Yes' significa que FALTOU. |

## Base tratada (usada no painel)

Arquivo `dados/tratado/consultas_tratadas.parquet`, com **109.839 linhas** e **24 colunas**, de 2016-04-29 a 2016-06-08. As colunas marcadas com ★ foram criadas por nós.

| Coluna | Tipo | Valores distintos | Exemplos | O que significa |
|---|---|---|---|---|
| `id_consulta` | inteiro | 109.839 | de 5030230 a 5790484 | Código da consulta (AppointmentID). |
| `id_paciente` | texto | 62.260 | 822145925426128, 99637671331, 26886125921145, 33534783483176 ... | Código do paciente (PatientId), guardado como texto. |
| `situacao` | texto | 2 | Compareceu, Faltou | Faltou ou Compareceu. Tradução da coluna No-show. |
| `faltou` | inteiro | 2 | 0, 1 | 1 se faltou, 0 se compareceu. A média dessa coluna é a taxa de faltas. |
| `data_agendamento` | data | 103.484 | de 10/11/2015 a 08/06/2016 | Data e hora em que a consulta foi marcada. |
| `hora_agendamento` ★ | inteiro | 16 | de 6 a 21 | Hora do dia em que a consulta foi marcada (0 a 23). Coluna nova. |
| `data_consulta` | data | 26 | de 29/04/2016 a 08/06/2016 | Data da consulta. |
| `dia_semana` ★ | texto | 5 | Quarta, Terça, Segunda, Sexta ... | Dia da semana da consulta, em português. Coluna nova. |
| `antecedencia_dias` ★ | inteiro | 129 | de 0 a 179 | Dias entre marcar e ir à consulta. 0 é encaixe no mesmo dia. Coluna nova. |
| `faixa_antecedencia` ★ | texto | 7 | Mesmo dia, 3 a 7 dias, 16 a 30 dias, 8 a 15 dias ... | Antecedência agrupada em faixas (mesmo dia, 1 a 2 dias, 3 a 7 dias...). Coluna nova. |
| `sms_possivel` ★ | texto | 2 | Sim, Não | Sim quando a consulta foi marcada com 3 dias ou mais, o único caso em que a base mostra SMS enviado. Coluna nova. |
| `recebeu_sms` | texto | 2 | Não, Sim | Se o paciente recebeu SMS de lembrete (Sim ou Não). |
| `sexo` | texto | 2 | Feminino, Masculino | Feminino ou Masculino. |
| `idade` | inteiro | 102 | de 0 a 102 | Idade em anos (0 a 110 depois da limpeza). |
| `faixa_etaria` ★ | texto | 6 | 46 a 60, 31 a 45, 0 a 12, 61 ou mais ... | Idade agrupada em faixas. Coluna nova. |
| `bairro` | texto | 77 | Jardim Camburi, Maria Ortiz, Resistência, Jardim da Penha ... | Bairro da unidade de saúde, com grafia padronizada. |
| `bolsa_familia` | texto | 2 | Não, Sim | Se a família recebe Bolsa Família (Sim ou Não). |
| `hipertensao` | texto | 2 | Não, Sim | Se tem hipertensão (Sim ou Não). |
| `diabetes` | texto | 2 | Não, Sim | Se tem diabetes (Sim ou Não). |
| `alcoolismo` | texto | 2 | Não, Sim | Se tem alcoolismo (Sim ou Não). |
| `deficiencia` ★ | texto | 2 | Não, Sim | Se tem alguma deficiência (Sim quando o grau é maior que 0). Coluna nova. |
| `grau_deficiencia` | inteiro | 5 | 0, 1, 2, 3 ... | Grau de deficiência original, de 0 a 4. |
| `faltas_anteriores` ★ | inteiro | 18 | de 0 a 17 | Quantas vezes o paciente já tinha faltado antes desta consulta, dentro da base. Coluna nova. |
| `ja_faltou_antes` ★ | texto | 2 | Não, Sim | Sim se faltas_anteriores for maior que 0. Coluna nova. |
