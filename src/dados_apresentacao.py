"""
Junta num arquivo só (apresentacao/dados.json) todos os números usados no relatório e nos slides.

Assim, relatório, slides e painel saem da mesma base tratada e nunca ficam com números diferentes.

Para rodar (depois de preparar_dados.py):  python src/dados_apresentacao.py
"""

import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
TRATADO = RAIZ / "dados" / "tratado" / "consultas_tratadas.parquet"
REGISTRO = RAIZ / "dados" / "tratado" / "registro_preprocessamento.json"
SAIDA = RAIZ / "apresentacao" / "dados.json"

ORDEM_ANTECEDENCIA = ["Mesmo dia", "1 a 2 dias", "3 a 7 dias", "8 a 15 dias", "16 a 30 dias",
                      "31 a 60 dias", "Mais de 60 dias"]
ORDEM_IDADE = ["0 a 12", "13 a 18", "19 a 30", "31 a 45", "46 a 60", "61 ou mais"]
ORDEM_DIAS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]


def taxa_por(df, coluna, ordem=None):
    """Consultas e taxa de faltas (em %) de cada valor da coluna."""
    t = df.groupby(coluna, observed=True)["faltou"].agg(consultas="size", taxa="mean").reset_index()
    t["taxa"] = (t["taxa"] * 100).round(1)
    if ordem:
        t = t.set_index(coluna).reindex(ordem).reset_index()
    return t.rename(columns={coluna: "grupo"}).to_dict("records")


def gerar():
    d = pd.read_parquet(TRATADO)
    registro = json.loads(REGISTRO.read_text(encoding="utf-8"))

    # SMS: só faz sentido comparar entre as consultas que podiam receber SMS (3 dias ou mais),
    # e sempre dentro da mesma faixa de antecedência.
    eleg = d[d["sms_possivel"] == "Sim"]
    sem_sms = eleg[eleg["recebeu_sms"] == "Não"]
    taxas = eleg.groupby(["faixa_antecedencia", "recebeu_sms"], observed=True)["faltou"].mean().unstack()
    volumes = eleg.groupby(["faixa_antecedencia", "recebeu_sms"], observed=True).size().unstack()
    evitaveis = 0.0
    for faixa, n in sem_sms.groupby("faixa_antecedencia", observed=True).size().items():
        ganho = taxas.loc[faixa, "Não"] - taxas.loc[faixa, "Sim"]
        if ganho > 0:
            evitaveis += ganho * n
    sms_faixas = [
        {"faixa": f, "sem": round(taxas.loc[f, "Não"] * 100, 1), "com": round(taxas.loc[f, "Sim"] * 100, 1),
         "n_sem": int(volumes.loc[f, "Não"]), "n_com": int(volumes.loc[f, "Sim"])}
        for f in ORDEM_ANTECEDENCIA if f in taxas.index
    ]

    bairros = pd.DataFrame(taxa_por(d, "bairro"))
    bairros_300 = bairros[bairros["consultas"] >= 300].sort_values("taxa", ascending=False)

    diario = d.groupby(d["data_consulta"].dt.strftime("%d/%m"))["faltou"].agg(["mean", "size"])
    hist = d.groupby("ja_faltou_antes")["faltou"].mean()

    # Exemplo de filtro combinado usado no relatório e no roteiro da demonstração:
    # consultas marcadas com 8 a 15 dias de antecedência no bairro Itararé.
    combo = d[(d["faixa_antecedencia"] == "8 a 15 dias") & (d["bairro"] == "Itararé")]
    faixa_8_15 = d[d["faixa_antecedencia"] == "8 a 15 dias"]

    def cobertura_sms(parte):
        """% das consultas que podiam receber SMS (3 dias ou mais) e receberam."""
        e = parte[parte["sms_possivel"] == "Sim"]
        return round((e["recebeu_sms"] == "Sim").mean() * 100, 1)

    combo_sms = combo.groupby("recebeu_sms")["faltou"].mean()
    ganhos = [f["sem"] - f["com"] for f in sms_faixas]

    dados = {
        "linhas_originais": registro["linhas_originais"],
        "linhas_finais": len(d),
        "colunas_finais": d.shape[1],
        "periodo": registro["periodo"],
        "faltas": int(d["faltou"].sum()),
        "taxa_geral": round(d["faltou"].mean() * 100, 1),
        "pacientes": int(d["id_paciente"].nunique()),
        "bairros": int(d["bairro"].nunique()),
        "dias_com_consulta": int(d["data_consulta"].nunique()),
        "registro": registro,
        "antecedencia": taxa_por(d, "faixa_antecedencia", ORDEM_ANTECEDENCIA),
        "mesmo_dia": round(d[d["antecedencia_dias"] == 0]["faltou"].mean() * 100, 1),
        "oito_ou_mais": round(d[d["antecedencia_dias"] >= 8]["faltou"].mean() * 100, 1),
        "sms_geral": {"com": round(d[d["recebeu_sms"] == "Sim"]["faltou"].mean() * 100, 1),
                      "sem": round(d[d["recebeu_sms"] == "Não"]["faltou"].mean() * 100, 1)},
        "sms_mesmo_dia_ou_2": int(d[(d["sms_possivel"] == "Não") & (d["recebeu_sms"] == "Sim")].shape[0]),
        "sms_faixas": sms_faixas,
        "elegiveis": len(eleg),
        "elegiveis_sem_sms": len(sem_sms),
        "elegiveis_sem_sms_pct": round(len(sem_sms) / len(eleg) * 100, 1),
        "faltas_evitaveis": int(round(evitaveis)),
        "historico": {"sim": round(hist["Sim"] * 100, 1), "nao": round(hist["Não"] * 100, 1),
                      "pacientes_sim": int(d[d["ja_faltou_antes"] == "Sim"]["id_paciente"].nunique())},
        "bairros_top": bairros_300.head(10).to_dict("records"),
        "bairros_com_300": len(bairros_300),
        "idade": taxa_por(d, "faixa_etaria", ORDEM_IDADE),
        "dia_semana": taxa_por(d, "dia_semana", ORDEM_DIAS),
        "bolsa": taxa_por(d, "bolsa_familia"),
        "sexo": taxa_por(d, "sexo"),
        "diario_min": [diario["mean"].idxmin(), round(diario["mean"].min() * 100, 1)],
        "diario_max": [diario["mean"].idxmax(), round(diario["mean"].max() * 100, 1)],
        "combo_exemplo": {"consultas": len(combo), "taxa": round(combo["faltou"].mean() * 100, 1),
                          "faltas": int(combo["faltou"].sum()), "pacientes": int(combo["id_paciente"].nunique()),
                          "cobertura_sms": cobertura_sms(combo),
                          "sms_com": round(combo_sms["Sim"] * 100, 1), "sms_sem": round(combo_sms["Não"] * 100, 1)},
        "cobertura_sms": cobertura_sms(d),
        "sms_ganho_min": round(min(ganhos), 1),
        "sms_ganho_max": round(max(ganhos), 1),
        "consultas_8_ou_mais": int((d["antecedencia_dias"] >= 8).sum()),
        "faltas_por_dia": round(d["faltou"].sum() / d["data_consulta"].nunique()),
        "evitaveis_por_dia": round(evitaveis / d["data_consulta"].nunique()),
        "faixa_8_15": {"consultas": len(faixa_8_15), "taxa": round(faixa_8_15["faltou"].mean() * 100, 1)},
    }

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(dados, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(f"Números gravados em {SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    gerar()
