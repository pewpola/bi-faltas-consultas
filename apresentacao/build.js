// Gera Apresentacao_Painel_BI_Faltas_Consultas.pptx no mesmo visual da apresentação do SUS.
// Uso: node build.js   (antes: python src/dados_apresentacao.py e, para as capturas, python src/capturas.py)
// Os números vêm de dados.json e a capa de identificacao.json, os mesmos usados no relatório.
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require("./apply_theme.js");

const D = JSON.parse(fs.readFileSync(path.join(__dirname, "dados.json"), "utf8"));
const ID = JSON.parse(fs.readFileSync(path.join(__dirname, "identificacao.json"), "utf8"));
const FIG = path.join(__dirname, "..", "figuras");
const OUT = path.join(__dirname, "Apresentacao_Painel_BI_Faltas_Consultas.pptx");

const THEME = {
  name: "Faltas",
  headFontFace: "Arial",
  bodyFontFace: "Arial",
  colors: {
    dk1: "0B2530", lt1: "FFFFFF", dk2: "3A525C", lt2: "F3F7F8",
    accent1: "0E7C86", accent2: "E4572E", accent3: "7FD4DC", accent4: "6B7F87",
    accent5: "067647", accent6: "B42318", hlink: "0E7C86", folHlink: "3A525C",
  },
};
// Cores em hex para as opções que não aceitam cor de tema (gráficos, linhas).
// Coral = falta (a mesma cor do painel), verde-petróleo = SMS e destaque, cinza = comparação.
const HX = {
  ink: "0B2530", ink2: "3A525C", muted: "6B7F87", line: "D9E2E5", soft: "F3F7F8",
  teal: "0E7C86", teal2: "7FD4DC", tealSoft: "E3F2F3", sand: "C98A2B", sandSoft: "FBF1E1",
  coral: "E4572E", coralSoft: "F6C9BD", coralBg: "FDEDE8", coralInk: "A63A1F", cinza: "94A3B8",
  green: "067647", greenSoft: "E7F6EE", card: "1D3640", lightInk: "BFD6DB", footDark: "7FA6B0",
};

const br = (v, c = 0) => Number(v).toLocaleString("pt-BR", { minimumFractionDigits: c, maximumFractionDigits: c });
const pct = (v) => br(v, 1) + "%";

function pngSize(file) {
  const b = fs.readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}
// Encaixa a imagem na caixa mantendo a proporção (alinhada ao topo, centralizada na horizontal)
function fit(file, x, y, w, h) {
  const s = pngSize(file);
  const r = Math.min(w / s.w, h / s.h);
  return { path: file, x: x + (w - s.w * r) / 2, y, w: s.w * r, h: s.h * r };
}

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13,333 x 7,5 pol
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Por que os pacientes faltam às consultas? Painel de BI interativo";
pres.author = ID.equipe.map((e) => e[0]).join(", ");
const C = pres.SchemeColor;

const MX = 0.76;
const CW = 13.333 - 2 * MX;
const RODAPE = "Painel de BI Interativo · Faltas em consultas";

// ------------------------------------------------------------------ layouts
const eyebrowPh = (cor) => ({
  placeholder: {
    options: { name: "eyebrow", type: "body", x: MX, y: 0.5, w: CW, h: 0.32, fontSize: 11, bold: true,
      charSpacing: 2.5, color: cor, margin: 0, valign: "middle" },
    text: "",
  },
});
const titlePh = (cor) => ({
  placeholder: {
    options: { name: "title", type: "title", x: MX, y: 0.84, w: CW, h: 0.62, fontSize: 30, bold: true,
      color: cor, margin: 0, valign: "middle", align: "left" },
    text: "",
  },
});
pres.defineSlideMaster({
  title: "Conteudo",
  background: { color: "FFFFFF" },
  objects: [
    eyebrowPh(C.accent1), titlePh(C.text1),
    { text: { text: RODAPE, options: { x: MX, y: 7.0, w: 8, h: 0.25, fontSize: 9, color: C.accent4, margin: 0 } } },
  ],
  slideNumber: { x: 13.333 - MX - 0.6, y: 7.0, w: 0.6, h: 0.25, fontSize: 9, color: HX.muted, align: "right", margin: 0 },
});
pres.defineSlideMaster({
  title: "Escuro",
  background: { color: HX.ink },
  objects: [
    eyebrowPh(C.accent3), titlePh(C.background1),
    { text: { text: RODAPE, options: { x: MX, y: 7.0, w: 8, h: 0.25, fontSize: 9, color: HX.footDark, margin: 0 } } },
  ],
  slideNumber: { x: 13.333 - MX - 0.6, y: 7.0, w: 0.6, h: 0.25, fontSize: 9, color: HX.footDark, align: "right", margin: 0 },
});
pres.defineSlideMaster({ title: "Capa", background: { color: HX.ink }, objects: [] });

// O topo de cada slide mostra o número do próprio slide e o tema (ex.: "03 · Pré-processamento").
// A capa é o slide 1, então o primeiro slide de conteúdo é o 2.
let numeroSlide = 1;
function novo(secao, tema, titulo, master = "Conteudo") {
  numeroSlide += 1;
  const s = pres.addSlide({ masterName: master, sectionTitle: secao });
  s.addText(`${String(numeroSlide).padStart(2, "0")} · ${tema}`.toUpperCase(), { placeholder: "eyebrow" });
  s.addText(titulo, { placeholder: "title" });
  return s;
}
function secao(t) { pres.addSection({ title: t }); }

// ------------------------------------------------------------------ componentes
function box(s, x, y, w, h, fill, name) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { color: fill },
    rectRadius: 0.12, objectName: name });
}
function card(s, x, y, w, h, name) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: "FFFFFF" },
    line: { color: HX.line, width: 1.25 }, rectRadius: 0.12, objectName: name });
}
function pill(s, x, y, texto, fg, bg, w = null, fs = 11) {
  const ww = w || Math.max(0.7, texto.length * 0.095 + 0.35);
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: ww, h: 0.3, fill: { color: bg }, line: { color: bg }, rectRadius: 0.15 });
  s.addText(texto, { x, y, w: ww, h: 0.3, fontSize: fs, bold: true, color: fg, align: "center", valign: "middle",
    margin: 0, isTextBox: true });
  return ww;
}
function txt(s, texto, o) { s.addText(texto, { margin: 0, isTextBox: true, color: HX.ink2, fontSize: 14, ...o }); }
function hline(s, x, y, w, cor = HX.line) { s.addShape(pres.shapes.LINE, { x, y, w, h: 0, line: { color: cor, width: 1.25 } }); }
function stat(s, x, y, w, valor, legenda, { cor = HX.ink, leg = HX.ink2, tam = 40 } = {}) {
  txt(s, valor, { x, y, w, h: 0.7, fontSize: tam, bold: true, color: cor, valign: "bottom" });
  txt(s, legenda, { x, y: y + 0.78, w, h: 0.6, fontSize: 13, color: leg, valign: "top" });
}
function print(s, nome, x, y, w, h, objName) {
  const img = fit(path.join(FIG, nome + ".png"), x, y, w, h);
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: img.x - 0.06, y: img.y - 0.06, w: img.w + 0.12, h: img.h + 0.12,
    fill: { color: "FFFFFF" }, line: { color: HX.line, width: 1.25 }, rectRadius: 0.06, objectName: "moldura_" + objName });
  s.addImage({ ...img, objectName: objName });
  return img;
}

const eixo = {
  catAxisLabelColor: HX.ink2, valAxisLabelColor: HX.muted, catAxisLabelFontSize: 12, valAxisLabelFontSize: 10,
  catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", dataLabelFontFace: "+mn-lt",
  catAxisLineShow: false, valGridLine: { style: "none" }, catGridLine: { style: "none" },
  dataLabelColor: HX.ink, dataLabelFontSize: 12, showValue: true, dataLabelPosition: "outEnd",
  dataLabelFormatCode: '0.0"%"', showLegend: false, valAxisHidden: true, lang: "pt-BR",
};

const ant = D.antecedencia;
const hist = D.historico;
const combo = D.combo_exemplo;
const idade = Object.fromEntries(D.idade.map((i) => [i.grupo, i]));
const bolsa = Object.fromEntries(D.bolsa.map((b) => [b.grupo, b]));
const top = D.bairros_top;
const dataBr = (iso) => iso.split("-").reverse().join("/");
const [ini, fim] = D.periodo.map(dataBr);

// ================================================================== 1. capa
secao("Abertura");
{
  const s = pres.addSlide({ masterName: "Capa", sectionTitle: "Abertura" });
  s.addImage({ path: path.join(__dirname, "ondas.png"), x: 0, y: 0, w: 13.333, h: 7.5, objectName: "ondas" });
  txt(s, "BUSINESS INTELLIGENCE · PAINEL DE BI INTERATIVO", { x: 0.9, y: 1.25, w: 10, h: 0.35, fontSize: 12,
    bold: true, charSpacing: 2.5, color: HX.teal2 });
  s.addText("Uma em cada cinco\nconsultas termina em falta", { x: 0.9, y: 1.7, w: 11.5, h: 1.75,
    fontSize: 44, bold: true, color: "FFFFFF", margin: 0, valign: "top", lineSpacingMultiple: 0.95, isTextBox: true });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.9, y: 3.75, w: 0.83, h: 0.05, fill: { color: HX.coral },
    line: { color: HX.coral }, rectRadius: 0.02, objectName: "traco" });
  txt(s, "Por que os pacientes faltam às consultas, e o que fazer a respeito", { x: 0.9, y: 4.0, w: 11, h: 0.4,
    fontSize: 18, color: HX.lightInk });
  txt(s, `Rede pública de saúde de Vitória (ES) · ${br(D.linhas_finais)} consultas · Python, Streamlit e Plotly`,
    { x: 0.9, y: 4.45, w: 11, h: 0.35, fontSize: 13, color: HX.footDark });
  txt(s, `${ID.curso} · ${ID.disciplina} · Prof. ${ID.professor}`,
    { x: 0.9, y: 5.05, w: 11, h: 0.35, fontSize: 13, color: HX.lightInk });
  txt(s, "EQUIPE", { x: 0.9, y: 6.1, w: 3, h: 0.25, fontSize: 10, bold: true, charSpacing: 2, color: HX.teal2 });
  ID.equipe.forEach(([n, m], i) => {
    const x = 0.9 + i * 2.15;
    txt(s, n, { x, y: 6.45, w: 2.1, h: 0.25, fontSize: 11, bold: true, color: "FFFFFF" });
    txt(s, m, { x, y: 6.72, w: 2.1, h: 0.22, fontSize: 9, color: HX.lightInk, fontFace: "Courier New" });
  });
  s.addNotes("Abertura em uma frase: de cada cinco consultas marcadas na rede pública de Vitória, uma termina em " +
    "falta. Nosso trabalho mostra quem falta, onde e em que situação, e o que o gestor pode fazer para reduzir isso.");
}


// ================================================================== 2. problema e base
secao("O problema");
{
  const s = novo("O problema", "O problema", "Cada falta é um horário parado e alguém a mais na fila");
  const w = 3.55;
  const stats = [
    [br(D.faltas), `faltas em ${br(D.linhas_finais)} consultas, de ${ini} a ${fim}`, HX.ink, "FFFFFF", HX.lightInk],
    [pct(D.taxa_geral), "das consultas marcadas terminam em falta: uma em cada cinco", HX.coralBg, HX.coralInk, HX.ink2],
    [br(D.faltas_por_dia), "horários perdidos por dia de atendimento, em uma só cidade", HX.soft, HX.ink, HX.ink2],
  ];
  stats.forEach(([v, l, bg, cor, leg], i) => {
    const y = 1.85 + i * 1.65;
    box(s, MX, y, w, 1.5, bg, "stat_" + i);
    stat(s, MX + 0.35, y + 0.12, w - 0.7, v, l, { cor, leg, tam: 36 });
  });
  const x = MX + w + 0.45, ww = CW - w - 0.45;
  txt(s, "DECISÕES QUE O PAINEL APOIA", { x, y: 1.85, w: ww, h: 0.3, fontSize: 11, bold: true, charSpacing: 1.5, color: HX.teal });
  const dec = [
    ["Lembrete", "para quais consultas enviar SMS, e a partir de quantos dias de espera"],
    ["Confirmação", "quais consultas confirmar antes do dia e quando liberar a vaga"],
    ["Prioridade", "que pacientes e bairros recebem contato ou busca ativa primeiro"],
  ];
  const cw = (ww - 0.4) / 3;
  dec.forEach(([t, d], i) => {
    const xx = x + i * (cw + 0.2);
    card(s, xx, 2.2, cw, 1.5, "decisao_" + i);
    txt(s, t, { x: xx + 0.25, y: 2.35, w: cw - 0.5, h: 0.4, fontSize: 17, bold: true, color: HX.ink });
    txt(s, d, { x: xx + 0.25, y: 2.78, w: cw - 0.5, h: 0.85, fontSize: 12.5, valign: "top" });
  });
  box(s, x, 3.9, ww, 2.85, HX.ink, "ficha_base");
  txt(s, "A BASE · MEDICAL APPOINTMENT NO SHOWS (KAGGLE)", { x: x + 0.35, y: 4.07, w: ww - 0.7, h: 0.3, fontSize: 11,
    bold: true, charSpacing: 1.5, color: HX.teal2 });
  const ficha = [
    [br(D.linhas_originais), "consultas marcadas"], ["14", "colunas, uma tabela"],
    ["2016", "dados reais e anonimizados"], ["81", "bairros de Vitória (ES)"],
  ];
  const fw = (ww - 0.7) / 4;
  ficha.forEach(([v, l], i) => {
    const xx = x + 0.35 + i * fw;
    txt(s, v, { x: xx, y: 4.43, w: fw - 0.1, h: 0.5, fontSize: 26, bold: true, color: "FFFFFF" });
    txt(s, l, { x: xx, y: 4.93, w: fw - 0.1, h: 0.45, fontSize: 11.5, color: HX.lightInk, valign: "top" });
  });
  s.addText([
    { text: "Colunas: ", options: { bold: true, color: "FFFFFF" } },
    { text: "uma linha por consulta, com quem (idade, sexo, Bolsa Família), quando, onde (bairro), saúde, SMS e se faltou.", options: { breakLine: true } },
    { text: "Por que: ", options: { bold: true, color: "FFFFFF" } },
    { text: "problema real e brasileiro, muitas dimensões para cruzar e sujeira de verdade para tratar." },
  ], { x: x + 0.35, y: 5.55, w: ww - 0.7, h: 1.05, fontSize: 12, color: HX.lightInk, valign: "top", margin: 0,
    paraSpaceAfter: 4, isTextBox: true });
  s.addNotes(`O valor para a rede: são cerca de ${br(D.faltas_por_dia)} horários parados por dia. Sem saber quem falta, ` +
    "onde e quando, toda ação vale para todos, custa caro e rende pouco. O painel serve para decidir três coisas: " +
    "lembrete, confirmação e prioridade. A base é pública, do Kaggle, com agendamentos reais e anonimizados de 2016. " +
    "Cuidado com o rótulo: na coluna No-show, 'Yes' quer dizer que o paciente faltou. O dicionário completo está no relatório, seção 2.");
}

// ================================================================== 3. limpeza e tratamento dos dados
secao("Os dados");
{
  const s = novo("Os dados", "Pré-processamento", "Como limpamos e tratamos os dados");
  const r = D.registro;
  const n = (lista, palavra) => lista.find((p) => p.acao.includes(palavra)).linhas_afetadas;
  const colunas = [
    ["Limpeza", [
      ["Valores nulos", "nenhum encontrado", "0"],
      ["Agendamentos duplicados", "gravados duas vezes no mesmo segundo", br(n(r.limpeza, "duplicados"))],
      ["Idades impossíveis", "−1 e 115 anos", br(n(r.limpeza, "negativa") + n(r.limpeza, "110"))],
      ["Consulta antes do agendamento", "espera negativa", br(n(r.limpeza, "anteriores"))],
    ]],
    ["Transformação", [
      ["Formato do arquivo", "CSV para Parquet, que guarda os tipos", "✓"],
      ["Tipos e rótulos", "texto virou data; No-show virou 1/0", "✓"],
      ["Moedas", "a base não tem valores em dinheiro", "n/a"],
      ["Novas colunas", "antecedência, histórico, faixas", "+9"],
    ]],
    ["Redução", [
      ["Sábado isolado", "único dia fora de segunda a sexta", br(n(r.reducao, "sábado"))],
      ["Bairros com < 30 consultas", "taxa pouco confiável", br(n(r.reducao, "bairros"))],
      ["Colunas", "só as que apoiam alguma decisão", String(D.colunas_finais)],
    ]],
  ];
  const w = (CW - 2 * 0.3) / 3;
  colunas.forEach(([t, itens], i) => {
    const x = MX + i * (w + 0.3);
    txt(s, t, { x, y: 1.8, w, h: 0.45, fontSize: 20, bold: true, color: HX.ink });
    hline(s, x, 2.3, w, HX.ink);
    itens.forEach(([a, d, v], j) => {
      const y = 2.4 + j * 0.86;
      txt(s, a, { x, y: y + 0.08, w: w - 0.95, h: 0.34, fontSize: 14.5, bold: true, color: HX.ink });
      txt(s, d, { x, y: y + 0.42, w: w - 0.95, h: 0.32, fontSize: 11.5 });
      pill(s, x + w - 0.8, y + 0.22, v, HX.teal, HX.tealSoft, 0.8, 12);
      if (j < itens.length - 1) hline(s, x, y + 0.86, w);
    });
  });
  box(s, MX, 6.1, CW, 0.66, HX.tealSoft, "resultado_tratamento");
  s.addText([
    { text: "Resultado: ", options: { bold: true, color: HX.ink } },
    { text: `de ${br(D.linhas_originais)} para ${br(D.linhas_finais)} consultas: ${br(D.linhas_originais - D.linhas_finais)} linhas retiradas (0,6%), cada passo registrado e visível no próprio painel.` },
  ], { x: MX + 0.25, y: 6.1, w: CW - 0.5, h: 0.66, fontSize: 14, color: HX.ink2, valign: "middle", margin: 0, isTextBox: true });
  s.addNotes("Dados estruturados: uma tabela em CSV, com esquema fixo. Tudo está em src/preparar_dados.py, que grava a base " +
    "tratada em Parquet, formato que guarda os tipos e é mais leve para o painel. Destaque: as duplicatas eram o mesmo agendamento gravado duas " +
    "vezes no mesmo segundo. Na transformação, a coluna mais importante criada foi a antecedência, que virou o " +
    "principal fator de falta.");
}


// ================================================================== 4. painel e filtros combinados
secao("O painel");
{
  const s = novo("O painel", "Painel interativo", "Todos os gráficos se filtram entre si");
  print(s, "dash_comb_topo", MX, 1.8, 8.3, 4.95, "print_combinado");
  const x = MX + 8.7, w = CW - 8.7;
  const itens = [
    ["9 filtros na lateral", "período, bairro, espera, idade, sexo, SMS, Bolsa Família, histórico e saúde"],
    ["Clique filtra tudo", "clicar numa barra filtra os outros gráficos, somando aos filtros"],
    ["Decisão em cada gráfico", "e o plano de ação recalculado para o recorte"],
  ];
  itens.forEach(([t, d], i) => {
    const y = 1.85 + i * 0.98;
    box(s, x, y, w, 0.86, HX.soft, "recurso_" + i);
    txt(s, t, { x: x + 0.22, y: y + 0.08, w: w - 0.4, h: 0.32, fontSize: 14, bold: true, color: HX.ink });
    txt(s, d, { x: x + 0.22, y: y + 0.4, w: w - 0.4, h: 0.42, fontSize: 10.5, valign: "top" });
  });
  box(s, x, 4.85, w, 1.9, HX.coralBg, "stat_combo");
  txt(s, "ITARARÉ + 8 A 15 DIAS", { x: x + 0.25, y: 4.97, w: w - 0.4, h: 0.28, fontSize: 10, bold: true, charSpacing: 1.5, color: HX.coralInk });
  txt(s, pct(combo.taxa), { x: x + 0.25, y: 5.25, w: w - 0.4, h: 0.6, fontSize: 32, bold: true, color: HX.coralInk, valign: "middle" });
  txt(s, `de faltas (+${br(combo.taxa - D.taxa_geral, 1)} p.p.)\nsem SMS ${pct(combo.sms_sem)} · com SMS ${pct(combo.sms_com)}`,
    { x: x + 0.25, y: 5.9, w: w - 0.4, h: 0.75, fontSize: 12, color: HX.ink2, valign: "top" });
  s.addNotes("Feito em Python com Streamlit e Plotly. A captura mostra dois filtros de origens diferentes somados: o " +
    "bairro Itararé escolhido na lateral e o clique na barra '8 a 15 dias'. A taxa vai a 37,1%, e o gráfico de SMS " +
    "passa a mostrar só esse recorte: com lembrete, a falta cai quase 11 pontos. É o que faremos ao vivo no fim.");
}

// ================================================================== 5. justificativa visual
{
  const s = novo("O painel", "Justificativa visual", "Cada gráfico foi escolhido pela pergunta que responde");
  const tipos = [
    ["Barras em ordem", "Antecedência e faixa etária", "categorias com ordem natural: a escada de crescimento aparece sozinha"],
    ["Barras agrupadas", "SMS × sem SMS · Quem falta mais", "dois grupos lado a lado: a comparação justa"],
    ["Linha", "Taxa dia a dia", "o tipo certo para tendência no tempo; volume ao fundo para não enganar"],
    ["Barras horizontais", "Bairros", "nomes longos cabem e a ordem já é o ranking"],
    ["Cartões", "Indicadores do topo", "o número-chave de relance, com a variação contra a média"],
    ["Cores com função", "Todo o painel", "coral = falta, verde = SMS, cinza = comparação; clicado fica escuro"],
  ];
  const w = (CW - 2 * 0.25) / 3, h = 2.25;
  tipos.forEach(([t, onde, por], i) => {
    const x = MX + (i % 3) * (w + 0.25), y = 1.85 + Math.floor(i / 3) * (h + 0.25);
    box(s, x, y, w, h, i === 5 ? HX.ink : HX.soft, "tipo_" + i);
    const esc = i === 5;
    txt(s, t, { x: x + 0.3, y: y + 0.25, w: w - 0.6, h: 0.42, fontSize: 19, bold: true, color: esc ? "FFFFFF" : HX.ink });
    txt(s, onde.toUpperCase(), { x: x + 0.3, y: y + 0.72, w: w - 0.6, h: 0.3, fontSize: 10, bold: true, charSpacing: 1, color: esc ? HX.teal2 : HX.teal });
    txt(s, por, { x: x + 0.3, y: y + 1.1, w: w - 0.6, h: 0.95, fontSize: 13.5, color: esc ? HX.lightInk : HX.ink2, valign: "top" });
  });
  s.addNotes("Regra geral: barras para comparar, linha para tempo, cartões para os números-chave. Não usamos pizza " +
    "nem 3D, que dificultam comparar valores próximos. A tabela completa está na seção 5 do relatório.");
}


// ================================================================== 6. diagnóstico: espera, quem e onde
secao("A decisão");
{
  const s = novo("A decisão", "Diagnóstico", "Espera longa e reincidência concentram as faltas");
  txt(s, "Taxa de faltas por antecedência do agendamento", { x: MX, y: 1.8, w: 7.6, h: 0.3, fontSize: 13, bold: true, color: HX.ink });
  s.addChart(pres.charts.BAR, [{ name: "Taxa", labels: ant.map((a) => a.grupo), values: ant.map((a) => a.taxa) }], {
    x: MX - 0.1, y: 2.15, w: 7.7, h: 4.0, barDir: "col", barGapWidthPct: 40, ...eixo,
    chartColors: ant.map((a) => (["Mesmo dia", "1 a 2 dias", "3 a 7 dias"].includes(a.grupo) ? HX.coralSoft : HX.coral)),
    valAxisMaxVal: 40, catAxisLabelFontSize: 11,
  });
  txt(s, `${pct(D.mesmo_dia)} no mesmo dia contra ${pct(D.oito_ou_mais)} com 8 dias ou mais · ${br(D.consultas_8_ou_mais)} consultas nessa situação`,
    { x: MX, y: 6.3, w: 7.6, h: 0.4, fontSize: 12.5, color: HX.ink2, bold: true });
  const x = MX + 8.0, w = CW - 8.0;
  box(s, x, 1.85, w, 2.1, HX.ink, "stat_reincidente");
  txt(s, "REINCIDÊNCIA", { x: x + 0.3, y: 1.98, w: w - 0.5, h: 0.28, fontSize: 10, bold: true, charSpacing: 1.5, color: HX.teal2 });
  s.addText([
    { text: pct(hist.sim), options: { bold: true, color: HX.coral, fontSize: 28 } },
    { text: "  já faltou antes", options: { breakLine: true } },
    { text: pct(hist.nao), options: { bold: true, color: "FFFFFF", fontSize: 28 } },
    { text: "  nunca faltou" },
  ], { x: x + 0.3, y: 2.3, w: w - 0.5, h: 1.15, fontSize: 12.5, color: HX.lightInk, margin: 0, valign: "middle", paraSpaceAfter: 2, isTextBox: true });
  txt(s, `${br(hist.pacientes_sim)} pacientes reincidentes`, { x: x + 0.3, y: 3.5, w: w - 0.5, h: 0.32, fontSize: 12, color: HX.teal2, bold: true });
  card(s, x, 4.1, w, 2.65, "onde_quem");
  txt(s, "ONDE E QUEM (MÉDIA: " + pct(D.taxa_geral) + ")", { x: x + 0.3, y: 4.22, w: w - 0.5, h: 0.28, fontSize: 10, bold: true, charSpacing: 1.5, color: HX.muted });
  const linhas = [
    [top[0].grupo, pct(top[0].taxa)], [top[1].grupo, pct(top[1].taxa)], [top[2].grupo, pct(top[2].taxa)],
    ["Adolescentes (13 a 18)", pct(idade["13 a 18"].taxa)], ["Bolsa Família", pct(bolsa["Sim"].taxa)],
  ];
  linhas.forEach(([t, v], i) => {
    const y = 4.55 + i * 0.42;
    txt(s, t, { x: x + 0.3, y, w: w - 1.6, h: 0.4, fontSize: 13, color: HX.ink, valign: "middle" });
    txt(s, v, { x: x + w - 1.35, y, w: 1.1, h: 0.4, fontSize: 15, bold: true, color: HX.coralInk, align: "right", valign: "middle" });
  });
  s.addNotes("O fator mais forte da base é a espera: consulta marcada para o mesmo dia quase não tem falta; com uma " +
    "semana ou mais, passa de 30%. Quem já faltou uma vez é o sinal mais forte de nova falta. No território, os " +
    "bairros do topo ficam de 6 a 9 pontos acima da média (mínimo de 300 consultas). Adolescentes e famílias do " +
    "Bolsa Família também faltam mais.");
}

// ================================================================== 7. anomalia do SMS
{
  const s = novo("A decisão", "Diagnóstico: a anomalia", "O SMS parece aumentar a falta. Na verdade, reduz");
  const w1 = 3.7;
  txt(s, "BASE INTEIRA: O QUE PARECE", { x: MX, y: 1.8, w: w1, h: 0.3, fontSize: 11, bold: true, charSpacing: 1.5, color: HX.coralInk });
  s.addChart(pres.charts.BAR, [{ name: "Taxa", labels: ["Sem SMS", "Com SMS"], values: [D.sms_geral.sem, D.sms_geral.com] }], {
    x: MX - 0.1, y: 2.15, w: w1 + 0.1, h: 3.3, barDir: "col", barGapWidthPct: 55, ...eixo,
    chartColors: [HX.cinza, HX.teal], valAxisMaxVal: 35, catAxisLabelFontSize: 13, dataLabelFontSize: 14,
  });
  const x2 = MX + w1 + 0.45, w2 = CW - w1 - 0.45;
  txt(s, "NA MESMA FAIXA DE ESPERA: O QUE ACONTECE", { x: x2, y: 1.8, w: w2, h: 0.3, fontSize: 11, bold: true, charSpacing: 1.5, color: HX.teal });
  const f = D.sms_faixas;
  s.addChart(pres.charts.BAR, [
    { name: "Sem SMS", labels: f.map((x) => x.faixa), values: f.map((x) => x.sem) },
    { name: "Com SMS", labels: f.map((x) => x.faixa), values: f.map((x) => x.com) },
  ], {
    x: x2 - 0.1, y: 2.15, w: w2 + 0.1, h: 3.3, barDir: "col", barGapWidthPct: 45, ...eixo,
    chartColors: [HX.cinza, HX.teal], valAxisMaxVal: 45, dataLabelFontSize: 11, catAxisLabelFontSize: 11,
    showLegend: true, legendPos: "t", legendFontSize: 11, legendColor: HX.ink2, legendFontFace: "+mn-lt",
  });
  box(s, MX, 5.65, CW, 1.1, HX.tealSoft, "explicacao_sms");
  s.addText([
    { text: "Por quê: ", options: { bold: true, color: HX.ink } },
    { text: "o SMS só é enviado para consultas marcadas com 3 dias ou mais, que já faltam mais. Comparando na " +
      `mesma espera, quem recebe o lembrete falta menos em todas as faixas, de ${br(D.sms_ganho_min, 1)} a ` +
      `${br(D.sms_ganho_max, 1)} pontos. Só aparece combinando filtros.` },
  ], { x: MX + 0.3, y: 5.65, w: CW - 0.6, h: 1.1, fontSize: 14, color: HX.ink2, valign: "middle", margin: 0, isTextBox: true });
  s.addNotes("Esta é a anomalia que pedimos ao painel para explicar. Na base inteira, o grupo sem SMS está cheio de " +
    `consultas do mesmo dia, que quase não têm falta (${pct(D.mesmo_dia)}), e nunca recebem SMS. Quando fixamos a ` +
    "espera, a comparação fica justa e o SMS ajuda em todas as faixas.");
}


// ================================================================== 8. plano de ação
{
  const s = novo("A decisão", "Prescrição", "Plano de ação: cinco medidas, em ordem de prioridade");
  const acoes = [
    ["1", "SMS para toda consulta marcada com 3 dias ou mais", `${br(D.elegiveis_sem_sms)} consultas ficaram sem lembrete`, `≈ ${br(D.faltas_evitaveis)} faltas a menos`, HX.coral],
    ["2", "Confirmar por telefone ou WhatsApp 1 a 2 dias antes", `${br(D.consultas_8_ou_mais)} consultas com 8 dias ou mais`, "vaga liberada para encaixe", HX.coral],
    ["3", "Lista de atenção com ligação de confirmação", `${br(hist.pacientes_sim)} pacientes reincidentes`, `falta de ${pct(hist.sim)} a reduzir`, HX.sand],
    ["4", "Busca ativa dos agentes comunitários", `${top[0].grupo}, ${top[1].grupo} e ${top[2].grupo}`, "barreiras locais de acesso", HX.sand],
    ["5", "Lembrete também para o responsável", "adolescentes de 13 a 18 anos", "alcançar quem leva à consulta", HX.cinza],
  ];
  txt(s, "AÇÃO", { x: MX + 0.75, y: 1.72, w: 5, h: 0.25, fontSize: 10, bold: true, charSpacing: 1.5, color: HX.muted });
  txt(s, "PARA QUEM", { x: MX + 6.3, y: 1.72, w: 3, h: 0.25, fontSize: 10, bold: true, charSpacing: 1.5, color: HX.muted });
  txt(s, "RESULTADO ESPERADO", { x: MX + 9.3, y: 1.72, w: 2.5, h: 0.25, fontSize: 10, bold: true, charSpacing: 1.5, color: HX.muted });
  hline(s, MX, 2.02, CW, HX.ink);
  const rh = 0.78;
  acoes.forEach(([n, a, quem, res, cor], i) => {
    const y = 2.08 + i * rh;
    s.addShape(pres.shapes.OVAL, { x: MX, y: y + (rh - 0.48) / 2, w: 0.48, h: 0.48, fill: { color: cor }, line: { color: cor } });
    txt(s, n, { x: MX, y: y + (rh - 0.48) / 2, w: 0.48, h: 0.48, fontSize: 15, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
    txt(s, a, { x: MX + 0.75, y, w: 5.4, h: rh, fontSize: 15.5, bold: true, color: HX.ink, valign: "middle" });
    txt(s, quem, { x: MX + 6.3, y, w: 2.85, h: rh, fontSize: 12.5, valign: "middle" });
    txt(s, res, { x: MX + 9.3, y, w: CW - 9.3, h: rh, fontSize: 12.5, bold: i === 0, color: i === 0 ? HX.coralInk : HX.ink2, valign: "middle" });
    if (i < acoes.length - 1) hline(s, MX, y + rh, CW);
  });
  box(s, MX, 6.1, CW, 0.66, HX.tealSoft, "acompanhar");
  s.addText([
    { text: "Como acompanhar: ", options: { bold: true, color: HX.ink } },
    { text: "o próprio painel mede cada ação: cobertura de SMS, taxa por faixa de espera, filtro de reincidentes e ranking de bairros." },
  ], { x: MX + 0.25, y: 6.1, w: CW - 0.5, h: 0.66, fontSize: 13.5, color: HX.ink2, valign: "middle", margin: 0, isTextBox: true });
  s.addNotes("A prescrição. As duas primeiras são as de maior impacto e usam canais que a rede já tem. Cada ação " +
    "tem um gráfico do painel para acompanhar o resultado.");
}

// ================================================================== 9. valor para o negócio
{
  const s = novo("A decisão", "Valor para o negócio", `Só a ação 1 devolve cerca de ${D.evitaveis_por_dia} consultas por dia`, "Escuro");
  const w = (CW - 2 * 0.3) / 3;
  const vals = [
    [br(D.faltas_evitaveis), "faltas evitáveis no período, com SMS para todas as consultas elegíveis"],
    [`≈ ${br(D.evitaveis_por_dia)}`, "horários devolvidos por dia de atendimento, sem abrir nenhuma vaga nova"],
    [br(D.elegiveis_sem_sms), "lembretes a mais: um canal que a rede já usa, com custo baixo"],
  ];
  vals.forEach(([v, l], i) => {
    const x = MX + i * (w + 0.3);
    box(s, x, 1.9, w, 2.3, HX.card, "valor_" + i);
    txt(s, v, { x: x + 0.35, y: 2.1, w: w - 0.7, h: 0.85, fontSize: 40, bold: true, color: i === 1 ? HX.coral : HX.teal2, valign: "bottom" });
    txt(s, l, { x: x + 0.35, y: 3.05, w: w - 0.7, h: 0.95, fontSize: 13.5, color: HX.lightInk, valign: "top" });
  });
  box(s, MX, 4.5, CW, 1.6, HX.card, "como_validar");
  txt(s, "COMO COMEÇAR COM SEGURANÇA", { x: MX + 0.35, y: 4.7, w: CW - 0.7, h: 0.3, fontSize: 11, bold: true, charSpacing: 1.5, color: HX.teal2 });
  txt(s, "A estimativa é uma associação, não uma prova de causa. Por isso, a proposta é começar o SMS ampliado em " +
    "alguns bairros, manter os outros como comparação e acompanhar a diferença no próprio painel por quatro semanas " +
    "antes de expandir para toda a rede.", { x: MX + 0.35, y: 5.1, w: CW - 0.7, h: 1.1, fontSize: 15, color: "FFFFFF", valign: "top" });
  s.addNotes("Como calculamos: para cada faixa de espera, aplicamos às consultas sem SMS a diferença de falta entre " +
    "quem recebeu e quem não recebeu, e somamos. Somos honestos sobre o limite: é associação; daí a proposta de piloto.");
}


// ================================================================== 10. obrigado
secao("Encerramento");
{
  const s = pres.addSlide({ masterName: "Capa", sectionTitle: "Encerramento" });
  s.addImage({ path: path.join(__dirname, "ondas.png"), x: 0, y: 0, w: 13.333, h: 7.5, objectName: "ondas" });
  s.addText("Obrigado!", { x: 0.9, y: 2.0, w: 11.5, h: 1.2, fontSize: 60, bold: true, color: "FFFFFF", margin: 0,
    valign: "middle", isTextBox: true });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.9, y: 3.45, w: 0.83, h: 0.05, fill: { color: HX.coral },
    line: { color: HX.coral }, rectRadius: 0.02, objectName: "traco" });
  txt(s, "Perguntas?", { x: 0.9, y: 3.7, w: 11, h: 0.5, fontSize: 24, color: HX.lightInk });
  txt(s, "EQUIPE", { x: 0.9, y: 6.1, w: 3, h: 0.25, fontSize: 10, bold: true, charSpacing: 2, color: HX.teal2 });
  ID.equipe.forEach(([n, m], i) => {
    const x = 0.9 + i * 2.15;
    txt(s, n, { x, y: 6.45, w: 2.1, h: 0.25, fontSize: 11, bold: true, color: "FFFFFF" });
    txt(s, m, { x, y: 6.72, w: 2.1, h: 0.22, fontSize: 9, color: HX.lightInk, fontFace: "Courier New" });
  });
  s.addNotes("Antes deste slide, trocar para o navegador com o painel já aberto (http://localhost:8501) e fazer a " +
    "demonstração: 1) visão geral, 20,1% e o gráfico de antecedência; 2) clicar em '8 a 15 dias'; 3) escolher " +
    "Itararé na lateral; 4) descer até o diagnóstico e ler a recomendação do recorte. Depois, voltar aqui para as perguntas.");
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("ok", OUT);
})();
