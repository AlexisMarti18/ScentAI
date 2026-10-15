"""03 - Experimentos que justifican decisiones de datos (antes de elegir modelo).

Usa un modelo rapido (Gradient Boosting) y una validacion interna (20 % del TRAIN).
El conjunto de TEST no se toca aqui.

  E1. Features: solo acordes vs acordes + notas.
  E2. Desbalance: sin pesos vs class_weight vs undersampling.
  E3. Filtro de votos minimos al entrenar.

Salida: reports/experiments.json
Uso: python pipeline/03_experiments.py
"""
import _bootstrap  # noqa: F401

import json
import time
from collections import Counter

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

from perfume_gender import config
from perfume_gender.modeling import load_dataset

TOP_NOTES = 300


def notes_matrix(df, top=TOP_NOTES):
    """Matriz binaria de las `top` notas mas frecuentes (solo para el experimento E1)."""
    cols = ["notes_top", "notes_middle", "notes_base", "notes_flat"]
    per_row = []
    for row in df[cols].itertuples(index=False):
        s = set()
        for cell in row:
            if isinstance(cell, str):
                s.update(n.strip().lower() for n in cell.split("|") if n.strip())
        per_row.append(s)
    counter = Counter(n for s in per_row for n in s)
    vocab = [n for n, _ in counter.most_common(top)]
    idx = {n: i for i, n in enumerate(vocab)}
    M = np.zeros((len(df), len(vocab)), dtype=np.float32)
    for r, s in enumerate(per_row):
        for n in s:
            j = idx.get(n)
            if j is not None:
                M[r, j] = 1.0
    return M


def model(class_weight=None):
    return HistGradientBoostingClassifier(
        max_iter=200, learning_rate=0.1, class_weight=class_weight,
        early_stopping=True, validation_fraction=0.1, n_iter_no_change=15, random_state=config.SEED)


def score(clf, Xtr, ytr, Xva, yva, mask_va=None):
    t = time.time()
    clf.fit(Xtr, ytr)
    pred = clf.predict(Xva)
    if mask_va is not None:
        pred, yva = pred[mask_va], yva[mask_va]
    return {"macro_f1": round(float(f1_score(yva, pred, average="macro")), 4),
            "accuracy": round(float(accuracy_score(yva, pred)), 4),
            "seconds": round(time.time() - t, 1)}


def main() -> None:
    df, X, vocab = load_dataset()
    train = df["split"] == "train"
    df, X = df[train].reset_index(drop=True), X[train.values]
    y = df["gender"].values

    idx_tr, idx_va = train_test_split(np.arange(len(df)), test_size=0.2, stratify=y, random_state=config.SEED)
    out: dict = {"validation_rows": len(idx_va), "train_rows": len(idx_tr)}

    # E1: acordes vs acordes + notas
    print("E1: acordes vs acordes + notas")
    N = notes_matrix(df)
    XN = np.hstack([X, N])
    out["E1_features"] = {
        "solo_acordes": score(model(), X[idx_tr], y[idx_tr], X[idx_va], y[idx_va]),
        "acordes_mas_notas": score(model(), XN[idx_tr], y[idx_tr], XN[idx_va], y[idx_va]),
        "solo_notas": score(model(), N[idx_tr], y[idx_tr], N[idx_va], y[idx_va]),
    }
    print(json.dumps(out["E1_features"], indent=1))

    # E2: tratamiento del desbalance
    print("E2: desbalance")
    rng = np.random.default_rng(config.SEED)
    classes, counts = np.unique(y[idx_tr], return_counts=True)
    n_min = counts.min()
    under = np.concatenate([rng.choice(idx_tr[y[idx_tr] == c], n_min, replace=False) for c in classes])
    out["E2_desbalance"] = {
        "sin_pesos": score(model(None), X[idx_tr], y[idx_tr], X[idx_va], y[idx_va]),
        "class_weight_balanced": score(model("balanced"), X[idx_tr], y[idx_tr], X[idx_va], y[idx_va]),
        "undersampling": score(model(None), X[under], y[under], X[idx_va], y[idx_va]),
    }
    out["E2_desbalance"]["undersampling"]["train_rows"] = int(len(under))
    print(json.dumps(out["E2_desbalance"], indent=1))

    # E3: filtro de votos minimos en el entrenamiento
    print("E3: votos minimos")
    votes = df["vote_count"].values
    va_reliable = votes[idx_va] >= 20
    out["E3_votos"] = {}
    for thr in (0, 5, 20, 50):
        keep = idx_tr[votes[idx_tr] >= thr]
        res = score(model(), X[keep], y[keep], X[idx_va], y[idx_va])
        res_rel = score(model(), X[keep], y[keep], X[idx_va], y[idx_va], mask_va=va_reliable)
        out["E3_votos"][f"min_{thr}"] = {
            "train_rows": int(len(keep)),
            "val_todo": {k: res[k] for k in ("macro_f1", "accuracy")},
            "val_solo_20+_votos": {k: res_rel[k] for k in ("macro_f1", "accuracy")},
        }
        print(thr, out["E3_votos"][f"min_{thr}"])

    config.REPORTS_DIR.mkdir(exist_ok=True)
    (config.REPORTS_DIR / "experiments.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Listo: reports/experiments.json")


if __name__ == "__main__":
    main()
