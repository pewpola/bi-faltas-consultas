"""
Painel de BI: faltas em consultas nas unidades de saúde de Vitória (ES).

Para abrir:  streamlit run app.py

Como a interatividade funciona:
- Os filtros da barra lateral valem para o painel inteiro.
- Clicar numa barra ou num ponto também filtra: o item clicado passa a filtrar todos os
  OUTROS gráficos (filtro cruzado). Dá para clicar em vários gráficos e combinar tudo.
- O botão "Limpar seleções" desfaz os cliques. Os filtros laterais têm o seu.
"""

import json
from functools import partial
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

RAIZ = Path(__file__).resolve().parent
BASE = RAIZ / "dados" / "tratado" / "consultas_tratadas.parquet"
REGISTRO = RAIZ / "dados" / "tratado" / "registro_preprocessamento.json"

# Paleta: coral chama atenção para a falta, verde-petróleo representa o comparecimento.
CORAL = "#E4572E"
CORAL_ESCURO = "#A63A1F"
CORAL_APAGADO = "#F6C9BD"
VERDE = "#0E7C7B"
VERDE_CLARO = "#9FD3CF"
CINZA = "#94A3B8"
TEXTO = "#1F2937"

ORDEM_ANTECEDENCIA = ["Mesmo dia", "1 a 2 dias", "3 a 7 dias", "8 a 15 dias",
                      "16 a 30 dias", "31 a 60 dias", "Mais de 60 dias"]
ORDEM_DIAS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
ORDEM_IDADE = ["0 a 12", "13 a 18", "19 a 30", "31 a 45", "46 a 60", "61 ou mais"]

# Cada gráfico clicável tem uma chave. Quando o usuário clica, guardamos o clique em
# st.session_state["cliques"]. Não dá para ler direto do gráfico porque o Streamlit
# zera a seleção quando o gráfico é redesenhado com a barra destacada.
GRAFICOS_CLICAVEIS = ["g_antecedencia", "g_sms", "g_dia", "g_data", "g_bairro", "g_idade", "g_perfil"]

st.set_page_config(page_title="Faltas em consultas · Vitória (ES)", page_icon="🩺", layout="wide")

st.markdown(
    """
    <style>
      .block-container {padding-top: 1.6rem; padding-bottom: 2rem;}
      h1 {font-size: 2.0rem !important; margin-bottom: 0.2rem;}
      .subtitulo {color: #4B5563; font-size: 1.02rem; margin-bottom: 1.1rem;}
      .decisao {background: #F2F6F6; border-left: 4px solid #0E7C7B; padding: 0.45rem 0.8rem;
                border-radius: 4px; font-size: 0.93rem; color: #1F2937; margin-top: -0.4rem;}
      .chip {display: inline-block; background: #FDE7E1; color: #A63A1F; border-radius: 999px;
             padding: 0.15rem 0.7rem; margin: 0 0.35rem 0.35rem 0; font-size: 0.88rem;}
      div[data-testid="stMetricValue"] {font-size: 1.9rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------- dados

@st.cache_data
def carregar():
    df = pd.read_parquet(BASE)
    df["data_txt"] = df["data_consulta"].dt.strftime("%Y-%m-%d")
    registro = json.loads(REGISTRO.read_text(encoding="utf-8"))
    return df, registro


def pct(valor, casas=1):
    """0.2011 -> '20,1%'"""
    return f"{valor * 100:.{casas}f}%".replace(".", ",")


def num(valor):
    """109839 -> '109.839'"""
    return f"{int(valor):,}".replace(",", ".")


def taxa_por(df, coluna, ordem=None):
    """Taxa de faltas e volume de consultas por categoria de uma coluna."""
    tabela = df.groupby(coluna, observed=True)["faltou"].agg(taxa="mean", consultas="size", faltas="sum")
    if ordem:
        tabela = tabela.reindex([o for o in ordem if o in tabela.index])
    return tabela.reset_index()


# --------------------------------------------------------------- filtro cruzado

def guardar_clique(chave):
    """Chamada pelo Streamlit quando o usuário clica num gráfico. Cada ponto traz no customdata
    pares [coluna, valor, ...], que viram um filtro {coluna: {valores}}."""
    filtros = {}
    try:
        pontos = st.session_state[chave]["selection"]["points"]
    except (KeyError, TypeError):
        pontos = []
    for ponto in pontos:
        dados = ponto.get("customdata")
        if not dados:
            continue
        dados = list(dados) if isinstance(dados, (list, tuple)) else [dados]
        for coluna, valor in zip(dados[0::2], dados[1::2]):
            filtros.setdefault(coluna, set()).add(valor)
    st.session_state.setdefault("cliques", {})[chave] = filtros


def selecoes_do_grafico(chave):
    """Filtros {coluna: {valores}} que vieram dos cliques num gráfico."""
    return st.session_state.get("cliques", {}).get(chave, {})


def aplicar_cliques(df, menos=None):
    """Aplica os cliques de todos os gráficos, exceto o do próprio gráfico (`menos`).
    Assim o gráfico clicado continua mostrando as outras barras, com a escolhida em destaque."""
    for chave in GRAFICOS_CLICAVEIS:
        if chave == menos:
            continue
        for coluna, valores in selecoes_do_grafico(chave).items():
            df = df[df[coluna].isin(valores)]
    return df


def limpar_cliques():
    st.session_state["cliques"] = {}
    for chave in GRAFICOS_CLICAVEIS:
        st.session_state.pop(chave, None)


def limpar_filtros():
    for chave in list(st.session_state.keys()):
        if chave.startswith("f_"):
            del st.session_state[chave]
    limpar_cliques()


def cores_destaque(categorias, escolhidas, cor=CORAL):
    """Barra escolhida fica escura, as outras ficam apagadas. Sem escolha, tudo na cor normal."""
    if not escolhidas:
        return [cor] * len(categorias)
    return [CORAL_ESCURO if c in escolhidas else CORAL_APAGADO for c in categorias]


def layout_padrao(fig, altura=330, **extra):
    fig.update_layout(
        height=altura,
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(size=14, color=TEXTO),
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False,
        clickmode="event+select",
        dragmode=False,
        hoverlabel=dict(font_size=14),
        **extra,
    )
    fig.update_yaxes(gridcolor="#E5E7EB", zeroline=False)
    fig.update_xaxes(showgrid=False)
    return fig


def mostrar(fig, chave):
    st.plotly_chart(fig, key=chave, on_select=partial(guardar_clique, chave), selection_mode="points",
                    use_container_width=True, config={"displayModeBar": False})


def decisao(texto):
    st.markdown(f'<div class="decisao"><b>Decisão que este gráfico apoia:</b> {texto}</div>',
                unsafe_allow_html=True)


# ---------------------------------------------------------------------- painel

df_total, registro = carregar()
taxa_geral = df_total["faltou"].mean()

st.title("Por que os pacientes faltam às consultas?")
st.markdown(
    f'<div class="subtitulo">Unidades públicas de saúde de Vitória (ES) · consultas de 29/04 a '
    f'08/06/2016 · {num(len(df_total))} consultas depois do tratamento dos dados. Clique nas barras '
    f'para filtrar os outros gráficos.</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------- filtros da lateral
with st.sidebar:
    st.header("Filtros")
    data_min, data_max = df_total["data_consulta"].min().date(), df_total["data_consulta"].max().date()
    periodo = st.date_input("Período da consulta", value=(data_min, data_max),
                            min_value=data_min, max_value=data_max, format="DD/MM/YYYY", key="f_periodo")
    bairros = st.multiselect("Bairro da unidade", sorted(df_total["bairro"].unique()), key="f_bairro",
                             placeholder="Todos os bairros")
    faixas_ant = st.multiselect("Antecedência do agendamento", ORDEM_ANTECEDENCIA, key="f_antecedencia",
                                placeholder="Todas")
    faixas_idade = st.multiselect("Faixa etária", ORDEM_IDADE, key="f_idade", placeholder="Todas")
    sexo = st.multiselect("Sexo", ["Feminino", "Masculino"], key="f_sexo", placeholder="Todos")
    col_a, col_b = st.columns(2)
    sms = col_a.selectbox("Recebeu SMS", ["Todos", "Sim", "Não"], key="f_sms")
    bolsa = col_b.selectbox("Bolsa Família", ["Todos", "Sim", "Não"], key="f_bolsa")
    historico = st.selectbox("Já tinha faltado antes", ["Todos", "Sim", "Não"], key="f_historico")
    condicoes = st.multiselect("Tem a condição", ["Hipertensão", "Diabetes", "Alcoolismo", "Deficiência"],
                               key="f_condicoes", placeholder="Qualquer paciente")
    st.button("Limpar todos os filtros", on_click=limpar_filtros, use_container_width=True)
    st.caption("Os filtros se combinam entre si e com os cliques nos gráficos.")

df = df_total
if isinstance(periodo, (list, tuple)) and len(periodo) == 2:
    df = df[(df["data_consulta"].dt.date >= periodo[0]) & (df["data_consulta"].dt.date <= periodo[1])]
if bairros:
    df = df[df["bairro"].isin(bairros)]
if faixas_ant:
    df = df[df["faixa_antecedencia"].isin(faixas_ant)]
if faixas_idade:
    df = df[df["faixa_etaria"].isin(faixas_idade)]
if sexo:
    df = df[df["sexo"].isin(sexo)]
if sms != "Todos":
    df = df[df["recebeu_sms"] == sms]
if bolsa != "Todos":
    df = df[df["bolsa_familia"] == bolsa]
if historico != "Todos":
    df = df[df["ja_faltou_antes"] == historico]
for nome, coluna in [("Hipertensão", "hipertensao"), ("Diabetes", "diabetes"),
                     ("Alcoolismo", "alcoolismo"), ("Deficiência", "deficiencia")]:
    if nome in condicoes:
        df = df[df[coluna] == "Sim"]

df_lateral = df                      # só os filtros da lateral
df_sel = aplicar_cliques(df_lateral)  # lateral + todos os cliques

# Lista dos cliques ativos, para o usuário saber o que está filtrando o painel.
ativos = []
for chave in GRAFICOS_CLICAVEIS:
    for coluna, valores in selecoes_do_grafico(chave).items():
        nome = coluna.replace("_", " ").replace("data txt", "data")
        ativos.append(f"{nome}: {', '.join(sorted(map(str, valores)))}")
if ativos:
    c1, c2 = st.columns([4, 1])
    c1.markdown("**Seleções nos gráficos:** " + "".join(f'<span class="chip">{a}</span>' for a in ativos),
                unsafe_allow_html=True)
    c2.button("Limpar seleções", on_click=limpar_cliques, use_container_width=True)

if df_sel.empty:
    st.warning("Nenhuma consulta com essa combinação de filtros. Tente afrouxar algum filtro.")
    st.stop()

# ---------------------------------------------------------------------- KPIs
taxa_sel = df_sel["faltou"].mean()
elegiveis = df_sel[df_sel["sms_possivel"] == "Sim"]
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Consultas", num(len(df_sel)))
k2.metric("Faltas", num(df_sel["faltou"].sum()))
diferenca = (taxa_sel - taxa_geral) * 100
# Sem filtro (ou com diferença desprezível) não há o que comparar, então a seta não aparece.
k3.metric("Taxa de faltas", pct(taxa_sel),
          delta=(f"{diferenca:+.1f}".replace(".", ",") + " p.p. vs. geral") if abs(diferenca) >= 0.05 else None,
          delta_color="inverse")
k4.metric("Pacientes", num(df_sel["id_paciente"].nunique()))
k5.metric("Lembrete por SMS", pct((elegiveis["recebeu_sms"] == "Sim").mean()) if len(elegiveis) else "–",
          help="Entre as consultas marcadas com 3 dias ou mais, que são as que podem receber SMS.")

st.divider()

# ------------------------------------------------- linha 1: antecedência e SMS
esq, dir_ = st.columns(2)

with esq:
    st.subheader("Quanto mais longe a consulta, maior a falta")
    base = aplicar_cliques(df_lateral, menos="g_antecedencia")
    tabela = taxa_por(base, "faixa_antecedencia", ORDEM_ANTECEDENCIA)
    escolhidas = selecoes_do_grafico("g_antecedencia").get("faixa_antecedencia", set())
    fig = go.Bar(
        x=tabela["faixa_antecedencia"], y=tabela["taxa"],
        marker_color=cores_destaque(tabela["faixa_antecedencia"], escolhidas),
        text=[pct(t) for t in tabela["taxa"]], textposition="outside",
        customdata=[["faixa_antecedencia", f] for f in tabela["faixa_antecedencia"]],
        hovertemplate="%{x}<br>Taxa de faltas: %{text}<br>Consultas: %{meta}<extra></extra>",
        meta=[num(c) for c in tabela["consultas"]],
    )
    fig = layout_padrao(go.Figure(fig), yaxis=dict(tickformat=".0%", range=[0, max(tabela["taxa"].max() * 1.25, 0.05)]))
    mostrar(fig, "g_antecedencia")
    decisao("até quantos dias à frente vale agendar e a partir de quando a consulta precisa de confirmação.")

with dir_:
    st.subheader("Com a mesma espera, quem recebe SMS falta menos")
    base = aplicar_cliques(df_lateral, menos="g_sms")
    base = base[base["sms_possivel"] == "Sim"]
    tabela = base.groupby(["faixa_antecedencia", "recebeu_sms"], observed=True)["faltou"].agg(["mean", "size"]).reset_index()
    ordem = [f for f in ORDEM_ANTECEDENCIA if f in set(tabela["faixa_antecedencia"])]
    escolhidos = selecoes_do_grafico("g_sms")
    fig = go.Figure()
    for valor, nome, cor in [("Não", "Sem SMS", CINZA), ("Sim", "Com SMS", VERDE)]:
        parte = tabela[tabela["recebeu_sms"] == valor].set_index("faixa_antecedencia").reindex(ordem)
        apagar = escolhidos and valor not in escolhidos.get("recebeu_sms", {valor})
        fig.add_bar(
            x=ordem, y=parte["mean"], name=nome, marker_color=cor, opacity=0.35 if apagar else 1,
            text=[pct(v) if pd.notna(v) else "" for v in parte["mean"]], textposition="outside",
            customdata=[["faixa_antecedencia", f, "recebeu_sms", valor] for f in ordem],
            hovertemplate=f"%{{x}} · {nome}<br>Taxa de faltas: %{{text}}<extra></extra>",
        )
    fig = layout_padrao(fig, barmode="group", yaxis=dict(tickformat=".0%"),
                        legend=dict(orientation="h", y=1.08, x=0))
    fig.update_layout(showlegend=True)
    mostrar(fig, "g_sms")
    decisao("ampliar o lembrete por SMS para todas as consultas marcadas com 3 dias ou mais. "
            "Só essas recebem SMS na base, por isso a comparação é feita dentro da mesma faixa de espera.")

st.divider()

# ---------------------------------------------- linha 2: dia a dia e semana
esq, dir_ = st.columns([3, 2])

with esq:
    st.subheader("Taxa de faltas dia a dia")
    base = aplicar_cliques(df_lateral, menos="g_data")
    diario = base.groupby("data_txt")["faltou"].agg(taxa="mean", consultas="size").reset_index()
    diario["data"] = pd.to_datetime(diario["data_txt"])
    escolhidas = selecoes_do_grafico("g_data").get("data_txt", set())
    media = base["faltou"].mean()
    fig = go.Figure()
    fig.add_bar(x=diario["data"], y=diario["consultas"], yaxis="y2", marker_color="#E5E7EB",
                hovertemplate="%{x|%d/%m}<br>Consultas: %{y}<extra></extra>")
    fig.add_scatter(
        x=diario["data"], y=diario["taxa"], mode="lines+markers",
        line=dict(color=CORAL, width=3),
        marker=dict(size=[13 if d in escolhidas else 8 for d in diario["data_txt"]],
                    color=[CORAL_ESCURO if d in escolhidas else CORAL for d in diario["data_txt"]]),
        customdata=[["data_txt", d] for d in diario["data_txt"]],
        hovertemplate="%{x|%d/%m (%a)}<br>Taxa de faltas: %{y:.1%}<extra></extra>",
    )
    fig.add_hline(y=media, line_dash="dot", line_color=CINZA,
                  annotation_text=f"média {pct(media)}", annotation_position="bottom left")
    fig = layout_padrao(
        fig, altura=340,
        yaxis=dict(tickformat=".0%", title="Taxa de faltas", rangemode="tozero"),
        yaxis2=dict(overlaying="y", side="right", showgrid=False, title="Consultas", rangemode="tozero"),
        xaxis=dict(tickformat="%d/%m"),
    )
    mostrar(fig, "g_data")
    decisao("achar dias fora do padrão e investigar o que aconteceu neles. Clique num ponto para ver o perfil daquele dia.")

with dir_:
    st.subheader("Dia da semana da consulta")
    base = aplicar_cliques(df_lateral, menos="g_dia")
    tabela = taxa_por(base, "dia_semana", ORDEM_DIAS)
    escolhidas = selecoes_do_grafico("g_dia").get("dia_semana", set())
    fig = go.Figure(go.Bar(
        x=tabela["dia_semana"], y=tabela["taxa"],
        marker_color=cores_destaque(tabela["dia_semana"], escolhidas),
        text=[pct(t) for t in tabela["taxa"]], textposition="outside",
        customdata=[["dia_semana", d] for d in tabela["dia_semana"]],
        hovertemplate="%{x}<br>Taxa de faltas: %{text}<extra></extra>",
    ))
    fig = layout_padrao(fig, altura=340, yaxis=dict(tickformat=".0%", range=[0, max(tabela["taxa"].max() * 1.25, 0.05)]))
    mostrar(fig, "g_dia")
    decisao("em que dias reforçar a confirmação e onde caberia encaixe extra para compensar as faltas.")

st.divider()

# -------------------------------------------- linha 3: bairros e perfil do paciente
esq, dir_ = st.columns([3, 2])

with esq:
    st.subheader("Bairros com mais faltas")
    minimo = st.slider("Mostrar só bairros com pelo menos este número de consultas", 50, 2000, 500, 50,
                       key="f_minimo_bairro")
    base = aplicar_cliques(df_lateral, menos="g_bairro")
    tabela = taxa_por(base, "bairro")
    if not tabela.empty and (tabela["consultas"] < minimo).all():
        # Recorte pequeno (ex.: um bairro só): em vez de deixar o gráfico vazio, mostra o que existe.
        st.caption(f"Nenhum bairro chega a {num(minimo)} consultas neste recorte; mostrando todos.")
    else:
        tabela = tabela[tabela["consultas"] >= minimo]
    tabela = tabela.sort_values("taxa", ascending=False).head(15)
    if tabela.empty:
        st.info("Nenhum bairro com os filtros atuais.")
    else:
        tabela = tabela.iloc[::-1]
        escolhidos = selecoes_do_grafico("g_bairro").get("bairro", set())
        fig = go.Figure(go.Bar(
            y=tabela["bairro"], x=tabela["taxa"], orientation="h",
            marker_color=cores_destaque(tabela["bairro"], escolhidos),
            text=[f"{pct(t)}  ({num(c)})" for t, c in zip(tabela["taxa"], tabela["consultas"])],
            textposition="outside",
            customdata=[["bairro", b] for b in tabela["bairro"]],
            hovertemplate="%{y}<br>Taxa de faltas: %{x:.1%}<extra></extra>",
        ))
        # A linha pontilhada é a taxa geral; a explicação vai no eixo para não cobrir as barras.
        fig.add_vline(x=taxa_geral, line_dash="dot", line_color=CINZA)
        fig = layout_padrao(fig, altura=max(200, 28 * len(tabela) + 90),
                            xaxis=dict(tickformat=".0%", range=[0, tabela["taxa"].max() * 1.3],
                                       title=f"Taxa de faltas · linha pontilhada = taxa geral ({pct(taxa_geral)})"))
        mostrar(fig, "g_bairro")
    decisao("onde concentrar busca ativa e confirmação por telefone. Entre parênteses, o número de consultas do bairro.")

with dir_:
    st.subheader("Quem falta mais")
    base = aplicar_cliques(df_lateral, menos="g_perfil")
    fatores = [("Já faltou antes", "ja_faltou_antes"), ("Bolsa Família", "bolsa_familia"),
               ("Hipertensão", "hipertensao"), ("Diabetes", "diabetes"),
               ("Alcoolismo", "alcoolismo"), ("Deficiência", "deficiencia")]
    escolhidos = selecoes_do_grafico("g_perfil")
    fig = go.Figure()
    for valor, nome, cor in [("Não", "Não", CINZA), ("Sim", "Sim", CORAL)]:
        taxas, dados = [], []
        for rotulo, coluna in fatores:
            parte = base[base[coluna] == valor]
            taxas.append(parte["faltou"].mean() if len(parte) else None)
            dados.append([coluna, valor])
        apagar = bool(escolhidos) and not any(valor in v for v in escolhidos.values())
        fig.add_bar(
            y=[f[0] for f in fatores], x=taxas, orientation="h", name=nome, marker_color=cor,
            opacity=0.35 if apagar else 1,
            text=[pct(t) if t is not None else "" for t in taxas], textposition="outside",
            customdata=dados, hovertemplate="%{y} = " + nome + "<br>Taxa de faltas: %{text}<extra></extra>",
        )
    maior = max([t for t in fig.data[0].x + fig.data[1].x if t is not None] or [0.3])
    fig = layout_padrao(fig, altura=380, barmode="group", xaxis=dict(tickformat=".0%", range=[0, maior * 1.3]),
                        legend=dict(orientation="h", y=1.08, x=0, title_text=""))
    fig.update_layout(showlegend=True, yaxis=dict(autorange="reversed"))
    mostrar(fig, "g_perfil")
    decisao("que grupos priorizar no contato. Quem já faltou antes é o sinal mais forte de nova falta.")

    st.subheader("Faixa etária")
    base = aplicar_cliques(df_lateral, menos="g_idade")
    tabela = taxa_por(base, "faixa_etaria", ORDEM_IDADE)
    escolhidas = selecoes_do_grafico("g_idade").get("faixa_etaria", set())
    fig = go.Figure(go.Bar(
        x=tabela["faixa_etaria"], y=tabela["taxa"],
        marker_color=cores_destaque(tabela["faixa_etaria"], escolhidas),
        text=[pct(t) for t in tabela["taxa"]], textposition="outside",
        customdata=[["faixa_etaria", f] for f in tabela["faixa_etaria"]],
        hovertemplate="%{x} anos<br>Taxa de faltas: %{text}<extra></extra>",
    ))
    fig = layout_padrao(fig, altura=280, yaxis=dict(tickformat=".0%", range=[0, max(tabela["taxa"].max() * 1.3, 0.05)]))
    mostrar(fig, "g_idade")
    decisao("adequar o canal de lembrete à idade (SMS, ligação ou aplicativo).")

st.divider()

# ---------------------------------------------------- diagnóstico e plano de ação
st.subheader("Diagnóstico e plano de ação para a seleção atual")
st.caption("Os números abaixo se recalculam com os filtros e cliques. São associações observadas nos dados, "
           "não provas de causa.")

d = df_sel
linhas = []

perto = d[d["antecedencia_dias"] == 0]["faltou"].mean()
longe = d[d["antecedencia_dias"] >= 8]["faltou"].mean()
if pd.notna(perto) and pd.notna(longe):
    linhas.append(("Antecedência",
                   f"Consultas marcadas com 8 dias ou mais têm **{pct(longe)}** de faltas, contra **{pct(perto)}** "
                   "nas marcadas para o mesmo dia.",
                   "Confirmar por telefone ou WhatsApp, 1 a 2 dias antes, toda consulta marcada com 8 dias ou mais."))

eleg = d[d["sms_possivel"] == "Sim"]
if len(eleg):
    sem = eleg[eleg["recebeu_sms"] == "Não"]
    # Estimativa simples: se as consultas elegíveis sem SMS tivessem a taxa das que receberam SMS,
    # comparando sempre dentro da mesma faixa de antecedência.
    taxas = eleg.groupby(["faixa_antecedencia", "recebeu_sms"], observed=True)["faltou"].mean().unstack()
    evitaveis = 0.0
    if {"Sim", "Não"} <= set(taxas.columns):
        for faixa_ant, n in sem.groupby("faixa_antecedencia", observed=True).size().items():
            ganho = taxas.loc[faixa_ant, "Não"] - taxas.loc[faixa_ant, "Sim"]
            if pd.notna(ganho) and ganho > 0:
                evitaveis += ganho * n
    linhas.append(("Lembrete por SMS",
                   f"**{num(len(sem))}** consultas marcadas com 3 dias ou mais (**{pct(len(sem) / len(eleg))}** "
                   "delas) não receberam SMS.",
                   f"Enviar SMS para todas elas. Pela diferença de faltas com e sem SMS na mesma faixa de espera, "
                   f"seriam cerca de **{num(round(evitaveis))} faltas a menos** neste recorte (estimativa)."))

hist = d.groupby("ja_faltou_antes")["faltou"].mean()
if {"Sim", "Não"} <= set(hist.index):
    n_hist = d[d["ja_faltou_antes"] == "Sim"]["id_paciente"].nunique()
    linhas.append(("Histórico do paciente",
                   f"Quem já tinha faltado antes falta **{pct(hist['Sim'])}** das vezes; quem nunca faltou, "
                   f"**{pct(hist['Não'])}**.",
                   f"Criar uma lista de atenção com esses **{num(n_hist)} pacientes** e fazer ligação de "
                   "confirmação para eles."))

bairros_tab = taxa_por(d, "bairro")
bairros_tab = bairros_tab[bairros_tab["consultas"] >= 300].sort_values("taxa", ascending=False)
if len(bairros_tab) >= 3:
    top = bairros_tab.head(3)
    nomes = ", ".join(f"{b} ({pct(t)})" for b, t in zip(top["bairro"], top["taxa"]))
    linhas.append(("Território",
                   f"Bairros com mais faltas (mínimo de 300 consultas): {nomes}.",
                   "Priorizar esses bairros na busca ativa feita pelos agentes comunitários de saúde."))

for titulo, diagnostico, acao in linhas:
    c1, c2 = st.columns([1, 1])
    c1.markdown(f"**{titulo}.** {diagnostico}")
    c2.markdown(f"➜ {acao}")

st.divider()

# ----------------------------------------------------------- sobre os dados
with st.expander("Sobre os dados e o tratamento feito"):
    st.markdown(
        f"Base pública **Medical Appointment No Shows** (Kaggle): {num(registro['linhas_originais'])} consultas "
        f"no arquivo original. Depois da limpeza, transformação e redução, ficaram "
        f"**{num(registro['linhas_finais'])}**. O passo a passo está abaixo e no relatório."
    )
    passos = []
    for etapa, nome in [("limpeza", "Limpeza"), ("transformacao", "Transformação"), ("reducao", "Redução")]:
        for p in registro[etapa]:
            passos.append({"Etapa": nome, "O que fizemos": p["acao"],
                           "Linhas retiradas": p["linhas_afetadas"] if etapa != "transformacao" else "–",
                           "Por quê": p["detalhe"]})
    st.dataframe(pd.DataFrame(passos), hide_index=True, use_container_width=True)

with st.expander("Ver as consultas da seleção atual"):
    colunas = ["data_consulta", "situacao", "bairro", "faixa_antecedencia", "antecedencia_dias", "recebeu_sms",
               "sexo", "idade", "bolsa_familia", "ja_faltou_antes"]
    st.dataframe(df_sel[colunas].head(500), hide_index=True, use_container_width=True)
    st.download_button("Baixar a seleção em CSV", df_sel.drop(columns="data_txt").to_csv(index=False).encode("utf-8"),
                       file_name="consultas_selecionadas.csv", mime="text/csv")
