"""05 - Evaluacion del modelo final y figuras para el README.

Requiere haber corrido 02, 03 y 04. Genera docs/figures/model_*.png y reports/evaluation.json.
Uso: python pipeline/05_evaluate.py
"""
import _bootstrap  # noqa: F401

import json

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.calibration import calibration_curve
from sklearn.inspection import permutation_importance
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import GroupShuffleSplit

import plotting as pl
from perfume_gender import config
from perfume_gender.modeling import load_dataset


def main() -> None:
    pl.setup()
    df, X, vocab = load_dataset()
    metrics = json.loads((config.REPORTS_DIR / "metrics.json").read_text(encoding="utf-8"))
    exps = json.loads((config.REPORTS_DIR / "experiments.json").read_text(encoding="utf-8"))
    model = joblib.load(config.MODEL_PATH)
    classes = [str(c) for c in model.classes_]
    es = config.CLASS_LABELS_ES

    te = (df["split"] == "test").values
    Xte, yte = X[te], df.loc[te, "gender"].values
    proba = model.predict_proba(Xte)
    pred = np.array(classes)[proba.argmax(axis=1)]
    out: dict = {}

    # ---- 1. Matriz de confusión (conteos y % por fila) ----
    cm = np.array(metrics["test"]["confusion_matrix"]["matrix"])
    cmn = cm / cm.sum(axis=1, keepdims=True)
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cmn, cmap="Purples", vmin=0, vmax=1)
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{cmn[i, j]:.0%}\n({cm[i, j]:,})", ha="center", va="center",
                    color="white" if cmn[i, j] > 0.5 else "black", fontsize=10)
    ax.set_xticks(range(3), [es[c] for c in classes])
    ax.set_yticks(range(3), [es[c] for c in classes])
    ax.set_xlabel("Género predicho")
    ax.set_ylabel("Género real")
    ax.set_title("Matriz de confusión (test, % por fila)")
    ax.grid(False)
    fig.colorbar(im, ax=ax, shrink=0.8)
    pl.save(fig, config.FIGURES_DIR / "model_confusion.png")

    # ---- 2. Comparación de modelos (CV) ----
    cv = metrics["cv"]
    names = list(cv)
    f1 = [cv[n]["macro_f1_mean"] for n in names]
    err = [cv[n]["macro_f1_std"] for n in names]
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    colors = [pl.GENDER_COLORS["female"] if n == metrics["winner"] else pl.NEUTRAL for n in names]
    ax.barh(names[::-1], f1[::-1], xerr=err[::-1], color=colors[::-1], capsize=3)
    for y_, v in enumerate(f1[::-1]):
        ax.text(v + 0.004, y_, f"{v:.3f}", va="center", fontsize=9)
    ax.set_xlim(0, max(f1) + 0.08)
    ax.set_xlabel("F1 macro (validación cruzada, 5 folds)")
    ax.set_title("Comparación de modelos")
    pl.save(fig, config.FIGURES_DIR / "model_comparacion.png")

    # ---- 3. Experimentos de datos (E1 features, E2 desbalance) ----
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    e1 = exps["E1_features"]
    lab1 = {"solo_acordes": "Solo acordes", "acordes_mas_notas": "Acordes + notas", "solo_notas": "Solo notas"}
    axes[0].bar([lab1[k] for k in e1], [e1[k]["macro_f1"] for k in e1], color=[pl.ACCENT, pl.NEUTRAL, pl.NEUTRAL])
    axes[0].set_ylim(0.5, 0.72)
    axes[0].set_ylabel("F1 macro (validación)")
    axes[0].set_title("Qué información usar")
    e2 = exps["E2_desbalance"]
    lab2 = {"sin_pesos": "Sin pesos", "class_weight_balanced": "class_weight", "undersampling": "Undersampling"}
    axes[1].bar([lab2[k] for k in e2], [e2[k]["macro_f1"] for k in e2], color=[pl.ACCENT, pl.NEUTRAL, pl.NEUTRAL])
    axes[1].set_ylim(0.5, 0.72)
    axes[1].set_title("Cómo tratar el desbalance")
    for ax in axes:
        for p in ax.patches:
            ax.text(p.get_x() + p.get_width() / 2, p.get_height() + 0.004, f"{p.get_height():.3f}",
                    ha="center", fontsize=9)
    pl.save(fig, config.FIGURES_DIR / "model_experimentos.png")

    # ---- 4. Calibración de probabilidades (uno-contra-todos) ----
    fig, ax = plt.subplots(figsize=(5.5, 5))
    ax.plot([0, 1], [0, 1], "--", color=pl.NEUTRAL, lw=1, label="Calibración perfecta")
    out["ece"] = {}
    for k, c in enumerate(classes):
        frac, mean_p = calibration_curve((yte == c).astype(int), proba[:, k], n_bins=10, strategy="quantile")
        ax.plot(mean_p, frac, "o-", color=pl.GENDER_COLORS[c], label=es[c], ms=4)
        bins = np.quantile(proba[:, k], np.linspace(0, 1, 11))
        ids = np.clip(np.digitize(proba[:, k], bins[1:-1]), 0, 9)
        ece = sum(abs(((yte == c)[ids == b]).mean() - proba[ids == b, k].mean()) * (ids == b).mean()
                  for b in range(10) if (ids == b).any())
        out["ece"][c] = round(float(ece), 4)
    ax.set_xlabel("Probabilidad predicha")
    ax.set_ylabel("Frecuencia observada")
    ax.set_title("Calibración (test)")
    ax.legend(frameon=False)
    pl.save(fig, config.FIGURES_DIR / "model_calibracion.png")

    # ---- 5. Importancia por permutacion (que acordes mueven mas la prediccion) ----
    rng = np.random.default_rng(config.SEED)
    sub = rng.choice(len(yte), size=min(6000, len(yte)), replace=False)
    pi = permutation_importance(model, Xte[sub], yte[sub], scoring="f1_macro", n_repeats=5,
                                random_state=config.SEED, n_jobs=-1)
    imp = pd.Series(pi.importances_mean, index=vocab).sort_values(ascending=False)
    top = imp.head(20)[::-1]
    fig, ax = plt.subplots(figsize=(7.5, 6))
    ax.barh(top.index, top.values, color=pl.ACCENT)
    ax.set_xlabel("Caída del F1 macro al permutar el acorde")
    ax.set_title("Acordes más importantes para el modelo")
    pl.save(fig, config.FIGURES_DIR / "model_importancia.png")
    out["top_features"] = {k: round(float(v), 4) for k, v in imp.head(15).items()}

    # ---- 6. Confiabilidad segun cantidad de votos del perfume (test) ----
    votes = df.loc[te, "vote_count"].values
    buckets = [("0-4 votos", 0, 5), ("5-19", 5, 20), ("20-99", 20, 100), ("100+", 100, 10**9)]
    out["by_votes"] = {}
    for label, lo, hi in buckets:
        m = (votes >= lo) & (votes < hi)
        out["by_votes"][label] = {
            "n": int(m.sum()),
            "accuracy": round(float(accuracy_score(yte[m], pred[m])), 4),
            "macro_f1": round(float(f1_score(yte[m], pred[m], average="macro")), 4),
        }

    # ---- 7. Robustez: particion por MARCA (perfumes de marcas nunca vistas) ----
    groups = df["brand"].fillna("desconocida").values
    gss = GroupShuffleSplit(n_splits=1, test_size=config.TEST_SIZE, random_state=config.SEED)
    tr_idx, te_idx = next(gss.split(X, df["gender"].values, groups))
    fresh = clone(model).fit(X[tr_idx], df["gender"].values[tr_idx])
    p2 = fresh.predict(X[te_idx])
    y2 = df["gender"].values[te_idx]
    out["brand_split"] = {
        "macro_f1": round(float(f1_score(y2, p2, average="macro")), 4),
        "accuracy": round(float(accuracy_score(y2, p2)), 4),
        "n_test": int(len(te_idx)),
    }
    out["random_split"] = {k: metrics["test"][k] for k in ("macro_f1", "accuracy")}

    (config.REPORTS_DIR / "evaluation.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
