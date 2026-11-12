"""
Gera docs/metadados.md, o dicionário de dados do projeto (seção 2 do relatório).

O significado de cada coluna está escrito aqui à mão. Já os números (tipo, quantidade de
valores distintos, exemplos) são calculados na hora a partir das bases, para o documento
nunca ficar desatualizado.

Para rodar (depois de preparar_dados.py):  python src/gerar_metadados.py
"""

import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
BRUTO = RAIZ / "dados" / "bruto" / "KaggleV2-May-2016.csv"
TRATADO = RAIZ / "dados" / "tratado" / "consultas_tratadas.parquet"
REGISTRO = RAIZ / "dados" / "tratado" / "registro_preprocessamento.json"
SAIDA = RAIZ / "docs" / "metadados.md"

SIGNIFICADO_ORIGINAL = {
    "PatientId": "Código do paciente. O mesmo paciente pode ter várias consultas.",
    "AppointmentID": "Código da consulta. Um por linha.",
    "Gender": "Sexo do paciente (F ou M).",
    "ScheduledDay": "Dia e hora em que a consulta foi marcada.",
    "AppointmentDay": "Dia da consulta. Vem sempre com hora 00:00, ou seja, sem horário.",
    "Age": "Idade do paciente em anos.",
    "Neighbourhood": "Bairro de Vitória (ES) onde fica a unidade de saúde.",
    "Scholarship": "Se a família recebe Bolsa Família (1) ou não (0).",
    "Hipertension": "Se o paciente tem hipertensão (1) ou não (0). Nome original com erro de grafia.",
    "Diabetes": "Se o paciente tem diabetes (1) ou não (0).",
    "Alcoholism": "Se o paciente tem alcoolismo (1) ou não (0).",
    "Handcap": "Grau de deficiência, de 0 (nenhuma) a 4. Nome original com erro de grafia.",
    "SMS_received": "Se o paciente recebeu SMS de lembrete (1) ou não (0).",
    "No-show": "Se o paciente faltou. Atenção: 'Yes' significa que FALTOU.",
}

SIGNIFICADO_TRATADO = {
    "id_consulta": "Código da consulta (AppointmentID).",
    "id_paciente": "Código do paciente (PatientId), guardado como texto.",
    "situacao": "Faltou ou Compareceu. Tradução da coluna No-show.",
    "faltou": "1 se faltou, 0 se compareceu. A média dessa coluna é a taxa de faltas.",
    "data_agendamento": "Data e hora em que a consulta foi marcada.",
    "hora_agendamento": "Hora do dia em que a consulta foi marcada (0 a 23). Coluna nova.",
    "data_consulta": "Data da consulta.",
    "dia_semana": "Dia da semana da consulta, em português. Coluna nova.",
    "antecedencia_dias": "Dias entre marcar e ir à consulta. 0 é encaixe no mesmo dia. Coluna nova.",
    "faixa_antecedencia": "Antecedência agrupada em faixas (mesmo dia, 1 a 2 dias, 3 a 7 dias...). Coluna nova.",
    "sms_possivel": "Sim quando a consulta foi marcada com 3 dias ou mais, o único caso em que a base mostra SMS enviado. Coluna nova.",
    "recebeu_sms": "Se o paciente recebeu SMS de lembrete (Sim ou Não).",
    "sexo": "Feminino ou Masculino.",
    "idade": "Idade em anos (0 a 110 depois da limpeza).",
    "faixa_etaria": "Idade agrupada em faixas. Coluna nova.",
    "bairro": "Bairro da unidade de saúde, com grafia padronizada.",
    "bolsa_familia": "Se a família recebe Bolsa Família (Sim ou Não).",
    "hipertensao": "Se tem hipertensão (Sim ou Não).",
    "diabetes": "Se tem diabetes (Sim ou Não).",
    "alcoolismo": "Se tem alcoolismo (Sim ou Não).",
    "deficiencia": "Se tem alguma deficiência (Sim quando o grau é maior que 0). Coluna nova.",
    "grau_deficiencia": "Grau de deficiência original, de 0 a 4.",
    "faltas_anteriores": "Quantas vezes o paciente já tinha faltado antes desta consulta, dentro da base. Coluna nova.",
    "ja_faltou_antes": "Sim se faltas_anteriores for maior que 0. Coluna nova.",
}

NOVAS = {"hora_agendamento", "dia_semana", "antecedencia_dias", "faixa_antecedencia", "sms_possivel",
         "faixa_etaria", "deficiencia", "faltas_anteriores", "ja_faltou_antes"}


def milhar(numero):
    """1234567 -> 1.234.567 (separador de milhar do português)."""
    return f"{numero:,}".replace(",", ".")


def resumo(serie):
    """Tipo, quantidade de valores distintos e alguns exemplos de uma coluna."""
    distintos = serie.nunique()
    if pd.api.types.is_numeric_dtype(serie) and distintos > 10:
        exemplo = f"de {serie.min():g} a {serie.max():g}" if pd.api.types.is_float_dtype(serie) else f"de {serie.min()} a {serie.max()}"
    elif pd.api.types.is_datetime64_any_dtype(serie):
        exemplo = f"de {serie.min():%d/%m/%Y} a {serie.max():%d/%m/%Y}"
    else:
        valores = serie.value_counts().index[:4].astype(str).tolist()
        exemplo = ", ".join(valores) + (" ..." if distintos > 4 else "")
    tipo = str(serie.dtype).replace("datetime64[us]", "data").replace("int64", "inteiro") \
        .replace("int32", "inteiro").replace("float64", "decimal").replace("str", "texto")
    return tipo, distintos, exemplo


def gerar():
    bruto = pd.read_csv(BRUTO)
    tratado = pd.read_parquet(TRATADO)
    registro = json.loads(REGISTRO.read_text(encoding="utf-8"))

    linhas = [
        "# Dicionário de dados",
        "",
        "Gerado por `src/gerar_metadados.py`. Não edite à mão: rode o script de novo se a base mudar.",
        "",
        "## Base original",
        "",
        f"Um arquivo CSV (`KaggleV2-May-2016.csv`) com **{milhar(len(bruto))} linhas** e **{bruto.shape[1]} colunas**. "
        "Cada linha é uma consulta marcada em unidades públicas de saúde de Vitória (ES).",
        "",
        "| Coluna original | Tipo | Valores distintos | Exemplos | O que significa |",
        "|---|---|---|---|---|",
    ]
    for coluna in bruto.columns:
        tipo, distintos, exemplo = resumo(bruto[coluna])
        linhas.append(f"| `{coluna}` | {tipo} | {milhar(distintos)} | {exemplo} | {SIGNIFICADO_ORIGINAL[coluna]} |")

    linhas += [
        "",
        "## Base tratada (usada no painel)",
        "",
        f"Arquivo `dados/tratado/consultas_tratadas.parquet`, com **{milhar(len(tratado))} linhas** e "
        f"**{tratado.shape[1]} colunas**, de {registro['periodo'][0]} a {registro['periodo'][1]}. "
        "As colunas marcadas com ★ foram criadas por nós.",
        "",
        "| Coluna | Tipo | Valores distintos | Exemplos | O que significa |",
        "|---|---|---|---|---|",
    ]
    for coluna in tratado.columns:
        tipo, distintos, exemplo = resumo(tratado[coluna])
        marca = " ★" if coluna in NOVAS else ""
        linhas.append(f"| `{coluna}`{marca} | {tipo} | {milhar(distintos)} | {exemplo} | {SIGNIFICADO_TRATADO[coluna]} |")

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"Dicionário gravado em {SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    gerar()
