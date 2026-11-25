"""
Gera o relatório do trabalho em Word (relatorio/Relatorio_Painel_BI_Faltas_Consultas.docx).

Segue o modelo do enunciado: capa e as seções 1 a 6. Os números vêm de apresentacao/dados.json
(gerado por dados_apresentacao.py) e a capa de apresentacao/identificacao.json, os mesmos usados
nos slides, então relatório, slides e painel sempre batem.

Para rodar:  python src/relatorio.py
Para ter o PDF:  soffice --headless --convert-to pdf --outdir relatorio relatorio/Relatorio_Painel_BI_Faltas_Consultas.docx
"""

import json
from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from gerar_metadados import NOVAS, SIGNIFICADO_ORIGINAL, SIGNIFICADO_TRATADO, milhar, resumo

RAIZ = Path(__file__).resolve().parent.parent
FIG = RAIZ / "figuras"
D = json.loads((RAIZ / "apresentacao" / "dados.json").read_text(encoding="utf-8"))
ID = json.loads((RAIZ / "apresentacao" / "identificacao.json").read_text(encoding="utf-8"))
SAIDA = RAIZ / "relatorio" / "Relatorio_Painel_BI_Faltas_Consultas.docx"

FONTE = "Calibri"
COR_TITULO = RGBColor(0x0E, 0x6E, 0x77)   # verde-petróleo, a mesma família de cor dos slides
COR_TEXTO = RGBColor(0x1F, 0x29, 0x37)
COR_CINZA = RGBColor(0x6B, 0x72, 0x80)
CABECALHO_TABELA = "0E6E77"
LINHA_TABELA = "C9D3D6"
LARGURA_UTIL = 16.0  # cm (A4 com margens de 2,5 cm)


def br(valor, casas=0):
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(valor):
    return br(valor, 1) + "%"


def data_br(iso):
    a, m, d = iso.split("-")
    return f"{d}/{m}/{a}"


# ------------------------------------------------------------------ estilos do documento
def configurar(doc):
    secao = doc.sections[0]
    secao.page_width, secao.page_height = Cm(21), Cm(29.7)
    for lado in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(secao, lado, Cm(2.5))

    normal = doc.styles["Normal"]
    normal.font.name = FONTE
    normal.font.size = Pt(11)
    normal.font.color.rgb = COR_TEXTO
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), FONTE)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.15
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    for nome, tamanho, antes in (("Heading 1", 14, 18), ("Heading 2", 12, 12)):
        estilo = doc.styles[nome]
        estilo.font.name = FONTE
        estilo.font.size = Pt(tamanho)
        estilo.font.bold = True
        estilo.font.color.rgb = COR_TITULO
        rfonts = estilo.element.rPr.rFonts
        for atributo in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
            rfonts.set(qn(atributo), FONTE)
        for tema in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
            rfonts.attrib.pop(qn(tema), None)
        estilo.paragraph_format.space_before = Pt(antes)
        estilo.paragraph_format.space_after = Pt(6)
        estilo.paragraph_format.keep_with_next = True

    legenda = doc.styles["Caption"]
    legenda.font.name = FONTE
    legenda.font.size = Pt(9.5)
    legenda.font.bold = False
    legenda.font.italic = False
    legenda.font.color.rgb = COR_CINZA

    lista = doc.styles["List Bullet"]
    lista.font.name = FONTE
    lista.paragraph_format.space_after = Pt(3)

    # Rodapé com o número da página (campo do Word)
    rodape = secao.footer.paragraphs[0]
    rodape.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = rodape.add_run()
    for tipo, texto in (("begin", None), (None, "PAGE"), ("end", None)):
        if tipo:
            campo = OxmlElement("w:fldChar")
            campo.set(qn("w:fldCharType"), tipo)
            run._r.append(campo)
        else:
            instr = OxmlElement("w:instrText")
            instr.set(qn("xml:space"), "preserve")
            instr.text = texto
            run._r.append(instr)
    run.font.size = Pt(9)
    run.font.color.rgb = COR_CINZA
    secao.different_first_page_header_footer = True   # capa sem número


# ------------------------------------------------------------------ blocos de texto
def paragrafo(doc, texto, negrito_inicial=None, alinhamento=None, tamanho=None, italico=False, cor=None, depois=None):
    """Parágrafo simples. negrito_inicial deixa em negrito só o começo (ex.: 'Datas.')."""
    p = doc.add_paragraph()
    if negrito_inicial:
        r = p.add_run(negrito_inicial + " ")
        r.bold = True
    r = p.add_run(texto)
    r.italic = italico
    for run in p.runs:
        if tamanho:
            run.font.size = Pt(tamanho)
        if cor:
            run.font.color.rgb = cor
    if alinhamento is not None:
        p.alignment = alinhamento
    if depois is not None:
        p.paragraph_format.space_after = Pt(depois)
    return p


def topicos(doc, itens):
    for item in itens:
        if isinstance(item, tuple):
            p = doc.add_paragraph(style="List Bullet")
            p.add_run(item[0] + " ").bold = True
            p.add_run(item[1])
        else:
            doc.add_paragraph(item, style="List Bullet")


def legenda(doc, texto, antes=True):
    p = doc.add_paragraph(texto, style="Caption")
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(6 if antes else 2)
    p.paragraph_format.space_after = Pt(3 if antes else 10)
    p.paragraph_format.keep_with_next = antes
    return p


def figura(doc, arquivo, texto, largura=LARGURA_UTIL):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_after = Pt(0)
    p.add_run().add_picture(str(FIG / f"{arquivo}.png"), width=Cm(largura))
    legenda(doc, texto, antes=False)


def sombrear(celula, cor):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), cor)
    celula._tc.get_or_add_tcPr().append(shd)


def bordas(tabela):
    tblPr = tabela._tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for lado in ("top", "bottom", "insideH"):
        el = OxmlElement(f"w:{lado}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), LINHA_TABELA)
        b.append(el)
    for lado in ("left", "right", "insideV"):
        el = OxmlElement(f"w:{lado}")
        el.set(qn("w:val"), "nil")
        b.append(el)
    tblPr.append(b)


def tabela(doc, titulo, cabecalho, linhas, larguras, numericas=(), tamanho=9.5):
    """Tabela no padrão do documento: título acima, cabeçalho colorido, linhas que não se partem."""
    legenda(doc, titulo)
    t = doc.add_table(rows=1, cols=len(cabecalho))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    bordas(t)
    escala = LARGURA_UTIL / sum(larguras)
    larguras = [Cm(l * escala) for l in larguras]

    def preencher(linha_tabela, valores, topo=False):
        tr = linha_tabela._tr
        trPr = tr.get_or_add_trPr()
        nao_partir = OxmlElement("w:cantSplit")
        trPr.append(nao_partir)
        if topo:
            repetir = OxmlElement("w:tblHeader")
            trPr.append(repetir)
        for i, (celula, valor) in enumerate(zip(linha_tabela.cells, valores)):
            celula.width = larguras[i]
            p = celula.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT if i in numericas else WD_ALIGN_PARAGRAPH.LEFT
            negrito = topo
            if isinstance(valor, tuple):      # (texto, negrito)
                valor, negrito = valor
            r = p.add_run(str(valor))
            r.font.size = Pt(tamanho)
            r.bold = negrito
            if topo:
                r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                sombrear(celula, CABECALHO_TABELA)

    preencher(t.rows[0], cabecalho, topo=True)
    for valores in linhas:
        preencher(t.add_row(), valores)
    # Larguras fixas na grade da tabela (o Word usa a da célula; o LibreOffice, a da grade)
    for i, coluna in enumerate(t.columns):
        coluna.width = larguras[i]
    tblPr = t._tbl.tblPr
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tblPr.append(layout)
    largura_total = OxmlElement("w:tblW")
    largura_total.set(qn("w:w"), str(int(sum(l.twips for l in larguras))))
    largura_total.set(qn("w:type"), "dxa")
    for antigo in tblPr.findall(qn("w:tblW")):
        tblPr.remove(antigo)
    tblPr.append(largura_total)
    # manter a tabela inteira junta quando couber na página
    for linha in t.rows[:-1]:
        for celula in linha.cells:
            for p in celula.paragraphs:
                p.paragraph_format.keep_with_next = True
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def quebra_pagina(doc):
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


# ------------------------------------------------------------------ conteúdo
def capa(doc):
    def linha(texto, tamanho=12, negrito=False, italico=False, cor=COR_TEXTO, depois=4, antes=0):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(depois)
        p.paragraph_format.space_before = Pt(antes)
        r = p.add_run(texto)
        r.font.size = Pt(tamanho)
        r.bold = negrito
        r.italic = italico
        r.font.color.rgb = cor
        return p

    linha("UNIVERSIDADE DE FORTALEZA", 12, negrito=True)
    linha(f"Curso de {ID['curso']}", 12)
    linha(f"Disciplina: {ID['disciplina']}", 12)
    linha(f"Professor: {ID['professor']}", 12, depois=90)
    linha("Por que os pacientes faltam às consultas?", 24, negrito=True, cor=COR_TITULO, depois=8)
    linha("Painel de BI interativo sobre as faltas em consultas na rede pública de saúde de Vitória (ES)", 13, depois=6)
    linha("Atividade Final: Painel de BI Interativo", 11, cor=COR_CINZA, depois=70)
    linha("Equipe", 11, negrito=True, depois=4)
    for nome, matricula in ID["equipe"]:
        linha(f"{nome} ({matricula})", 11, depois=1)
    linha(f"“{ID['frase']}”", 11, italico=True, antes=60, depois=2)
    linha("Albert Einstein", 10, cor=COR_CINZA, depois=80)   # a fonte completa está nas referências
    linha(ID["local_data"], 11)
    quebra_pagina(doc)


def sumario(doc):
    p = doc.add_paragraph()
    r = p.add_run("Sumário")
    r.bold = True
    r.font.size = Pt(14)
    r.font.color.rgb = COR_TITULO
    p.paragraph_format.space_after = Pt(12)
    itens = [
        ("1. Definição do problema", 0), ("1.1 Escolha da base de dados", 1), ("1.2 Informação e decisão em cada gráfico", 1),
        ("2. Metadados e estrutura", 0), ("3. Processo de pré-processamento", 0), ("3.1 Limpeza", 1),
        ("3.2 Transformação", 1), ("3.3 Redução", 1), ("4. Dashboard interativo", 0),
        ("4.1 Demonstração com filtros combinados", 1), ("5. Justificativa visual", 0),
        ("6. Análise de diagnóstico e plano de ação", 0), ("6.1 O diagnóstico", 1), ("6.2 A prescrição", 1),
        ("7. Considerações finais", 0), ("Referências", 0),
    ]
    for texto, nivel in itens:
        q = doc.add_paragraph(texto)
        q.alignment = WD_ALIGN_PARAGRAPH.LEFT
        q.paragraph_format.left_indent = Cm(0.8 * nivel)
        q.paragraph_format.space_after = Pt(4)
    quebra_pagina(doc)


def secao_1(doc):
    inicio, fim = data_br(D["periodo"][0]), data_br(D["periodo"][1])
    doc.add_heading("1. Definição do problema", level=1)
    paragrafo(doc, "Quando um paciente falta a uma consulta agendada, o horário do profissional fica ocioso e quem está "
              "na fila continua esperando por uma vaga. Na base analisada, das "
              f"{br(D['linhas_finais'])} consultas marcadas entre {inicio} e {fim} em unidades públicas de saúde de "
              f"Vitória (ES), {br(D['faltas'])} terminaram em falta, uma taxa de {pct(D['taxa_geral'])}. Isso equivale "
              f"a cerca de {br(D['faltas_por_dia'])} consultas perdidas por dia de atendimento.")
    paragrafo(doc, "O problema, para o gestor da rede, não é apenas o tamanho da taxa, mas não saber quem falta, onde e "
              "em que situação. Sem essa informação, ações como lembretes e confirmações acabam sendo aplicadas a todos "
              "os pacientes da mesma forma. O painel foi construído para apoiar três decisões:")
    topicos(doc, [
        ("Lembrete:", "para quais consultas enviar SMS e a partir de quantos dias de antecedência;"),
        ("Confirmação:", "quais consultas confirmar por telefone antes da data e quando liberar a vaga para encaixe;"),
        ("Prioridade:", "quais pacientes e bairros devem receber contato ou busca ativa primeiro."),
    ])

    doc.add_heading("1.1 Escolha da base de dados", level=2)
    paragrafo(doc, f"Utilizamos a base pública Medical Appointment No Shows, disponível no Kaggle, com "
              f"{br(D['linhas_originais'])} agendamentos reais e anonimizados de 2016. A escolha se deu por três motivos: o "
              "problema é real e fácil de entender; a base tem várias dimensões que podem ser cruzadas (data, bairro, "
              "idade, tempo de espera, SMS e condições de saúde); e os dados apresentam problemas de qualidade que "
              "exigem tratamento, como registros duplicados e idades impossíveis. A partir dela é possível medir a taxa "
              "de faltas, identificar os grupos e bairros com mais faltas e avaliar o efeito do lembrete por SMS.")

    doc.add_heading("1.2 Informação e decisão em cada gráfico", level=2)
    paragrafo(doc, "A Tabela 1 resume o que cada elemento do painel mostra e qual decisão ele permite tomar.")
    tabela(doc, "Tabela 1. Informação produzida e decisão apoiada por elemento do painel",
           ["Elemento", "Informação produzida", "Decisão possível"],
           [
               ["Indicadores do topo", "Consultas, faltas, taxa de faltas, pacientes e cobertura de SMS do recorte, com a diferença em relação à taxa geral", "Avaliar se o recorte escolhido está acima do normal"],
               ["Taxa por antecedência", "Como a falta varia com o tempo entre o agendamento e a consulta", "Definir até quantos dias agendar e a partir de quando confirmar"],
               ["SMS e sem SMS por antecedência", "Taxa de faltas de quem recebeu e de quem não recebeu lembrete, com a mesma espera", "Ampliar o envio de SMS"],
               ["Taxa dia a dia", "Evolução da taxa no período e dias fora do padrão", "Investigar dias atípicos"],
               ["Dia da semana", "Diferença de faltas entre os dias úteis", "Escolher os dias para reforçar a confirmação"],
               ["Bairros com mais faltas", "Ranking dos bairros, com o volume de consultas", "Definir onde fazer busca ativa"],
               ["Quem falta mais", "Taxa de faltas com e sem cada característica (histórico, Bolsa Família, doenças)", "Escolher o perfil a priorizar no contato"],
               ["Faixa etária", "Taxa de faltas por idade", "Escolher o canal de lembrete para cada público"],
               ["Diagnóstico e plano de ação", "Números e recomendações recalculados para o recorte", "Montar o plano de um bairro, perfil ou período"],
           ],
           [3.4, 6.6, 6.0])
    paragrafo(doc, "A decisão mais útil aparece quando os gráficos são combinados. Ao escolher um bairro e uma faixa de "
              "antecedência, por exemplo, o gestor vê na hora qual é a taxa de faltas daquele recorte, quanto o SMS a "
              "reduz e quantas faltas poderiam ser evitadas ali.")


def secao_2(doc):
    bruto = pd.read_csv(RAIZ / "dados" / "bruto" / "KaggleV2-May-2016.csv")
    tratado = pd.read_parquet(RAIZ / "dados" / "tratado" / "consultas_tratadas.parquet")
    doc.add_heading("2. Metadados e estrutura", level=1)
    paragrafo(doc, "A amostra é composta por dados estruturados: uma única tabela em formato CSV, o arquivo "
              f"KaggleV2-May-2016.csv, com {br(len(bruto))} registros e {bruto.shape[1]} colunas de esquema fixo. "
              "Todas as linhas têm as mesmas colunas, cada coluna tem um tipo e um significado definidos e não há "
              "campos de texto livre, imagens ou outros dados não estruturados. Cada linha representa uma consulta "
              "agendada. A Tabela 2 descreve as colunas originais.")
    linhas = [[c, resumo(bruto[c])[0], milhar(resumo(bruto[c])[1]), SIGNIFICADO_ORIGINAL[c]] for c in bruto.columns]
    tabela(doc, "Tabela 2. Colunas da base original", ["Coluna", "Tipo", "Valores distintos", "Significado"],
           linhas, [3.4, 1.8, 2.2, 8.6], numericas=(2,))
    paragrafo(doc, f"Após o pré-processamento, a tabela usada no painel ficou com {br(len(tratado))} linhas e "
              f"{tratado.shape[1]} colunas, com nomes em português. As colunas criadas pela equipe estão indicadas "
              "como “nova” na Tabela 3.")
    linhas = [[c + (" (nova)" if c in NOVAS else ""), resumo(tratado[c])[0], milhar(resumo(tratado[c])[1]),
               SIGNIFICADO_TRATADO[c]] for c in tratado.columns]
    tabela(doc, "Tabela 3. Colunas da base tratada", ["Coluna", "Tipo", "Valores distintos", "Significado"],
           linhas, [4.2, 1.6, 2.0, 8.2], numericas=(2,))


def secao_3(doc):
    reg = D["registro"]
    removidas = D["linhas_originais"] - D["linhas_finais"]
    doc.add_heading("3. Processo de pré-processamento", level=1)
    paragrafo(doc, "Todo o tratamento foi feito em Python, no script preparar_dados.py, que lê o arquivo original e "
              "grava a base tratada. Cada etapa registra quantas linhas havia antes e depois, e esse registro também "
              f"pode ser consultado dentro do painel. Ao final, a base passou de {br(D['linhas_originais'])} para "
              f"{br(D['linhas_finais'])} consultas, com {br(removidas)} linhas retiradas (0,6% do total).")

    doc.add_heading("3.1 Limpeza", level=2)
    paragrafo(doc, "Verificamos valores nulos, registros duplicados e valores impossíveis. O resultado de cada "
              "verificação está na Tabela 4.")
    tabela(doc, "Tabela 4. Etapas de limpeza", ["Verificação", "O que encontramos e o que fizemos", "Linhas retiradas"],
           [[p["acao"], p["detalhe"], br(p["linhas_afetadas"])] for p in reg["limpeza"]],
           [4.6, 9.0, 2.4], numericas=(2,))

    doc.add_heading("3.2 Transformação", level=2)
    paragrafo(doc, "a base original, em CSV (texto separado por vírgulas), foi gravada pelo script em Parquet, um "
              "formato binário organizado por colunas que preserva o tipo de cada coluna e é mais leve e rápido para o "
              "painel carregar (cerca de 3 MB, contra 11 MB do CSV).", negrito_inicial="Formato do arquivo:")
    paragrafo(doc, "as duas colunas de data vinham como texto (por exemplo, 2016-04-29T18:38:08Z) e foram convertidas "
              "para data. O agendamento manteve data e hora; a consulta ficou apenas com o dia, porque a base não "
              "informa o horário dela.", negrito_inicial="Datas:")
    paragrafo(doc, "a base não possui nenhum valor monetário, portanto não houve moeda a padronizar.",
              negrito_inicial="Moedas:")
    paragrafo(doc, "na coluna No-show, o valor “Yes” indica que o paciente faltou, o que costuma gerar confusão. Ela "
              "deu origem às colunas faltou (1 ou 0, cuja média é a própria taxa de faltas) e situacao (Faltou ou "
              "Compareceu).", negrito_inicial="Rótulos:")
    paragrafo(doc, "os nomes das colunas foram traduzidos e corrigidos (a origem traz Hipertension e Handcap), os "
              "valores 0 e 1 viraram Não e Sim, o sexo foi escrito por extenso e a grafia dos bairros foi "
              "uniformizada. Cinco códigos de paciente tinham casas decimais e foram corrigidos sem misturar "
              "pacientes diferentes.", negrito_inicial="Padronização:")
    paragrafo(doc, "A Tabela 5 apresenta as colunas criadas para a análise.")
    tabela(doc, "Tabela 5. Colunas criadas na transformação", ["Coluna", "Como é calculada", "Uso na análise"], [
        ["antecedencia_dias", "Dias entre o agendamento e a consulta", "Principal fator de falta encontrado"],
        ["faixa_antecedencia", "Antecedência agrupada em 7 faixas, do mesmo dia a mais de 60 dias", "Eixo dos gráficos de antecedência e de SMS"],
        ["sms_possivel", "Sim quando a consulta foi marcada com 3 dias ou mais", "Comparar o SMS apenas onde ele podia ser enviado"],
        ["faltas_anteriores", "Faltas do paciente antes da consulta, em ordem de data", "Medir a reincidência"],
        ["ja_faltou_antes", "Sim quando o paciente já havia faltado antes", "Filtro e lista de atenção"],
        ["dia_semana, hora_agendamento", "Extraídos das datas", "Padrões de calendário"],
        ["faixa_etaria, deficiencia", "Idade em 6 faixas; grau de deficiência maior que zero", "Filtros e perfil do paciente"],
    ], [4.4, 6.6, 5.0])

    doc.add_heading("3.3 Redução", level=2)
    paragrafo(doc, "Aplicamos dois filtros de relevância nas linhas e mantivemos apenas as colunas utilizadas na "
              f"análise, conforme a Tabela 6. A base final tem {D['colunas_finais']} colunas.")
    tabela(doc, "Tabela 6. Filtros de redução", ["Filtro", "Motivo", "Linhas retiradas"],
           [[p["acao"], p["detalhe"], br(p["linhas_afetadas"])] for p in reg["reducao"]],
           [4.6, 9.0, 2.4], numericas=(2,))


def secao_4(doc):
    combo = D["combo_exemplo"]
    doc.add_heading("4. Dashboard interativo", level=1)
    paragrafo(doc, "O painel foi desenvolvido em Python com as bibliotecas Streamlit e Plotly e está publicado no "
              "Streamlit Community Cloud, em https://bi-faltas-consultas.streamlit.app/. Também pode ser aberto localmente com o comando "
              "streamlit run app.py. Ele oferece três formas de filtrar, que se combinam entre si:")
    topicos(doc, [
        ("Filtros da lateral:", "período, bairro, antecedência, faixa etária, sexo, SMS, Bolsa Família, histórico de "
         "faltas e condição de saúde, além de um controle de mínimo de consultas no gráfico de bairros;"),
        ("Clique nos gráficos:", "ao clicar em uma barra ou ponto, todos os outros gráficos são filtrados por aquele "
         "valor (filtro cruzado), somando-se aos filtros da lateral;"),
        ("Seleção visível:", "uma faixa no topo mostra o que está selecionado nos gráficos, com um botão para limpar, "
         "e a barra escolhida fica destacada."),
    ])
    paragrafo(doc, "Abaixo de cada gráfico há um quadro que explica a decisão que ele apoia, e o fim da página traz "
              "o diagnóstico e o plano de ação recalculados para o recorte escolhido. A Figura 1 mostra o painel sem "
              "filtros.")
    figura(doc, "dash_geral_topo", "Figura 1. Painel sem filtros: indicadores gerais e os dois gráficos principais.")

    doc.add_heading("4.1 Demonstração com filtros combinados", level=2)
    paragrafo(doc, "Para demonstrar a combinação de filtros, escolhemos o bairro Itararé na lateral e clicamos na "
              "barra “8 a 15 dias” do gráfico de antecedência. Os dois filtros se somam e todo o painel é recalculado "
              "(Figura 2 e Tabela 7).")
    figura(doc, "dash_comb_topo", "Figura 2. Filtros combinados: bairro Itararé e antecedência de 8 a 15 dias.")
    tabela(doc, "Tabela 7. Indicadores da base inteira e do recorte combinado",
           ["Indicador", "Base inteira", "Itararé, 8 a 15 dias"], [
               ["Consultas", br(D["linhas_finais"]), br(combo["consultas"])],
               ["Taxa de faltas", pct(D["taxa_geral"]), pct(combo["taxa"])],
               ["Consultas elegíveis que receberam SMS", pct(D["cobertura_sms"]), pct(combo["cobertura_sms"])],
               ["Taxa de faltas sem SMS", pct(D["sms_geral"]["sem"]), pct(combo["sms_sem"])],
               ["Taxa de faltas com SMS", pct(D["sms_geral"]["com"]), pct(combo["sms_com"])],
           ], [8.0, 4.0, 4.0], numericas=(1, 2))
    paragrafo(doc, f"No recorte, a taxa de faltas sobe para {pct(combo['taxa'])}, {br(combo['taxa'] - D['taxa_geral'], 1)} "
              "pontos percentuais acima da média. Como a espera está fixa, a comparação do SMS fica justa: sem "
              f"lembrete, a falta é de {pct(combo['sms_sem'])}; com lembrete, de {pct(combo['sms_com'])}. O diagnóstico "
              "no fim da página também se ajusta ao recorte (Figura 3).")
    figura(doc, "dash_comb_diag", "Figura 3. Diagnóstico e plano de ação recalculados para o recorte combinado.")
    figura(doc, "dash_geral_baixo", "Figura 4. Parte inferior do painel: bairros, perfil de quem falta e faixa etária.", largura=13.5)


def secao_5(doc):
    doc.add_heading("5. Justificativa visual", level=1)
    paragrafo(doc, "Cada tipo de gráfico foi escolhido de acordo com a pergunta que precisa responder: barras para "
              "comparar grupos, linha para acompanhar a evolução no tempo e cartões para os números principais. "
              "Evitamos gráficos de pizza e 3D, que dificultam a comparação de valores próximos. A Tabela 8 detalha as "
              "escolhas.")
    tabela(doc, "Tabela 8. Tipo de gráfico escolhido e justificativa", ["Gráfico", "Tipo", "Justificativa"], [
        ["Indicadores", "Cartões com número e variação", "Mostram o tamanho do problema de imediato; a seta indica se o recorte está acima ou abaixo da média"],
        ["Taxa por antecedência", "Barras verticais ordenadas", "As faixas de espera têm ordem natural, e as barras evidenciam o crescimento da falta"],
        ["SMS e sem SMS", "Barras agrupadas", "Colocam os dois grupos lado a lado dentro de cada faixa de espera"],
        ["Taxa dia a dia", "Linha, com o volume em barras ao fundo", "A linha é adequada para tendência no tempo; o volume evita conclusões a partir de dias com poucas consultas"],
        ["Dia da semana", "Barras verticais", "Poucas categorias, comparação direta"],
        ["Bairros", "Barras horizontais ordenadas", "Nomes longos cabem melhor na horizontal e a ordem já forma o ranking"],
        ["Quem falta mais", "Barras horizontais agrupadas", "Comparam, para vários fatores, quem tem e quem não tem cada característica"],
        ["Faixa etária", "Barras verticais ordenadas", "As faixas de idade têm ordem natural"],
    ], [3.4, 4.4, 8.2])
    paragrafo(doc, "Quanto às cores, usamos coral para falta, por chamar atenção para o problema; verde-petróleo "
              "para o SMS e para os elementos da interface; e cinza para o grupo de comparação. Ao clicar em uma barra, "
              "ela fica em tom mais escuro e as demais ficam claras. Os gráficos usam fonte sem serifa em tamanho 14, "
              "com o valor escrito sobre cada barra e percentuais no formato brasileiro.")


def secao_6(doc):
    hist = D["historico"]
    top = D["bairros_top"]
    idade = {i["grupo"]: i for i in D["idade"]}
    bolsa = {b["grupo"]: b for b in D["bolsa"]}
    doc.add_heading("6. Análise de diagnóstico e plano de ação", level=1)

    doc.add_heading("6.1 O diagnóstico", level=2)
    paragrafo(doc, "A principal anomalia encontrada envolve o lembrete por SMS. Considerando a base inteira, quem "
              f"recebeu o lembrete faltou {pct(D['sms_geral']['com'])} das vezes, enquanto quem não recebeu faltou "
              f"{pct(D['sms_geral']['sem'])}. À primeira vista, o SMS estaria aumentando as faltas.")
    paragrafo(doc, "O cruzamento entre SMS e antecedência no painel explica o resultado. O SMS só foi enviado para "
              "consultas marcadas com 3 dias ou mais de antecedência, que são justamente as que mais têm faltas. As "
              f"consultas do mesmo dia, com apenas {pct(D['mesmo_dia'])} de faltas, nunca recebem SMS e reduzem a taxa do "
              "grupo sem lembrete. Quando a comparação é feita dentro da mesma faixa de espera (Tabela 9), o resultado "
              f"se inverte: o SMS reduz a falta em todas as faixas, de {br(D['sms_ganho_min'], 1)} a "
              f"{br(D['sms_ganho_max'], 1)} pontos percentuais.")
    tabela(doc, "Tabela 9. Taxa de faltas com e sem SMS por faixa de antecedência",
           ["Antecedência", "Consultas sem SMS", "Faltas sem SMS", "Consultas com SMS", "Faltas com SMS", "Diferença"],
           [[f["faixa"], br(f["n_sem"]), pct(f["sem"]), br(f["n_com"]), pct(f["com"]), f"{br(f['sem'] - f['com'], 1)} p.p."]
            for f in D["sms_faixas"]],
           [3.4, 2.6, 2.4, 2.6, 2.4, 2.6], numericas=(1, 2, 3, 4, 5))
    paragrafo(doc, f"Esse resultado também revela uma oportunidade: {br(D['elegiveis_sem_sms'])} consultas marcadas com "
              f"3 dias ou mais ({pct(D['elegiveis_sem_sms_pct'])} das que poderiam receber o lembrete) ficaram sem SMS.")
    paragrafo(doc, "Além disso, o painel mostrou que:")
    topicos(doc, [
        f"a taxa de faltas cresce com a antecedência: {pct(D['mesmo_dia'])} nas consultas do mesmo dia e "
        f"{pct(D['oito_ou_mais'])} nas marcadas com 8 dias ou mais, que somam {br(D['consultas_8_ou_mais'])} consultas;",
        f"quem já havia faltado antes falta {pct(hist['sim'])} das vezes, contra {pct(hist['nao'])} de quem nunca "
        f"faltou; são {br(hist['pacientes_sim'])} pacientes reincidentes;",
        f"entre os bairros com pelo menos 300 consultas, {top[0]['grupo']} ({pct(top[0]['taxa'])}), "
        f"{top[1]['grupo']} ({pct(top[1]['taxa'])}) e {top[2]['grupo']} ({pct(top[2]['taxa'])}) têm as maiores taxas;",
        f"adolescentes de 13 a 18 anos faltam {pct(idade['13 a 18']['taxa'])} e pessoas com 61 anos ou mais, "
        f"{pct(idade['61 ou mais']['taxa'])}; famílias do Bolsa Família faltam {pct(bolsa['Sim']['taxa'])}, contra "
        f"{pct(bolsa['Não']['taxa'])} das demais.",
    ])

    doc.add_heading("6.2 A prescrição", level=2)
    paragrafo(doc, "Com base no painel, sugerimos ao gestor da rede as ações da Tabela 10, em ordem de prioridade. "
              "Todas utilizam canais que a rede já possui: SMS, telefone e agentes comunitários de saúde.")
    tabela(doc, "Tabela 10. Plano de ação", ["Prioridade", "Ação", "Público", "Resultado esperado", "Acompanhamento no painel"], [
        ["1", "Enviar SMS para todas as consultas marcadas com 3 dias ou mais", f"{br(D['elegiveis_sem_sms'])} consultas que ficaram sem lembrete",
         f"Cerca de {br(D['faltas_evitaveis'])} faltas a menos no período, perto de {D['evitaveis_por_dia']} por dia", "Indicador de cobertura de SMS"],
        ["2", "Confirmar a presença por telefone ou WhatsApp 1 a 2 dias antes", f"{br(D['consultas_8_ou_mais'])} consultas marcadas com 8 dias ou mais",
         "Liberar para encaixe a vaga de quem não confirmar", "Gráfico de antecedência"],
        ["3", "Ligar para confirmar a consulta dos pacientes reincidentes", f"{br(hist['pacientes_sim'])} pacientes que já faltaram",
         "Reduzir a reincidência", "Filtro “Já tinha faltado antes”"],
        ["4", "Busca ativa pelos agentes comunitários de saúde", f"{top[0]['grupo']}, {top[1]['grupo']} e {top[2]['grupo']}",
         "Identificar barreiras de acesso locais", "Gráfico de bairros"],
        ["5", "Enviar o lembrete também ao responsável", "Adolescentes de 13 a 18 anos",
         "Alcançar quem organiza a ida à consulta", "Gráfico de faixa etária"],
    ], [1.8, 4.2, 3.6, 3.6, 2.8], tamanho=9)
    paragrafo(doc, "A estimativa de faltas evitáveis foi calculada aplicando, em cada faixa de antecedência, a "
              "diferença de faltas entre quem recebeu e quem não recebeu SMS às consultas que ficaram sem lembrete. "
              "Por se tratar de uma associação observada nos dados, e não de uma prova de causa, recomendamos começar "
              "a ampliação do SMS em alguns bairros e comparar o resultado com os demais no próprio painel antes de "
              "estender a medida para toda a rede.")


def secao_7(doc):
    doc.add_heading("7. Considerações finais", level=1)
    paragrafo(doc, "O painel permitiu passar da descrição do problema para ações concretas. O tempo de espera é o "
              "fator mais associado às faltas, o lembrete por SMS reduz a falta quando comparado de forma justa e o "
              "risco se concentra em pacientes reincidentes e em alguns bairros. A principal limitação é o período "
              "curto, de cerca de seis semanas em 2016, que impede analisar sazonalidade. A base também não traz o "
              "horário da consulta, a especialidade, a unidade de saúde nem valores em dinheiro.")


def referencias(doc):
    doc.add_heading("Referências", level=1)
    refs = [
        "HOPPEN, J. Medical appointment no shows: why do 30% of patients miss their scheduled appointments? [S. l.]: "
        "Kaggle, [2016?]. Disponível em: https://www.kaggle.com/datasets/joniarroba/noshowappointments. Acesso em: 16 nov. 2026.",
        "MCKINNEY, W. Data structures for statistical computing in Python. In: PYTHON IN SCIENCE CONFERENCE, 9., 2010, "
        "Austin. Proceedings [...]. Austin: SciPy, 2010. p. 56-61.",
        "PLOTLY TECHNOLOGIES. Plotly Python graphing library. Montreal: Plotly, 2026. Disponível em: https://plotly.com/python/. "
        "Acesso em: 16 nov. 2026.",
        "SNOWFLAKE. Streamlit documentation. 2026. Disponível em: https://docs.streamlit.io. Acesso em: 16 nov. 2026.",
        "VIERECK, G. S. What life means to Einstein: an interview by George Sylvester Viereck. The Saturday Evening Post, "
        "Philadelphia, p. 17, 26 out. 1929.",
    ]
    for r in refs:
        p = doc.add_paragraph(r)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.line_spacing = 1.0


def main():
    doc = Document()
    configurar(doc)
    capa(doc)
    sumario(doc)
    secao_1(doc)
    secao_2(doc)
    secao_3(doc)
    secao_4(doc)
    secao_5(doc)
    secao_6(doc)
    secao_7(doc)
    referencias(doc)
    doc.core_properties.title = "Por que os pacientes faltam às consultas? Painel de BI interativo"
    doc.core_properties.author = ", ".join(n for n, _ in ID["equipe"])
    doc.save(SAIDA)
    print("Relatório gravado em", SAIDA.relative_to(RAIZ))


if __name__ == "__main__":
    main()
