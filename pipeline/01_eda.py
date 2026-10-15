"""01 - Analisis exploratorio (EDA) y justificacion de decisiones de limpieza.

Genera las figuras de docs/figures/eda_*.png y reports/eda.json.
Uso: python pipeline/01_eda.py
"""
import _bootstrap  # noqa: F401  (configura sys.path)

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import plotting as pl
from perfume_gender import config
from perfume_gender.data import clean, load_raw
from perfume_gender.features import build_vocab, to_matrix


def main() -> None:
    pl.setup()
    raw = load_raw()
    df, stats = clean(raw)
    report: dict = {"cleaning": stats}
    print(f"Filas crudas: {len(raw):,} -> limpias: {len(df):,}")

    # ---- 1. Distribucion de la variable objetivo (antes / despues de limpiar) ----
    fig, ax = plt.subplots(figsize=(7.5, 4))
    order = config.CLASSES
    before = pd.Series(stats["raw_class_counts"]).reindex(order)
    after = pd.Series(stats["final_class_counts"]).reindex(order)
    x = np.arange(len(order))
    w = 0.38
    ax.bar(x - w / 2, before.values, w, label="Dataset crudo", color=pl.NEUTRAL, alpha=0.55)
    ax.bar(x + w / 2, after.values, w, label="Tras limpieza", color=[pl.GENDER_COLORS[c] for c in order])
    for xi, v in zip(x + w / 2, after.values):
        ax.text(xi, v, f"{v / after.sum():.0%}", ha="center", va="bottom", fontsize=9)
    ax.set_xticks(x, [config.CLASS_LABELS_ES[c] for c in order])
    ax.set_ylabel("Perfumes")
    ax.set_title("Variable objetivo: género")
    ax.legend(frameon=False)
    pl.save(fig, config.FIGURES_DIR / "eda_01_clases.png")
    report["baseline_majority"] = float(after.max() / after.sum())

    # ---- 2. Cantidad de acordes por perfume y relacion con la cantidad de votos ----
    df["n_accords"] = df["accords_dict"].map(len)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    counts = df["n_accords"].value_counts().sort_index()
    axes[0].bar(counts.index, counts.values, color=pl.ACCENT)
    axes[0].set_xlabel("Acordes por perfume")
    axes[0].set_ylabel("Perfumes")
    axes[0].set_title("Casi todos tienen 8 acordes")
    groups = [np.log10(df.loc[df["n_accords"] == n, "vote_count"] + 1) for n in range(1, 9)]
    axes[1].boxplot(groups, tick_labels=range(1, 9), showfliers=False,
                    boxprops={"color": pl.NEUTRAL}, medianprops={"color": pl.GENDER_COLORS["female"]})
    axes[1].set_xlabel("Acordes por perfume")
    axes[1].set_ylabel("log10(votos + 1)")
    axes[1].set_title("Votos según cantidad de acordes")
    pl.save(fig, config.FIGURES_DIR / "eda_02_acordes_por_perfume.png")
    report["n_accords_counts"] = {int(k): int(v) for k, v in counts.items()}
    report["median_votes_by_n_accords"] = {
        int(n): float(df.loc[df["n_accords"] == n, "vote_count"].median()) for n in range(1, 9)
    }

    # ---- 3. Distribucion de votos (outliers por cola larga) ----
    fig, ax = plt.subplots(figsize=(7.5, 4))
    ax.hist(np.log10(df["vote_count"] + 1), bins=50, color=pl.ACCENT)
    ax.set_xlabel("log10(votos + 1)")
    ax.set_ylabel("Perfumes")
    ax.set_title("Cantidad de votos por perfume (cola muy larga)")
    for thr in (5, 20):
        ax.axvline(np.log10(thr + 1), color=pl.GENDER_COLORS["female"], ls="--", lw=1)
        ax.text(np.log10(thr + 1), ax.get_ylim()[1] * 0.92, f" {thr} votos", fontsize=8,
                color=pl.GENDER_COLORS["female"])
    pl.save(fig, config.FIGURES_DIR / "eda_03_votos.png")
    vc = df["vote_count"]
    report["vote_count"] = {
        "median": float(vc.median()), "p25": float(vc.quantile(.25)), "p75": float(vc.quantile(.75)),
        "max": float(vc.max()), "lt5": int((vc < 5).sum()), "eq0": int((vc == 0).sum()),
    }

    # ---- 4. Distribucion de intensidades (el acorde principal siempre vale 100) ----
    all_vals = np.concatenate([list(d.values()) for d in df["accords_dict"]])
    fig, ax = plt.subplots(figsize=(7.5, 4))
    ax.hist(all_vals[all_vals < 100], bins=50, color=pl.ACCENT)
    ax.set_xlabel("Intensidad del acorde (0-100), sin el acorde principal")
    ax.set_ylabel("Apariciones")
    ax.set_title("Intensidades: el acorde principal es siempre 100")
    pl.save(fig, config.FIGURES_DIR / "eda_04_intensidades.png")
    top_per_perfume = df["accords_dict"].map(lambda d: max(d.values()))
    report["intensity"] = {
        "top_accord_always_100": bool((top_per_perfume == 100).all()),
        "min": float(all_vals.min()), "median": float(np.median(all_vals)),
        "p5": float(np.percentile(all_vals, 5)),
    }

    # ---- 5. Frecuencia de acordes ----
    vocab = build_vocab(df["accords_dict"])
    X = to_matrix(df["accords_dict"], vocab)
    freq = pd.Series((X > 0).mean(axis=0), index=vocab).sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(8, 7))
    top = freq.head(30)[::-1]
    ax.barh(top.index, top.values * 100, color=pl.ACCENT)
    ax.set_xlabel("% de perfumes que lo incluyen")
    ax.set_title("Los 30 acordes más frecuentes")
    pl.save(fig, config.FIGURES_DIR / "eda_05_frecuencia_acordes.png")
    report["n_accords_vocab"] = len(vocab)
    report["rarest_accords"] = {a: int((X[:, vocab.index(a)] > 0).sum()) for a in freq.tail(8).index}

    # ---- 6. Acordes que mas distinguen femenino de masculino ----
    y = df["gender"].values
    mean_by_gender = pd.DataFrame({g: X[y == g].mean(axis=0) for g in config.CLASSES}, index=vocab)
    diff = (mean_by_gender["female"] - mean_by_gender["male"])
    sel = pd.concat([diff.sort_values().head(12), diff.sort_values().tail(12)]).sort_values()
    fig, ax = plt.subplots(figsize=(8, 7))
    ax.barh(sel.index, sel.values,
            color=[pl.GENDER_COLORS["female"] if v > 0 else pl.GENDER_COLORS["male"] for v in sel.values])
    ax.axvline(0, color="black", lw=0.8)
    ax.set_xlabel("Intensidad media en femeninos - intensidad media en masculinos")
    ax.set_title("Acordes que más separan femenino (rosa) de masculino (azul)")
    pl.save(fig, config.FIGURES_DIR / "eda_06_acordes_por_genero.png")
    report["top_female_accords"] = list(diff.sort_values(ascending=False).head(8).index)
    report["top_male_accords"] = list(diff.sort_values().head(8).index)

    # ---- 7. Correlacion entre los acordes mas frecuentes ----
    top_acc = list(freq.head(25).index)
    corr = pd.DataFrame(X[:, [vocab.index(a) for a in top_acc]], columns=top_acc).corr()
    fig, ax = plt.subplots(figsize=(9, 7.5))
    im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-0.6, vmax=0.6)
    ax.set_xticks(range(len(top_acc)), top_acc, rotation=90, fontsize=8)
    ax.set_yticks(range(len(top_acc)), top_acc, fontsize=8)
    ax.grid(False)
    fig.colorbar(im, ax=ax, shrink=0.8, label="Correlacion de Pearson")
    ax.set_title("Co-ocurrencia entre los 25 acordes más frecuentes")
    pl.save(fig, config.FIGURES_DIR / "eda_07_correlacion.png")

    config.REPORTS_DIR.mkdir(exist_ok=True)
    (config.REPORTS_DIR / "eda.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print("Listo: reports/eda.json")


if __name__ == "__main__":
    main()
