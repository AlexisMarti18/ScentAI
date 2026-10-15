"use strict";

const CLASS_ES = { female: "Femenino", male: "Masculino", unisex: "Unisex" };
const CLASS_COLOR = { female: "var(--female)", male: "var(--male)", unisex: "var(--unisex)" };
const CLASS_ORDER = ["female", "male", "unisex"];
const ZONE_TEXT = {
  female: "Tiende a femenino",
  unisex: "Zona intermedia (unisex)",
  male: "Tiende a masculino",
};

const PRESETS = {
  "Fresco aromático": { aromatic: 100, "fresh spicy": 80, citrus: 65, lavender: 50, woody: 40 },
  "Floral dulce": { "white floral": 100, sweet: 75, fruity: 65, powdery: 50, vanilla: 40 },
  "Amaderado ahumado": { woody: 100, leather: 89, smoky: 73, amber: 40, "warm spicy": 30 },
};

const state = { vocab: [], max: 8, selected: new Map(), filter: "", timer: null, seq: 0 };

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

const fmt = (x, d = 2) => x.toLocaleString("es-AR", { minimumFractionDigits: d, maximumFractionDigits: d });
const pct = (x, d = 1) => fmt(x * 100, d) + "%";
const nEs = (n) => n.toLocaleString("es-AR");

function showBanner(msg) {
  const b = $("banner");
  b.textContent = msg;
  b.hidden = !msg;
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

/* ------------------------------------------------------------------ tabs */
document.querySelectorAll(".tab").forEach((btn) =>
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((b) => {
      const on = b === btn;
      b.classList.toggle("active", on);
      b.setAttribute("aria-selected", String(on));
    });
    document.querySelectorAll(".pane").forEach((p) => p.classList.toggle("active", p.id === "tab-" + btn.dataset.tab));
  })
);

/* --------------------------------------------------------- accord picking */
function renderChips() {
  const box = $("chips");
  box.replaceChildren();
  const full = state.selected.size >= state.max;
  const q = state.filter.trim().toLowerCase();
  const list = state.vocab.filter((a) => !q || a.includes(q));
  if (!list.length) box.append(el("p", { class: "empty", text: "Sin resultados." }));
  for (const name of list) {
    const on = state.selected.has(name);
    box.append(el("button", {
      class: "chip", type: "button", text: name, "aria-pressed": String(on),
      ...(full && !on ? { disabled: "" } : {}),
      onclick: () => toggle(name),
    }));
  }
}

function toggle(name, intensity = 70) {
  if (state.selected.has(name)) state.selected.delete(name);
  else if (state.selected.size < state.max) state.selected.set(name, intensity);
  changed();
}

function renderSelected() {
  const box = $("selected");
  box.replaceChildren();
  for (const [name, value] of state.selected) {
    const val = el("span", { class: "val", text: String(value) });
    const slider = el("input", {
      type: "range", min: "1", max: "100", value: String(value), "aria-label": `Intensidad de ${name}`,
      oninput: (e) => {
        state.selected.set(name, Number(e.target.value));
        val.textContent = e.target.value;
        schedulePredict();
      },
    });
    box.append(el("div", { class: "row" },
      el("span", { class: "name", text: name, title: name }), slider, val,
      el("button", { class: "rm", type: "button", "aria-label": `Quitar ${name}`, text: "×", onclick: () => toggle(name) })));
  }
  $("selected-empty").hidden = state.selected.size > 0;
  $("clear").hidden = state.selected.size === 0;
  $("counter").textContent = `${state.selected.size} / ${state.max}`;
}

function changed() {
  renderChips();
  renderSelected();
  schedulePredict();
}

function applyPreset(preset) {
  state.selected = new Map(Object.entries(preset).filter(([k]) => state.vocab.includes(k)).slice(0, state.max));
  changed();
}

/* ------------------------------------------------------------- prediction */
function schedulePredict() {
  clearTimeout(state.timer);
  state.timer = setTimeout(predict, 180);
}

async function predict() {
  if (!state.selected.size) {
    $("result").hidden = true;
    $("result-empty").hidden = false;
    return;
  }
  const seq = ++state.seq;
  const body = { accords: [...state.selected].map(([name, intensity]) => ({ name, intensity })) };
  try {
    const data = await api("/api/predict", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
    });
    if (seq !== state.seq) return; // llego una respuesta mas nueva
    showBanner("");
    renderResult(data);
  } catch (err) {
    showBanner("No se pudo predecir: " + err.message);
  }
}

function renderResult(data) {
  $("result-empty").hidden = true;
  $("result").hidden = false;

  // Posicion en el espectro
  const z = data.zone;
  $("verdict").textContent = ZONE_TEXT[z];
  $("verdict").style.color = CLASS_COLOR[z];
  $("verdict-sub").textContent = `Índice ${fmt(data.index)} (0 = femenino, 1 = masculino).`;
  $("marker").style.left = (data.index * 100).toFixed(1) + "%";
  $("spectrum").setAttribute("aria-label", `Índice ${fmt(data.index)}: ${ZONE_TEXT[z]}`);

  // Femenino vs masculino (ignora unisex)
  const mf = data.male_vs_female;
  const duel = $("duel");
  duel.replaceChildren();
  const fem = el("div");
  const mas = el("div");
  fem.style.cssText = `width:${(mf.female * 100).toFixed(1)}%;background:var(--female)`;
  mas.style.cssText = `width:${(mf.male * 100).toFixed(1)}%;background:var(--male)`;
  duel.append(
    el("div", { class: "duel-bar", role: "img", "aria-label": `Femenino ${pct(mf.female, 0)}, masculino ${pct(mf.male, 0)}` }, fem, mas),
    el("div", { class: "duel-labels" },
      el("span", { text: `Femenino ${pct(mf.female, 0)}`, style: "color:var(--female)" }),
      el("span", { text: `Masculino ${pct(mf.male, 0)}`, style: "color:var(--male)" })));

  // Probabilidades por etiqueta y frecuencia base (lift)
  const probs = data.class_probabilities;
  const bars = $("bars");
  bars.replaceChildren();
  for (const c of CLASS_ORDER) {
    const fill = el("div", { class: "fill" });
    fill.style.width = ((probs[c] ?? 0) * 100).toFixed(1) + "%";
    fill.style.background = CLASS_COLOR[c];
    bars.append(el("div", { class: "bar-row" },
      el("span", { text: CLASS_ES[c] }),
      el("div", { class: "track", role: "img", "aria-label": `${CLASS_ES[c]} ${pct(probs[c] ?? 0, 0)}` }, fill),
      el("span", { class: "pct" }, `${pct(probs[c] ?? 0, 0)} `, el("small", { text: `×${fmt(data.lift[c] ?? 0, 1)}` }))));
  }

  // Influencia de cada acorde sobre el indice
  const list = $("influences");
  list.replaceChildren();
  for (const inf of data.influences.slice(0, 8)) {
    const pts = Math.round(inf.index_effect * 100);
    const neutral = inf.pushes_toward === "neutral";
    list.append(el("li", {},
      el("span", { class: "acc", text: inf.accord }),
      el("span", { class: "tag" },
        el("b", { text: neutral ? "Neutro" : CLASS_ES[inf.pushes_toward], style: `color:${neutral ? "var(--muted)" : CLASS_COLOR[inf.pushes_toward]}` }),
        ` ${pts > 0 ? "+" : ""}${pts} pts`)));
  }
}

/* ------------------------------------------------------------ model tab */
function cell(text, cls = "") { return el("td", { class: cls, text: String(text) }); }
function head(cols) {
  return el("tr", {}, ...cols.map((c, i) => el("th", { class: i ? "num" : "", text: c })));
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
    for (const [num, lbl] of [
      [fmt(r10.B_indice.mae, 3), "Error medio (índice 0-1)"],
      [fmt(r10.B_indice.spearman, 3), "Correlación de Spearman"],
      [pct(r10.B_indice.zonas_f1_macro), "F1 macro por zonas"],
      [`−${fmt(r10.mejora_mae_pct, 1)} %`, "Error vs. clasificador"],
    ]) tiles.append(el("div", { class: "tile" }, el("div", { class: "num", text: num }), el("div", { class: "lbl", text: lbl })));

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
async function init() {
  $("search").addEventListener("input", (e) => { state.filter = e.target.value; renderChips(); });
  $("clear").addEventListener("click", () => { state.selected.clear(); changed(); });
  for (const [label, preset] of Object.entries(PRESETS)) {
    $("presets").append(el("button", { class: "preset", type: "button", text: label, onclick: () => applyPreset(preset) }));
  }
  renderSelected();

  try {
    const data = await api("/api/accords");
    state.vocab = data.accords;
    state.max = data.max_accords;
    $("max-accords").textContent = state.max;
    renderChips();
    renderSelected();
  } catch (err) {
    showBanner("No se pudo cargar el modelo: " + err.message);
    return;
  }
  try {
    renderModel(await api("/api/model/info"));
  } catch (err) {
    $("model-summary").textContent = "No se pudo cargar la información del modelo.";
  }
}

init();
