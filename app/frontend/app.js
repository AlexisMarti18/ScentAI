"use strict";

const CLASS_ES = { female: "Femenino", male: "Masculino", unisex: "Unisex" };
const CLASS_COLOR = { female: "var(--female)", male: "var(--male)", unisex: "var(--unisex)" };
const CLASS_TEXT = { female: "var(--female-t)", male: "var(--male-t)", unisex: "var(--unisex-t)" };
const CLASS_ORDER = ["female", "male", "unisex"];
const ZONES = ["female", "unisex", "male"];
const ZONE_TEXT = {
  female: "Tiende a femenino",
  unisex: "Zona intermedia (unisex)",
  male: "Tiende a masculino",
};
const ZONE_ADJ = { female: "femenina", unisex: "unisex", male: "masculina" };
// Espejo de ZONE_LIMITS en perfume_gender/perception.py (solo para avisar que el índice está cerca de un borde).
const ZONE_LIMITS = [0.33, 0.67];
const NEAR_LIMIT = 0.04;

const PRESETS = {
  "Fresco aromático": { aromatic: 100, "fresh spicy": 80, citrus: 65, lavender: 50, woody: 40 },
  "Floral dulce": { "white floral": 100, sweet: 75, fruity: 65, powdery: 50, vanilla: 40 },
  "Amaderado ahumado": { woody: 100, leather: 89, smoky: 73, amber: 40, "warm spicy": 30 },
};

const ICONS = {
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/>',
  moon: '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
  x: '<path d="M18 6 6 18M6 6l12 12"/>',
  check: '<path d="M20 6 9 17l-5-5"/>',
  alert: '<circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/>',
  info: '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>',
  sliders: '<path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6"/>',
  "chevron-up": '<path d="m18 15-6-6-6 6"/>',
};

const state = {
  vocab: [], max: 8, selected: new Map(), filter: "", timer: null, seq: 0,
  chipEls: new Map(), rows: new Map(), presetEls: new Map(), hasResult: false, summaryVisible: true, lastZone: null,
};
const dom = {}; // nodos del resultado que se crean una sola vez y luego solo se actualizan

const $ = (id) => document.getElementById(id);

function el(tag, props = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (k === "text") node.textContent = v;
    else if (k === "class") node.className = v;
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v);
  }
  for (const c of children) node.append(c);
  return node;
}

function icon(name) {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "0 0 24 24");
  svg.setAttribute("aria-hidden", "true");
  svg.innerHTML = ICONS[name]; // constante propia, no hay datos externos
  return svg;
}

const fmt = (x, d = 2) => x.toLocaleString("es-AR", { minimumFractionDigits: d, maximumFractionDigits: d });
const pct = (x, d = 1) => fmt(x * 100, d) + "%";
const nEs = (n) => n.toLocaleString("es-AR");
const announce = (msg) => { $("sr-status").textContent = msg; };

function showBanner(msg) {
  $("banner-text").textContent = msg;
  $("banner").hidden = !msg;
}

async function api(path, options) {
  const res = await fetch(path, options);
  if (!res.ok) {
    let detail = `Error ${res.status}`;
    try { detail = (await res.json()).detail || detail; } catch (_) { /* sin cuerpo JSON */ }
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return res.json();
}

/* ------------------------------------------------------------------ tema */
function storedTheme() {
  try { return localStorage.getItem("scentai-theme"); } catch (_) { return null; }
}

function applyTheme(theme, persist = false) {
  document.documentElement.dataset.theme = theme;
  const btn = $("theme-toggle");
  btn.setAttribute("aria-label", theme === "dark" ? "Cambiar a tema claro" : "Cambiar a tema oscuro");
  btn.firstElementChild.replaceChildren(icon(theme === "dark" ? "sun" : "moon"));
  document.querySelector('meta[name="theme-color"]').setAttribute("content", theme === "dark" ? "#0f0d12" : "#f6f1ea");
  if (persist) { try { localStorage.setItem("scentai-theme", theme); } catch (_) { /* almacenamiento bloqueado */ } }
}

function initTheme() {
  applyTheme(document.documentElement.dataset.theme);
  $("theme-toggle").addEventListener("click", () =>
    applyTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark", true));
  // Sin preferencia guardada, acompaña al sistema operativo.
  matchMedia("(prefers-color-scheme: light)").addEventListener("change", (e) => {
    if (!storedTheme()) applyTheme(e.matches ? "light" : "dark");
  });
}

/* ------------------------------------------------------------------ tabs */
const TAB_HASH = { predict: "", model: "#modelo" };

function selectTab(btn, { focus = false } = {}) {
  document.querySelectorAll(".tab").forEach((b) => {
    const on = b === btn;
    b.setAttribute("aria-selected", String(on));
    b.tabIndex = on ? 0 : -1;
  });
  document.querySelectorAll(".pane").forEach((p) => p.classList.toggle("active", p.id === "tab-" + btn.dataset.tab));
  history.replaceState(null, "", TAB_HASH[btn.dataset.tab] || location.pathname + location.search);
  window.scrollTo(0, 0);
  if (focus) btn.focus();
}

function initTabs() {
  const tabs = [...document.querySelectorAll(".tab")];
  tabs.forEach((btn, i) => {
    btn.addEventListener("click", () => selectTab(btn));
    btn.addEventListener("keydown", (e) => {
      const next = { ArrowRight: (i + 1) % tabs.length, ArrowLeft: (i - 1 + tabs.length) % tabs.length, Home: 0, End: tabs.length - 1 }[e.key];
      if (next === undefined) return;
      e.preventDefault();
      selectTab(tabs[next], { focus: true });
    });
  });
  if (location.hash === TAB_HASH.model) selectTab(tabs.find((b) => b.dataset.tab === "model"));
}

/* --------------------------------------------------------- accord picking */
function skeletonChips() {
  const box = $("chips");
  box.setAttribute("aria-busy", "true");
  for (let i = 0; i < 20; i++) box.append(el("span", { class: "chip skeleton", "aria-hidden": "true", style: `width:${56 + ((i * 17) % 52)}px` }));
}

function buildChips() {
  const box = $("chips");
  box.replaceChildren();
  box.removeAttribute("aria-busy");
  state.chipEls.clear();
  for (const name of state.vocab) {
    const chip = el("button", { class: "chip", type: "button", "aria-pressed": "false", onclick: () => toggle(name) },
      el("span", { text: name }));
    state.chipEls.set(name, chip);
    box.append(chip);
  }
  box.append(el("p", { class: "empty", id: "chips-empty", text: "Sin resultados. Probá con otra palabra.", hidden: "" }));
}

// Se actualizan los botones existentes (no se recrean) para no perder el foco del teclado.
function updateChips() {
  if (!state.chipEls.size) return; // el vocabulario todavía no llegó
  const q = state.filter.trim().toLowerCase();
  const full = state.selected.size >= state.max;
  let shown = 0;
  for (const [name, chip] of state.chipEls) {
    const on = state.selected.has(name);
    const match = !q || name.includes(q);
    chip.hidden = !match;
    if (match) shown++;
    chip.setAttribute("aria-pressed", String(on));
    chip.disabled = full && !on;
    const mark = chip.querySelector("svg");
    if (on && !mark) chip.prepend(icon("check"));
    else if (!on && mark) mark.remove();
  }
  $("chips-empty").hidden = shown > 0 || !state.chipEls.size;
  $("chips-status").textContent = full
    ? `Llegaste al máximo de ${state.max} acordes. Quitá uno para agregar otro.`
    : q ? `${shown} de ${state.vocab.length} acordes` : `${state.vocab.length} acordes disponibles`;
}

function toggle(name, intensity = 70) {
  if (state.selected.has(name)) state.selected.delete(name);
  else if (state.selected.size < state.max) state.selected.set(name, intensity);
  changed();
}

function removeAccord(name) {
  const names = [...state.selected.keys()];
  const at = names.indexOf(name);
  state.selected.delete(name);
  changed();
  const rest = [...state.selected.keys()];
  // El botón de quitar desaparece: el foco pasa al siguiente acorde o a la búsqueda.
  (rest.length ? state.rows.get(rest[Math.min(at, rest.length - 1)]).slider : $("search")).focus();
}

function setFill(slider) {
  slider.style.setProperty("--pct", ((slider.value - slider.min) / (slider.max - slider.min)) * 100 + "%");
}

function buildRow(name, value) {
  const val = el("span", { class: "val", text: String(value) });
  const slider = el("input", {
    type: "range", min: "1", max: "100", value: String(value), "aria-label": `Intensidad de ${name}`,
    oninput: (e) => {
      state.selected.set(name, Number(e.target.value));
      val.textContent = e.target.value;
      setFill(e.target);
      schedulePredict();
    },
  });
  setFill(slider);
  const rm = el("button", { class: "icon-btn icon-btn-sm rm", type: "button", "aria-label": `Quitar ${name}`, onclick: () => removeAccord(name) }, icon("x"));
  const node = el("div", { class: "row" }, el("span", { class: "name", text: name, title: name }), slider, val, rm);
  return { node, slider, val };
}

function renderSelected() {
  const box = $("selected");
  for (const [name, row] of state.rows) {
    if (!state.selected.has(name)) { row.node.remove(); state.rows.delete(name); }
  }
  let i = 0;
  for (const [name, value] of state.selected) {
    let row = state.rows.get(name);
    if (!row) { row = buildRow(name, value); state.rows.set(name, row); }
    else if (Number(row.slider.value) !== value) { // un ejemplo pisó la intensidad
      row.slider.value = String(value);
      row.val.textContent = String(value);
      setFill(row.slider);
    }
    if (box.children[i] !== row.node) box.insertBefore(row.node, box.children[i] ?? null);
    i++;
  }
  const n = state.selected.size;
  $("selected-empty").hidden = n > 0;
  $("clear").hidden = n === 0;
  $("counter").textContent = `${n} / ${state.max}`;
  $("counter").classList.toggle("full", n >= state.max);
}

function changed() {
  updateChips();
  renderSelected();
  updatePresets();
  schedulePredict();
}

const presetEntries = (preset) => Object.entries(preset).filter(([k]) => state.vocab.includes(k)).slice(0, state.max);

// Marca el ejemplo cuyo contenido coincide exactamente con la selección actual.
function updatePresets() {
  for (const [label, btn] of state.presetEls) {
    const entries = presetEntries(PRESETS[label]);
    const same = entries.length === state.selected.size && entries.every(([k, v]) => state.selected.get(k) === v);
    if (same) btn.setAttribute("aria-current", "true");
    else btn.removeAttribute("aria-current");
  }
}

function applyPreset(label) {
  state.selected = new Map(presetEntries(PRESETS[label]));
  changed();
  announce(`Ejemplo ${label} cargado.`);
}

/* ------------------------------------------------------------- prediction */
function schedulePredict() {
  clearTimeout(state.timer);
  state.timer = setTimeout(predict, 180);
}

async function predict() {
  if (!state.selected.size) {
    ++state.seq; // descarta respuestas en vuelo
    state.hasResult = false;
    state.lastZone = null;
    $("result").hidden = true;
    $("details").hidden = true;
    $("result-empty").hidden = false;
    updateMinibar();
    return;
  }
  const seq = ++state.seq;
  const body = { accords: [...state.selected].map(([name, intensity]) => ({ name, intensity })) };
  $("summary").setAttribute("aria-busy", "true");
  try {
    const data = await api("/api/predict", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
    });
    if (seq !== state.seq) return; // llego una respuesta mas nueva
    showBanner("");
    renderResult(data);
  } catch (err) {
    if (seq === state.seq) showBanner("No se pudo predecir: " + err.message);
  } finally {
    if (seq === state.seq) $("summary").removeAttribute("aria-busy");
  }
}

// Si el índice está pegado a un límite de zona, avisa cuál es la zona vecina.
function neighbourZone(index, zone) {
  for (let i = 0; i < ZONE_LIMITS.length; i++) {
    if (Math.abs(index - ZONE_LIMITS[i]) > NEAR_LIMIT) continue;
    if (zone === ZONES[i]) return ZONES[i + 1];
    if (zone === ZONES[i + 1]) return ZONES[i];
  }
  return null;
}

function buildResultDom() {
  const side = (label, valueEl, color) => {
    valueEl.style.color = color;
    return el("div", { class: "duel-side" }, el("small", { text: label }), valueEl);
  };
  dom.duelF = el("b");
  dom.duelM = el("b");
  dom.duelBarF = el("div");
  dom.duelBarM = el("div");
  dom.duelBarF.style.background = CLASS_COLOR.female;
  dom.duelBarM.style.background = CLASS_COLOR.male;
  dom.duelBar = el("div", { class: "duel-bar", role: "img" }, dom.duelBarF, dom.duelBarM);
  $("duel").append(
    el("div", { class: "duel-labels" }, side("Femenino", dom.duelF, CLASS_TEXT.female), side("Masculino", dom.duelM, CLASS_TEXT.male)),
    dom.duelBar);

  dom.bars = {};
  for (const c of CLASS_ORDER) {
    const fill = el("div", { class: "fill" });
    fill.style.background = CLASS_COLOR[c];
    fill.style.width = "0%";
    const track = el("div", { class: "track", role: "img" }, fill);
    const val = el("span");
    const lift = el("small");
    dom.bars[c] = { fill, track, val, lift };
    $("bars").append(el("div", { class: "bar-row" }, el("span", { text: CLASS_ES[c] }), track, el("span", { class: "pct" }, val, lift)));
  }
}

function renderResult(data) {
  if (!dom.bars) buildResultDom();
  $("result-empty").hidden = true;
  $("result").hidden = false;
  $("details").hidden = false;
  state.hasResult = true;

  // Posicion en el espectro
  const z = data.zone;
  const left = (data.index * 100).toFixed(1) + "%";
  $("result").dataset.zone = z;
  $("spectrum").dataset.zone = z;
  $("verdict").textContent = ZONE_TEXT[z];
  $("index-num").textContent = fmt(data.index);
  $("marker").style.left = left;
  $("spectrum").setAttribute("aria-label", `Índice ${fmt(data.index)} en una escala de 0 (femenino) a 1 (masculino): ${ZONE_TEXT[z]}`);
  const near = neighbourZone(data.index, z);
  $("verdict-sub").textContent = "El índice va de 0 (femenino) a 1 (masculino)." +
    (near ? ` Está cerca del límite con la zona ${ZONE_ADJ[near]}: un pequeño cambio de intensidad podría cambiar la lectura.` : "");
  if (z !== state.lastZone) announce(`${ZONE_TEXT[z]}. Índice ${fmt(data.index)}.`);
  state.lastZone = z;

  // Femenino vs masculino (ignora unisex)
  const mf = data.male_vs_female;
  dom.duelF.textContent = pct(mf.female, 0);
  dom.duelM.textContent = pct(mf.male, 0);
  dom.duelBarF.style.width = (mf.female * 100).toFixed(1) + "%";
  dom.duelBarM.style.width = (mf.male * 100).toFixed(1) + "%";
  dom.duelBar.setAttribute("aria-label", `Femenino ${pct(mf.female, 0)}, masculino ${pct(mf.male, 0)}`);

  // Probabilidades por etiqueta y frecuencia base (lift)
  for (const c of CLASS_ORDER) {
    const p = data.class_probabilities[c] ?? 0;
    const bar = dom.bars[c];
    bar.fill.style.width = (p * 100).toFixed(1) + "%";
    bar.track.setAttribute("aria-label", `${CLASS_ES[c]} ${pct(p, 0)}`);
    bar.val.textContent = pct(p, 0);
    bar.lift.textContent = `×${fmt(data.lift[c] ?? 0, 1)}`;
  }

  // Influencia de cada acorde sobre el indice: barras divergentes (izquierda femenino, derecha masculino)
  const list = $("influences");
  list.replaceChildren();
  const top = data.influences.slice(0, 8);
  const maxAbs = Math.max(0.01, ...top.map((i) => Math.abs(i.index_effect)));
  for (const inf of top) {
    const pts = Math.round(inf.index_effect * 100);
    const dir = inf.pushes_toward; // female | male | neutral
    const text = `${pts > 0 ? "+" : pts < 0 ? "−" : ""}${Math.abs(pts)} pts`;
    const meaning = dir === "neutral" ? "efecto neutro" : `empuja hacia ${CLASS_ES[dir].toLowerCase()}`;
    const bar = el("div", { class: `dbar ${dir}` });
    if (dir !== "neutral") bar.style.width = ((Math.abs(inf.index_effect) / maxAbs) * 50).toFixed(1) + "%";
    list.append(el("li", {},
      el("span", { class: "acc", text: inf.accord, title: inf.accord }),
      el("div", { class: "dtrack", role: "img", "aria-label": `${inf.accord}: ${meaning}, ${text}` }, bar),
      el("span", { class: `dval ${dir}`, text })));
  }

  // Barra flotante (movil)
  $("minibar-dot").style.background = CLASS_COLOR[z];
  $("minibar-verdict").textContent = ZONE_TEXT[z];
  $("minibar-index").textContent = fmt(data.index);
  $("minibar-marker").style.left = left;
  updateMinibar();
}

function updateMinibar() {
  const show = state.hasResult && !state.summaryVisible;
  $("minibar").hidden = !show;
  document.body.classList.toggle("has-minibar", show);
}

function initMinibar() {
  $("minibar").addEventListener("click", () => {
    const calm = matchMedia("(prefers-reduced-motion: reduce)").matches;
    $("summary").scrollIntoView({ behavior: calm ? "auto" : "smooth", block: "start" });
  });
  if (!("IntersectionObserver" in window)) return;
  new IntersectionObserver(([entry]) => {
    state.summaryVisible = entry.intersectionRatio >= 0.2;
    updateMinibar();
  }, { threshold: [0, 0.2, 1] }).observe($("summary"));
}

/* ------------------------------------------------------------ model tab */
function cell(text, cls = "") { return el("td", { class: cls, text: String(text) }); }
function head(cols) {
  return el("tr", {}, ...cols.map((c, i) => el("th", { class: i ? "num" : "", scope: "col", text: c })));
}

function renderModel(info) {
  const meta = info.metadata, idx = info.index_metrics, clf = info.classifier_metrics;

  if (idx) {
    const r10 = idx.resultados.N10;
    $("model-summary").textContent =
      `Gradient Boosting entrenado con ${nEs(meta.index_model.n_train)} perfumes que tienen votos de percepción ` +
      `(${pct(idx.entrenamiento.fraccion)} del train), ponderados por √votos.`;
    const tiles = $("tiles");
    tiles.replaceChildren();
    tiles.removeAttribute("aria-busy");
    for (const [num, lbl, desc] of [
      [fmt(r10.B_indice.mae, 3), "Error medio (índice 0-1)", "Cuánto se aleja en promedio del índice real."],
      [fmt(r10.B_indice.spearman, 3), "Correlación de Spearman", "Qué tan bien ordena los perfumes de femenino a masculino (1 = orden perfecto)."],
      [pct(r10.B_indice.zonas_f1_macro), "F1 macro por zonas", "Acierto al ubicar cada perfume en femenino, unisex o masculino."],
      [`−${fmt(r10.mejora_mae_pct, 1)} %`, "Error vs. clasificador", "Reducción del error frente a convertir la etiqueta de género en índice."],
    ]) tiles.append(el("div", { class: "tile" },
      el("div", { class: "num", text: num }), el("div", { class: "lbl", text: lbl }), el("div", { class: "desc", text: desc })));

    const t = $("cmp-table");
    t.replaceChildren(head(["Votos de percepción mínimos", "Perfumes test", "Error A → B", "Spearman A → B", "F1 zonas A → B"]));
    for (const k of ["N10", "N30", "N100"]) {
      const r = idx.resultados[k];
      t.append(el("tr", {}, cell("≥ " + k.slice(1)), cell(nEs(r.n_test), "num"),
        cell(`${fmt(r.A_clasificador_umbral.mae, 3)} → ${fmt(r.B_indice.mae, 3)}`, "num"),
        cell(`${fmt(r.A_clasificador_umbral.spearman, 3)} → ${fmt(r.B_indice.spearman, 3)}`, "num"),
        cell(`${fmt(r.A_clasificador_argmax.zonas_f1_macro, 2)} → ${fmt(r.B_indice.zonas_f1_macro, 2)}`, "num")));
    }
    $("cmp-hint").textContent =
      "A = clasificador por etiqueta convertido a índice; B = modelo de índice. Test de perfumes nunca vistos.";
  }

  if (info.vote_weights) {
    const t = $("weights-table");
    t.replaceChildren(head(["Esquema", "Error", "Spearman"]));
    for (const [name, r] of Object.entries(info.vote_weights.esquemas)) {
      t.append(el("tr", name.startsWith("pesos sqrt") ? { class: "best" } : {},
        cell(name), cell(fmt(r.mae, 4), "num"), cell(fmt(r.spearman, 3), "num")));
    }
  }

  const per = info.eda?.perception;
  if (per) {
    $("bias-text").textContent =
      `Entre los perfumes etiquetados "unisex" con ≥ 30 votos de percepción, ${fmt(per.unisex_percibido_masculino_pct, 1)} % caen en la zona ` +
      `masculina del índice, ${fmt(per.unisex_percibido_femenino_pct, 1)} % en la femenina y ${fmt(per.unisex_percibido_intermedio_pct, 1)} % en la intermedia.`;
  }
  const exp = info.experiments;
  if (exp) {
    const t = $("exp-table");
    t.replaceChildren(head(["Variables (clasificador)", "F1 macro", "Exactitud"]));
    const names = { solo_acordes: "Solo acordes (lo que usa la app)", acordes_mas_notas: "Acordes + notas", solo_notas: "Solo notas" };
    for (const [k, label] of Object.entries(names)) {
      const r = exp.E1_features?.[k];
      if (r) t.append(el("tr", {}, cell(label), cell(pct(r.macro_f1), "num"), cell(pct(r.accuracy), "num")));
    }
  }

  if (clf) {
    const mt = meta.classifier.metrics_test;
    $("clf-summary").textContent =
      `${meta.classifier.model_name}: exactitud ${pct(mt.accuracy)} (baseline ${pct(mt.baseline_accuracy)}), ` +
      `F1 macro ${pct(mt.macro_f1)}. Aporta las probabilidades por clase y la lectura femenino vs. masculino.`;
    const t = $("cv-table");
    t.tHead.replaceChildren(head(["Modelo (validación cruzada)", "F1 macro", "Exactitud"]));
    t.tBodies[0].replaceChildren();
    for (const [name, r] of Object.entries(clf.cv)) {
      t.tBodies[0].append(el("tr", name === clf.winner ? { class: "best" } : {},
        el("td", { text: name + (r.note ? ` (${r.note})` : "") }),
        cell(`${pct(r.macro_f1_mean)} ± ${pct(r.macro_f1_std)}`, "num"), cell(pct(r.accuracy_mean), "num")));
    }
    const test = clf.test;
    const cmt = $("cm-table");
    cmt.className = "cm";
    cmt.replaceChildren(head(["Real \\ Predicho", ...test.confusion_matrix.labels.map((l) => CLASS_ES[l])]));
    test.confusion_matrix.matrix.forEach((row, i) => {
      cmt.append(el("tr", {}, cell(CLASS_ES[test.confusion_matrix.labels[i]]),
        ...row.map((v, j) => cell(nEs(v), "num" + (i === j ? " diag" : "")))));
    });
    const ct = $("class-table");
    ct.replaceChildren(head(["Clase", "Precisión", "Recall", "F1", "Perfumes"]));
    for (const c of CLASS_ORDER) {
      const r = test.per_class[c];
      if (r) ct.append(el("tr", {}, cell(CLASS_ES[c]), cell(pct(r.precision), "num"), cell(pct(r.recall), "num"),
        cell(pct(r["f1-score"]), "num"), cell(nEs(r.support), "num")));
    }
  }
}

/* ---------------------------------------------------------------- init */
function initControls() {
  const search = $("search");
  search.addEventListener("input", (e) => {
    state.filter = e.target.value;
    $("search-clear").hidden = !state.filter;
    updateChips();
  });
  search.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && search.value) { search.value = ""; search.dispatchEvent(new Event("input")); }
  });
  $("search-clear").addEventListener("click", () => {
    search.value = "";
    search.dispatchEvent(new Event("input"));
    search.focus();
  });
  $("clear").addEventListener("click", () => { state.selected.clear(); changed(); search.focus(); announce("Se quitaron todos los acordes."); });
  $("banner-close").addEventListener("click", () => showBanner(""));

  const labels = Object.keys(PRESETS);
  for (const label of labels) {
    const btn = el("button", { class: "preset", type: "button", onclick: () => applyPreset(label) },
      el("span", { class: "preset-name", text: label }),
      el("span", { class: "preset-desc", text: Object.keys(PRESETS[label]).slice(0, 3).join(" · ") }));
    state.presetEls.set(label, btn);
    $("presets").append(btn);
  }
  $("try-example").addEventListener("click", () => applyPreset(labels[0]));
}

async function init() {
  document.querySelectorAll("[data-icon]").forEach((n) => n.replaceChildren(icon(n.dataset.icon)));
  initTheme();
  initTabs();
  initControls();
  initMinibar();
  skeletonChips();
  renderSelected();

  try {
    const data = await api("/api/accords");
    state.vocab = data.accords;
    state.max = data.max_accords;
    $("max-accords").textContent = state.max;
    buildChips();
    updateChips();
    renderSelected();
  } catch (err) {
    $("chips").replaceChildren(el("p", { class: "empty", text: "No se pudieron cargar los acordes." }));
    $("chips").removeAttribute("aria-busy");
    showBanner("No se pudo cargar el modelo: " + err.message);
    return;
  }
  try {
    renderModel(await api("/api/model/info"));
  } catch (err) {
    $("model-summary").textContent = "No se pudo cargar la información del modelo.";
    $("tiles").replaceChildren();
    $("tiles").removeAttribute("aria-busy");
  }
}

init();
