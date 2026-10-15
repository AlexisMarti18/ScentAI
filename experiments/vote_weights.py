"""Estudio: como tratar la cantidad de votos de percepcion al entrenar el modelo de indice.

Justifica la decision de usar pesos sqrt(min(votos, 100)) en lugar de filtrar por votos.
Usa SOLO el train (el test no se toca). Validacion: perfumes con >= 30 votos de percepcion.

  1. Filtro por minimo de votos (sin pesos), 1 particion.
  2. Esquemas de pesos vs filtro, promedio de 3 particiones.

Salida: reports/vote_weights.json
Uso: python experiments/vote_weights.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import json  # noqa: E402

import numpy as np  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402
from sklearn.ensemble import HistGradientBoostingRegressor  # noqa: E402
from sklearn.metrics import mean_absolute_error  # noqa: E402
from sklearn.model_selection import train_test_split  # noqa: E402

from perfume_gender import config  # noqa: E402
from perfume_gender.modeling import load_dataset  # noqa: E402

N_VALIDACION = 30
FILTROS = (1, 3, 5, 10, 15, 20, 30, 50, 100)
SEMILLAS = (42, 7, 123)

ESQUEMAS = {
    "sin filtro, sin pesos (N>=1)": (1, lambda v: np.ones_like(v)),
    "filtro N>=5, sin pesos": (5, lambda v: np.ones_like(v)),
    "pesos min(votos,5)": (1, lambda v: np.minimum(v, 5)),
    "pesos min(votos,10)": (1, lambda v: np.minimum(v, 10)),
    "pesos min(votos,30)": (1, lambda v: np.minimum(v, 30)),
    "pesos min(votos,100)": (1, lambda v: np.minimum(v, 100)),
    "pesos sqrt(votos), tope 100": (1, lambda v: np.sqrt(np.minimum(v, 100))),
    "N>=3 + pesos min(votos,30)": (3, lambda v: np.minimum(v, 30)),
}


def regresor(seed: int) -> HistGradientBoostingRegressor:
    return HistGradientBoostingRegressor(
        max_iter=300, learning_rate=0.08, max_leaf_nodes=31, min_samples_leaf=40,
        early_stopping=True, validation_fraction=0.1, n_iter_no_change=20, random_state=seed)


def evaluar(X, y, v, a, b, n_min, pesos, seed):
    ia = a[v[a] >= n_min]
    m = regresor(seed).fit(X[ia], y[ia], sample_weight=pesos(v[ia].astype(float)))
    vb = b[v[b] >= N_VALIDACION]
    pred = np.clip(m.predict(X[vb]), 0, 1)
    return len(ia), float(mean_absolute_error(y[vb], pred)), float(spearmanr(y[vb], pred).statistic)


def main() -> None:
    df, X, _ = load_dataset()
    train = (df["split"] == "train").values
    X = X[train]
    y = df.loc[train, "perc_index"].values
    v = df.loc[train, "perc_votes"].values
    con_voto = v >= 1
    out: dict = {"n_validacion_votos": N_VALIDACION, "train_total": int(train.sum()),
                 "filtros": {}, "esquemas": {}}

    # Para el estudio solo se usan perfumes con indice (>= 1 voto de percepcion).
    idx = np.where(con_voto)[0]
    a, b = train_test_split(idx, test_size=0.2, random_state=42)
    print("Filtro por votos minimos (sin pesos):")
    for n in FILTROS:
        filas, mae, sp = evaluar(X, y, v, a, b, n, lambda w: np.ones_like(w), 42)
        out["filtros"][f"N{n}"] = {"filas_train": filas, "pct_del_train": round(100 * filas / train.sum(), 1),
                                   "mae": round(mae, 4), "spearman": round(sp, 4)}
        print(f"  N>={n:>3}: filas={filas:>6,}  MAE={mae:.4f}  Spearman={sp:.4f}")

    resultados = {k: [] for k in ESQUEMAS}
    for seed in SEMILLAS:
        a, b = train_test_split(idx, test_size=0.2, random_state=seed)
        for nombre, (n_min, pesos) in ESQUEMAS.items():
            _, mae, sp = evaluar(X, y, v, a, b, n_min, pesos, seed)
            resultados[nombre].append((mae, sp))
    print("\nEsquemas (promedio de 3 particiones):")
    for nombre, r in resultados.items():
        r = np.array(r)
        out["esquemas"][nombre] = {"mae": round(float(r[:, 0].mean()), 4), "mae_std": round(float(r[:, 0].std()), 4),
                                   "spearman": round(float(r[:, 1].mean()), 4),
                                   "spearman_std": round(float(r[:, 1].std()), 4)}
        print(f"  {nombre:32s} MAE={r[:, 0].mean():.4f}  Spearman={r[:, 1].mean():.4f}")

    (config.REPORTS_DIR / "vote_weights.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Listo: reports/vote_weights.json")


if __name__ == "__main__":
    main()
