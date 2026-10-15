"use strict";

const CLASS_ES = { female: "Femenino", male: "Masculino", unisex: "Unisex" };
const CLASS_COLOR = { female: "var(--female)", male: "var(--male)", unisex: "var(--unisex)" };
const CLASS_ORDER = ["female", "male", "unisex"];

const PRESETS = {
  "Fresco aromático": { aromatic: 100, "fresh spicy": 80, citrus: 65, lavender: 50, woody: 40 },
  "Floral dulce": { "white floral": 100, sweet: 75, fruity: 65, powdery: 50, vanilla: 40 },
  "Amaderado cálido": { woody: 100, "warm spicy": 80, amber: 65, leather: 45, vanilla: 30 },
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

const pct = (x, d = 1) => (x * 100).toFixed(d) + "%";

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

  const probs = data.probabilities;
  const top = data.label;
  const topP = probs[top];
  $("verdict").textContent = CLASS_ES[top];
  $("verdict").style.color = CLASS_COLOR[top];
  $("verdict-sub").textContent = topP < 0.5
    ? `Tendencia poco marcada (${pct(topP, 0)}): el perfil es ambiguo.`
    : `Probabilidad estimada: ${pct(topP, 0)}.`;

  const bars = $("bars");
  bars.replaceChildren();
  for (const c of CLASS_ORDER) {
    const fill = el("div", { class: "fill" });
    fill.style.width = pct(probs[c] ?? 0, 1);
    fill.style.background = CLASS_COLOR[c];
    bars.append(el("div", { class: "bar-row" },
      el("span", { text: CLASS_ES[c] }),
      el("div", { class: "track", role: "img", "aria-label": `${CLASS_ES[c]} ${pct(probs[c] ?? 0, 0)}` }, fill),
      el("span", { class: "pct", text: pct(probs[c] ?? 0, 0) })));
  }

  const list = $("influences");
  list.replaceChildren();
  for (const inf of data.influences.slice(0, 8)) {
    const c = inf.pushes_toward;
    const pp = Math.round(inf.effect[c] * 100);
    list.append(el("li", {},
      el("span", { class: "acc", text: inf.accord }),
      el("span", { class: "tag" },
        el("b", { text: CLASS_ES[c], style: `color:${CLASS_COLOR[c]}` }),
        ` ${pp >= 0 ? "+" : ""}${pp} pp`)));
  }
}

/* ------------------------------------------------------------ model tab */
function cell(text, cls = "") { return el("td", { class: cls, text: String(text) }); }
function head(cols) {
  return el("tr", {}, ...cols.map((c, i) => el("th", { class: i ? "num" : "", text: c })));
}

function renderModel(info) {
  const meta = info.metadata, m = info.metrics, test = m?.test;
  $("model-summary").textContent =
    `${meta.model_name} · ${meta.n_features} acordes · entrenado con ${meta.n_train.toLocaleString("es-AR")} perfumes ` +
    `y evaluado en ${meta.n_test.toLocaleString("es-AR")} perfumes que nunca vio.`;

  const tiles = $("tiles");
  tiles.replaceChildren();
  const mt = meta.metrics_test;
  for (const [num, lbl] of [
    [pct(mt.accuracy), "Exactitud (test)"],
    [pct(mt.macro_f1), "F1 macro (test)"],
    [pct(mt.baseline_accuracy), "Baseline: siempre 'unisex'"],
  ]) tiles.append(el("div", { class: "tile" }, el("div", { class: "num", text: num }), el("div", { class: "lbl", text: lbl })));

  if (m?.cv) {
    const t = $("cv-table");
    t.tHead.replaceChildren(head(["Modelo", "F1 macro", "Exactitud"]));
    t.tBodies[0].replaceChildren();
    for (const [name, r] of Object.entries(m.cv)) {
      const best = name === m.winner;
      const tr = el("tr", best ? { class: "best" } : {},
        el("td", { text: name + (r.note ? ` (${r.note})` : "") }),
        cell(`${pct(r.macro_f1_mean)} ± ${pct(r.macro_f1_std)}`, "num"),
        cell(pct(r.accuracy_mean), "num"));
      t.tBodies[0].append(tr);
    }
  }

  if (test) {
    const cm = $("cm-table");
    cm.className = "cm";
    cm.replaceChildren(head(["Real \\ Predicho", ...test.confusion_matrix.labels.map((l) => CLASS_ES[l])]));
    test.confusion_matrix.matrix.forEach((row, i) => {
      cm.append(el("tr", {}, cell(CLASS_ES[test.confusion_matrix.labels[i]]),
        ...row.map((v, j) => cell(v.toLocaleString("es-AR"), "num" + (i === j ? " diag" : "")))));
    });

    const ct = $("class-table");
    ct.replaceChildren(head(["Clase", "Precisión", "Recall", "F1", "Perfumes"]));
    for (const c of CLASS_ORDER) {
      const r = test.per_class[c];
      if (!r) continue;
      ct.append(el("tr", {}, cell(CLASS_ES[c]), cell(pct(r.precision), "num"), cell(pct(r.recall), "num"),
        cell(pct(r["f1-score"]), "num"), cell(r.support.toLocaleString("es-AR"), "num")));
    }
  }

  const exp = info.experiments;
  if (exp) {
    const t = $("exp-table");
    t.replaceChildren(head(["Variante de features", "F1 macro", "Exactitud"]));
    const names = { solo_acordes: "Solo acordes (lo que usa la app)", acordes_mas_notas: "Acordes + notas", solo_notas: "Solo notas" };
    for (const [k, label] of Object.entries(names)) {
      const r = exp.E1_features?.[k];
      if (r) t.append(el("tr", {}, cell(label), cell(pct(r.macro_f1), "num"), cell(pct(r.accuracy), "num")));
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
