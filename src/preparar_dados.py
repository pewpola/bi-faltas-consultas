"""
Prepara a base de consultas para o painel.

Lê o arquivo original em dados/bruto/, passa pelas três etapas que o trabalho pede
(limpeza, transformação e redução) e grava o resultado em dados/tratado/.

Cada etapa anota quantas linhas tirou ou mudou. Essas anotações vão para
dados/tratado/registro_preprocessamento.json e servem de base para a seção 3 do relatório.

Para rodar:  python src/preparar_dados.py
"""

import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
ARQUIVO_BRUTO = RAIZ / "dados" / "bruto" / "KaggleV2-May-2016.csv"
PASTA_TRATADA = RAIZ / "dados" / "tratado"

# Limites que usamos nas regras. Ficam aqui em cima para ser fácil mudar e explicar.
IDADE_MAXIMA = 110          # acima disso, tratamos como erro de digitação
MINIMO_CONSULTAS_BAIRRO = 30  # abaixo disso, a taxa de faltas do bairro não é confiável

# Nomes que a base original trouxe com erro de grafia ou em inglês.
NOMES_COLUNAS = {
    "PatientId": "id_paciente",
    "AppointmentID": "id_consulta",
    "Gender": "sexo",
    "ScheduledDay": "data_agendamento",
    "AppointmentDay": "data_consulta",
    "Age": "idade",
    "Neighbourhood": "bairro",
    "Scholarship": "bolsa_familia",
    "Hipertension": "hipertensao",
    "Diabetes": "diabetes",
    "Alcoholism": "alcoolismo",
    "Handcap": "grau_deficiencia",
    "SMS_received": "recebeu_sms",
    "No-show": "no_show",
}

DIAS_DA_SEMANA = {
    0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 4: "Sexta", 5: "Sábado", 6: "Domingo",
}

# Faixas pensadas para a decisão do gestor: "mesmo dia" é encaixe, até 2 dias não recebe SMS,
# e a partir daí as faixas seguem semanas e meses de espera.
FAIXAS_ANTECEDENCIA = [
    (0, 0, "Mesmo dia"),
    (1, 2, "1 a 2 dias"),
    (3, 7, "3 a 7 dias"),
    (8, 15, "8 a 15 dias"),
    (16, 30, "16 a 30 dias"),
    (31, 60, "31 a 60 dias"),
    (61, 10_000, "Mais de 60 dias"),
]

FAIXAS_IDADE = [
    (0, 12, "0 a 12"),
    (13, 18, "13 a 18"),
    (19, 30, "19 a 30"),
    (31, 45, "31 a 45"),
    (46, 60, "46 a 60"),
    (61, 200, "61 ou mais"),
]


def faixa(valor, faixas):
    """Devolve o rótulo da faixa em que o valor cai."""
    for inicio, fim, rotulo in faixas:
        if inicio <= valor <= fim:
            return rotulo
    return None


def nome_bonito(bairro):
    """JARDIM DA PENHA -> Jardim da Penha (preposições ficam em minúsculas)."""
    minusculas = {"da", "de", "do", "das", "dos", "e"}
    palavras = bairro.title().split()
    return " ".join(p.lower() if p.lower() in minusculas and i > 0 else p for i, p in enumerate(palavras))


def preparar():
    registro = {"limpeza": [], "transformacao": [], "reducao": []}

    def anotar(etapa, acao, linhas_antes, linhas_depois, detalhe=""):
        registro[etapa].append({
            "acao": acao,
            "linhas_antes": int(linhas_antes),
            "linhas_depois": int(linhas_depois),
            "linhas_afetadas": int(linhas_antes - linhas_depois),
            "detalhe": detalhe,
        })

    df = pd.read_csv(ARQUIVO_BRUTO)
    registro["linhas_originais"] = len(df)
    registro["colunas_originais"] = list(df.columns)

    # ------------------------------------------------------------------ LIMPEZA
    df = df.rename(columns=NOMES_COLUNAS)

    nulos = int(df.isna().sum().sum())
    anotar("limpeza", "Procura de valores nulos", len(df), len(df),
           f"{nulos} valores nulos encontrados. Nada a preencher ou remover.")

    # Duplicatas: o mesmo agendamento gravado duas vezes no mesmo segundo, só com IDs diferentes.
    # Por isso comparamos todas as colunas menos o id da consulta.
    antes = len(df)
    df = df.drop_duplicates(subset=[c for c in df.columns if c != "id_consulta"], keep="first")
    anotar("limpeza", "Remoção de agendamentos duplicados", antes, len(df),
           "Mesmo paciente, mesmos horários e mesmos dados, mudando só o id da consulta "
           "(registro feito duas vezes no mesmo segundo).")

    antes = len(df)
    df = df[df["idade"] >= 0]
    anotar("limpeza", "Remoção de idade negativa", antes, len(df), "Idade -1 não existe.")

    antes = len(df)
    df = df[df["idade"] <= IDADE_MAXIMA]
    anotar("limpeza", f"Remoção de idade acima de {IDADE_MAXIMA} anos", antes, len(df),
           "Registros com 115 anos, tratados como erro de digitação.")

    # ------------------------------------------------------------ TRANSFORMAÇÃO
    # As datas vêm em texto no formato ISO com "Z" no fim. A consulta não tem hora (sempre 00:00).
    df["data_agendamento"] = pd.to_datetime(df["data_agendamento"]).dt.tz_localize(None)
    df["data_consulta"] = pd.to_datetime(df["data_consulta"]).dt.tz_localize(None).dt.normalize()
    anotar("transformacao", "Datas de texto convertidas para data", len(df), len(df),
           "Agendamento mantém data e hora; consulta fica só com a data, porque a base não traz o horário.")

    df["antecedencia_dias"] = (df["data_consulta"] - df["data_agendamento"].dt.normalize()).dt.days

    # Consulta marcada para antes do próprio agendamento: erro de registro, sai da base.
    antes = len(df)
    df = df[df["antecedencia_dias"] >= 0]
    anotar("limpeza", "Remoção de consultas anteriores ao agendamento", antes, len(df),
           "Antecedência negativa é impossível.")

    df["faltou"] = (df["no_show"] == "Yes").astype(int)
    df["situacao"] = df["faltou"].map({1: "Faltou", 0: "Compareceu"})
    df = df.drop(columns="no_show")
    anotar("transformacao", "Coluna No-show traduzida", len(df), len(df),
           "Na origem, 'Yes' quer dizer que o paciente FALTOU. Viraram 'faltou' (1/0) e 'situacao' "
           "(Faltou/Compareceu) para não haver dúvida.")

    # Cinco códigos de paciente vieram com casas decimais, o que não faz sentido para um código.
    # Cortar a parte decimal não junta pacientes diferentes, então guardamos o código como texto inteiro.
    com_decimal = int((df["id_paciente"] % 1 != 0).sum())
    distintos_antes = df["id_paciente"].nunique()
    df["id_paciente"] = df["id_paciente"].astype("int64").astype(str)
    anotar("transformacao", "Código do paciente corrigido", len(df), len(df),
           f"{com_decimal} códigos tinham casas decimais. Sem a parte decimal, o número de pacientes "
           f"distintos continua {distintos_antes} ({df['id_paciente'].nunique()} depois), então nenhum paciente foi misturado.")
    df["sexo"] = df["sexo"].map({"F": "Feminino", "M": "Masculino"})
    df["bairro"] = df["bairro"].str.strip().map(nome_bonito)
    for coluna in ["bolsa_familia", "hipertensao", "diabetes", "alcoolismo", "recebeu_sms"]:
        df[coluna] = df[coluna].map({1: "Sim", 0: "Não"})
    df["deficiencia"] = df["grau_deficiencia"].gt(0).map({True: "Sim", False: "Não"})
    anotar("transformacao", "Padronização de códigos e textos", len(df), len(df),
           "Sexo F/M por extenso, 0/1 virou Não/Sim, bairros com grafia de título e "
           "grau de deficiência (0 a 4) resumido em Sim/Não, mantendo o grau original.")

    df["dia_semana"] = df["data_consulta"].dt.day_of_week.map(DIAS_DA_SEMANA)
    df["hora_agendamento"] = df["data_agendamento"].dt.hour
    df["faixa_antecedencia"] = df["antecedencia_dias"].map(lambda d: faixa(d, FAIXAS_ANTECEDENCIA))
    df["faixa_etaria"] = df["idade"].map(lambda i: faixa(i, FAIXAS_IDADE))
    df["sms_possivel"] = df["antecedencia_dias"].ge(3).map({True: "Sim", False: "Não"})

    # Histórico do paciente dentro da própria base: quantas vezes ele já tinha faltado
    # em consultas anteriores. Ordenamos por data para contar só o passado.
    df = df.sort_values(["id_paciente", "data_consulta", "data_agendamento", "id_consulta"])
    faltas_acumuladas = df.groupby("id_paciente")["faltou"].cumsum()
    df["faltas_anteriores"] = (faltas_acumuladas - df["faltou"]).astype(int)
    df["ja_faltou_antes"] = df["faltas_anteriores"].gt(0).map({True: "Sim", False: "Não"})
    anotar("transformacao", "Novas colunas criadas", len(df), len(df),
           "antecedencia_dias, faixa_antecedencia, dia_semana, hora_agendamento, faixa_etaria, "
           "sms_possivel (consulta marcada com 3 dias ou mais), faltas_anteriores e ja_faltou_antes.")

    # ------------------------------------------------------------------ REDUÇÃO
    antes = len(df)
    df = df[df["dia_semana"] != "Sábado"]
    anotar("reducao", "Retirada do sábado isolado", antes, len(df),
           "Só um sábado (14/05/2016) teve consultas, e foram poucas. Fora do padrão de "
           "segunda a sexta, ele distorceria a comparação por dia da semana.")

    contagem = df["bairro"].value_counts()
    pequenos = contagem[contagem < MINIMO_CONSULTAS_BAIRRO]
    antes = len(df)
    df = df[~df["bairro"].isin(pequenos.index)]
    anotar("reducao", f"Retirada de bairros com menos de {MINIMO_CONSULTAS_BAIRRO} consultas", antes, len(df),
           "Volume pequeno demais para uma taxa de faltas confiável: " + ", ".join(sorted(pequenos.index)) + ".")

    colunas_finais = [
        "id_consulta", "id_paciente", "situacao", "faltou", "data_agendamento", "hora_agendamento",
        "data_consulta", "dia_semana", "antecedencia_dias", "faixa_antecedencia", "sms_possivel",
        "recebeu_sms", "sexo", "idade", "faixa_etaria", "bairro", "bolsa_familia", "hipertensao",
        "diabetes", "alcoolismo", "deficiencia", "grau_deficiencia", "faltas_anteriores", "ja_faltou_antes",
    ]
    df = df[colunas_finais].sort_values(["data_consulta", "id_consulta"]).reset_index(drop=True)
    anotar("reducao", "Colunas finais selecionadas", len(df), len(df),
           f"{len(colunas_finais)} colunas: as 14 originais tratadas e as novas colunas de análise.")

    registro["linhas_finais"] = len(df)
    registro["periodo"] = [str(df["data_consulta"].min().date()), str(df["data_consulta"].max().date())]
    registro["taxa_faltas_final"] = round(float(df["faltou"].mean()) * 100, 2)

    PASTA_TRATADA.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PASTA_TRATADA / "consultas_tratadas.parquet", index=False)
    with open(PASTA_TRATADA / "registro_preprocessamento.json", "w", encoding="utf-8") as f:
        json.dump(registro, f, ensure_ascii=False, indent=2)
    return df, registro


if __name__ == "__main__":
    tabela, registro = preparar()
    print(f"Linhas na base original: {registro['linhas_originais']:,}".replace(",", "."))
    for etapa in ["limpeza", "transformacao", "reducao"]:
        print(f"\n{etapa.upper()}")
        for passo in registro[etapa]:
            if etapa == "transformacao":
                print(f"  - {passo['acao']}")
            else:
                print(f"  - {passo['acao']}: {passo['linhas_afetadas']} linha(s) retirada(s)")
    print(f"\nLinhas na base tratada: {registro['linhas_finais']:,}".replace(",", "."))
    print(f"Taxa de faltas: {registro['taxa_faltas_final']}%")
