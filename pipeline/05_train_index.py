"""05 - Modelo principal: indice de masculinidad percibida (0 = femenino, 1 = masculino).

  * Objetivo: indice calculado con los votos `perceived_*` (solo como objetivo, nunca como predictor).
  * Entrenamiento: solo perfumes con >= 1 voto de percepcion, ponderados por sqrt(min(votos, 100)).
  * Hiperparametros fijos (no se ajustan con el test). CV de 5 folds sobre train.
  * Evaluacion unica sobre el test, con perfumes de >= 10 votos (referencia), >= 30 y >= 100,
    contra el clasificador por etiqueta `gender` convertido a indice esperado.

Salidas: models/index_model.joblib, models/metadata.json (seccion index_model),
         reports/index_metrics.json, docs/figures/index_*.png
Uso: python pipeline/05_train_index.py
"""
import _bootstrap  # noqa: F401

import json
from datetime import datetime, timezone

import joblib
import matplotlib.pyplot as plt
import numpy as np
import sklearn
from scipy.stats import spearmanr
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import f1_score, mean_absolute_error, r2_score
from sklearn.model_selection import KFold

import plotting as pl
from perfume_gender import config
from perfume_gender.features import rescale_to_max, vectorize
from perfume_gender.modeling import load_dataset, update_metadata
from perfume_gender.perception import ZONE_LIMITS, vote_weight, zone

N_REFERENCIA = 10
N_SENSIBILIDAD = (10, 30, 100)
ZONE_LABELS = ["female", "unisex", "male"]

# Composicion de prueba (caso real del usuario): perfil "masculino" que el clasificador manda a unisex.
COMPOSICION = {"alcohol": 9, "cannabis": 15, "chocolate": 16, "woody": 84,
               "aldehydic": 5, "leather": 75, "smoky": 61}


def nuevo_regresor(seed: int = config.SEED) -> HistGradientBoostingRegressor:
    return HistGradientBoostingRegressor(
        max_iter=300, learning_rate=0.08, max_leaf_nodes=31, min_samples_leaf=40,
        early_stopping=True, validation_fraction=0.1, n_iter_no_change=20, random_state=seed)


def metricas(real, pred, zonas_pred=None) -> dict:
    """MAE, R2, Spearman y acierto por zonas (F1 macro y exactitud)."""
    zr = zone(real)
    zp = zone(pred) if zonas_pred is None else zonas_pred
    return {
        "mae": round(float(mean_absolute_error(real, pred)), 4),
        "r2": round(float(r2_score(real, pred)), 4),
        "spearman": round(float(spearmanr(real, pred).statistic), 4),
        "zonas_f1_macro": round(float(f1_score(zr, zp, average="macro")), 4),
        "zonas_exactitud": round(float((zr == zp).mean()), 4),
    }


def curva(real, pred, bins: int = 10):
    """Indice real medio por decil de la prediccion (grafico de calibracion)."""
    edges = np.quantile(pred, np.linspace(0, 1, bins + 1))
    ids = np.clip(np.digitize(pred, edges[1:-1]), 0, bins - 1)
    return (np.array([pred[ids == b].mean() for b in range(bins)]),
            np.array([real[ids == b].mean() for b in range(bins)]))


def main() -> None:
    pl.setup()
    df, X, vocab = load_dataset()
    clasificador = joblib.load(config.MODEL_PATH)
    clases = [str(c) for c in clasificador.classes_]
    proba = clasificador.predict_proba(X)

    votos = df["perc_votes"].values
    indice = df["perc_index"].values
    es_train = (df["split"] == "train").values
    es_test = ~es_train

    # ---- Entrenamiento: perfumes de train con >= 1 voto de percepcion, ponderados ----
    tr = es_train & (votos >= 1)
    X_tr, y_tr, w_tr = X[tr], indice[tr], vote_weight(votos[tr])
    print(f"Train del regresor: {tr.sum():,} de {es_train.sum():,} filas de train "
          f"({tr.sum() / es_train.sum():.1%}) con >= 1 voto de percepcion")

    # ---- Validacion cruzada (5 folds) dentro del train; se puntua en filas con >= 10 votos ----
    cv_mae, cv_sp = [], []
    for k, (a, b) in enumerate(KFold(config.CV_FOLDS, shuffle=True, random_state=config.SEED).split(X_tr)):
        m = nuevo_regresor().fit(X_tr[a], y_tr[a], sample_weight=w_tr[a])
        fiable = votos[tr][b] >= N_REFERENCIA
        p = np.clip(m.predict(X_tr[b][fiable]), 0, 1)
        cv_mae.append(mean_absolute_error(y_tr[b][fiable], p))
        cv_sp.append(spearmanr(y_tr[b][fiable], p).statistic)
        print(f"  fold {k + 1}: MAE={cv_mae[-1]:.4f} Spearman={cv_sp[-1]:.4f}")
    out: dict = {
        "entrenamiento": {
            "filas_train_regresor": int(tr.sum()), "filas_train_total": int(es_train.sum()),
            "fraccion": round(float(tr.sum() / es_train.sum()), 4),
            "peso": "sqrt(min(votos_percepcion, 100))",
            "hiperparametros": nuevo_regresor().get_params() | {"random_state": config.SEED},
        },
        "cv": {"n_minimo_votos_validacion": N_REFERENCIA,
               "mae_media": round(float(np.mean(cv_mae)), 4), "mae_std": round(float(np.std(cv_mae)), 4),
               "spearman_media": round(float(np.mean(cv_sp)), 4), "spearman_std": round(float(np.std(cv_sp)), 4)},
        "zonas": {"limites": list(ZONE_LIMITS)},
        "resultados": {},
    }

    modelo = nuevo_regresor().fit(X_tr, y_tr, sample_weight=w_tr)

    # ---- Evaluacion unica en test: A (clasificador actual) vs B (regresor) ----
    curvas, zonas_ref = {}, None
    for n in N_SENSIBILIDAD:
        te = es_test & (votos >= n)
        trn = es_train & (votos >= n)
        y_te = indice[te]
        # A: indice esperado = sum(p_clase * indice medio de la clase en train)
        m_clase = np.array([indice[trn & (df["gender"] == c).values].mean() for c in clases])
        pred_a = proba[te] @ m_clase
        argmax_a = np.array(clases)[proba[te].argmax(axis=1)]
        pred_b = np.clip(modelo.predict(X[te]), 0, 1)
        res = {
            "n_test": int(te.sum()),
            "indice_medio_por_clase": {c: round(float(m), 3) for c, m in zip(clases, m_clase)},
            "A_clasificador_umbral": metricas(y_te, pred_a),
            "A_clasificador_argmax": metricas(y_te, pred_a, zonas_pred=argmax_a),
            "B_indice": metricas(y_te, pred_b),
        }
        a_mae, b_mae = res["A_clasificador_umbral"]["mae"], res["B_indice"]["mae"]
        res["mejora_mae_pct"] = round(100 * (a_mae - b_mae) / a_mae, 1)
        res["spearman_b_no_peor"] = bool(res["B_indice"]["spearman"] >= res["A_clasificador_umbral"]["spearman"])
        out["resultados"][f"N{n}"] = res
        curvas[n] = (curva(y_te, pred_a), curva(y_te, pred_b))
        if n == N_REFERENCIA:
            zonas_ref = (zone(y_te), zone(pred_b))
        print(f"N>={n}: test={te.sum():,}  MAE A={a_mae} B={b_mae} ({res['mejora_mae_pct']}%)  "
              f"Spearman A={res['A_clasificador_umbral']['spearman']} B={res['B_indice']['spearman']}  "
              f"F1 zonas A={res['A_clasificador_argmax']['zonas_f1_macro']} B={res['B_indice']['zonas_f1_macro']}")

    r = out["resultados"]
    criterios = {
        "mae_10pct_menor_en_N10": r[f"N{N_REFERENCIA}"]["mejora_mae_pct"] >= 10,
        "spearman_no_peor_en_N10": r[f"N{N_REFERENCIA}"]["spearman_b_no_peor"],
        "zonas_f1_macro_065_en_N10": r[f"N{N_REFERENCIA}"]["B_indice"]["zonas_f1_macro"] >= 0.65,
        "mismo_patron_en_N30_y_N100": all(
            r[k]["mejora_mae_pct"] >= 10 and r[k]["spearman_b_no_peor"] for k in ("N30", "N100")),
    }
    out["criterios"] = criterios
    print("Criterios:", criterios)

    # ---- Caso de prueba: composicion del usuario ----
    limpia = {k: float(v) for k, v in COMPOSICION.items()}
    x = vectorize(rescale_to_max(limpia), vocab).reshape(1, -1)
    p = clasificador.predict_proba(x)[0]
    m_ref = np.array([indice[es_train & (votos >= N_REFERENCIA) & (df["gender"] == c).values].mean() for c in clases])
    b = float(np.clip(modelo.predict(x)[0], 0, 1))
    out["caso_prueba"] = {
        "acordes": COMPOSICION,
        "A_probabilidades": {c: round(float(v), 3) for c, v in zip(clases, p)},
        "A_indice_esperado": round(float(p @ m_ref), 3),
        "B_indice": round(b, 3), "B_zona": str(zone(b)),
    }
    print("Caso de prueba:", json.dumps(out["caso_prueba"], ensure_ascii=False))

    # ---- Figuras ----
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.6))
    for ax, n in zip(axes, (N_REFERENCIA, 30)):
        (pa, ra), (pb, rb) = curvas[n]
        ax.plot([0, 1], [0, 1], "--", color=pl.NEUTRAL, lw=1, label="Ideal")
        ax.plot(pa, ra, "o-", color=pl.NEUTRAL, label="A: clasificador (índice esperado)")
        ax.plot(pb, rb, "o-", color=pl.GENDER_COLORS["female"], label="B: modelo de índice")
        ax.set_xlabel("Índice predicho (media por decil)")
        ax.set_ylabel("Índice real medio")
        ax.set_title(f"Calibración, ≥ {n} votos de percepción")
        ax.legend(frameon=False, fontsize=8)
    pl.save(fig, config.FIGURES_DIR / "index_calibracion.png")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    ns = [f"N{n}" for n in N_SENSIBILIDAD]
    xp = np.arange(len(ns))
    for ax, clave, titulo in ((axes[0], "mae", "Error medio absoluto (menor es mejor)"),
                              (axes[1], "spearman", "Correlación de Spearman (mayor es mejor)")):
        ax.bar(xp - 0.2, [r[k]["A_clasificador_umbral"][clave] for k in ns], 0.4, color=pl.NEUTRAL, label="A: clasificador")
        ax.bar(xp + 0.2, [r[k]["B_indice"][clave] for k in ns], 0.4, color=pl.GENDER_COLORS["female"], label="B: índice")
        ax.set_xticks(xp, [f"≥ {n} votos" for n in N_SENSIBILIDAD])
        ax.set_title(titulo)
        ax.legend(frameon=False)
    pl.save(fig, config.FIGURES_DIR / "index_metricas.png")

    zr, zp = zonas_ref
    cm = np.array([[int(((zr == a) & (zp == b_)).sum()) for b_ in ZONE_LABELS] for a in ZONE_LABELS])
    cmn = cm / cm.sum(axis=1, keepdims=True)
    nombres = [config.CLASS_LABELS_ES[z] for z in ZONE_LABELS]
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cmn, cmap="Purples", vmin=0, vmax=1)
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{cmn[i, j]:.0%}\n({cm[i, j]:,})", ha="center", va="center",
                    color="white" if cmn[i, j] > 0.5 else "black", fontsize=10)
    ax.set_xticks(range(3), nombres)
    ax.set_yticks(range(3), nombres)
    ax.set_xlabel("Zona predicha")
    ax.set_ylabel("Zona real (según votos)")
    ax.set_title(f"Zonas del índice (test, ≥ {N_REFERENCIA} votos)")
    ax.grid(False)
    fig.colorbar(im, ax=ax, shrink=0.8)
    pl.save(fig, config.FIGURES_DIR / "index_zonas.png")
    out["zonas"]["matriz_N10"] = {"labels": ZONE_LABELS, "matriz": cm.tolist()}

    # ---- Artefactos ----
    joblib.dump(modelo, config.INDEX_MODEL_PATH, compress=3)
    update_metadata(index_model={
        "model_class": type(modelo).__name__,
        "target": "indice de masculinidad percibida (0 femenino - 1 masculino)",
        "n_train": int(tr.sum()),
        "zone_limits": list(ZONE_LIMITS),
        "metrics_test_N10": r[f"N{N_REFERENCIA}"]["B_indice"],
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sklearn_version": sklearn.__version__,
        "model_size_mb": round(config.INDEX_MODEL_PATH.stat().st_size / 1e6, 2),
    })
    (config.REPORTS_DIR / "index_metrics.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Listo: {config.INDEX_MODEL_PATH.name} y reports/index_metrics.json")


if __name__ == "__main__":
    main()
