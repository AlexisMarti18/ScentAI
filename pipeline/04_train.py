"""04 - Seleccion de modelo (CV sobre TRAIN) y entrenamiento final.

  1. Validacion cruzada estratificada (5 folds, macro-F1) de todos los candidatos
     sobre el conjunto de entrenamiento. El TEST no se usa para elegir.
  2. Ajuste fino acotado del Gradient Boosting, el mejor candidato (RandomizedSearchCV).
  3. El ganador se reentrena con todo el TRAIN y se evalua UNA sola vez en TEST.
  4. Se guarda models/model.joblib + metadata + reports/metrics.json.

Uso: python pipeline/04_train.py
"""
import _bootstrap  # noqa: F401

import json
import time
from datetime import datetime, timezone

import joblib
import numpy as np
import sklearn
from sklearn.base import clone
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix, f1_score, accuracy_score
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, cross_validate

from perfume_gender import config
from perfume_gender.modeling import candidates, load_dataset, update_metadata

SVM_SUBSAMPLE = 20_000  # la SVM RBF es O(n^2): se evalua sobre una submuestra estratificada


def stratified_subsample(y, n, seed):
    rng = np.random.default_rng(seed)
    idx = []
    for c in np.unique(y):
        pool = np.where(y == c)[0]
        idx.append(rng.choice(pool, int(round(n * len(pool) / len(y))), replace=False))
    return np.sort(np.concatenate(idx))


def main() -> None:
    df, X, vocab = load_dataset()
    tr = (df["split"] == "train").values
    te = ~tr
    Xtr, ytr, Xte, yte = X[tr], df.loc[tr, "gender"].values, X[te], df.loc[te, "gender"].values
    print(f"Train {len(ytr):,} | Test {len(yte):,} | features {Xtr.shape[1]}")

    cv = StratifiedKFold(n_splits=config.CV_FOLDS, shuffle=True, random_state=config.SEED)
    scoring = {"macro_f1": "f1_macro", "accuracy": "accuracy"}
    report: dict = {"cv": {}, "tuning": {}}

    # ---- 1. Comparacion de candidatos por CV ----
    for name, est in candidates().items():
        Xs, ys, note = Xtr, ytr, ""
        if name.startswith("SVM"):
            sub = stratified_subsample(ytr, SVM_SUBSAMPLE, config.SEED)
            Xs, ys, note = Xtr[sub], ytr[sub], f"submuestra de {SVM_SUBSAMPLE:,} filas"
        t = time.time()
        res = cross_validate(est, Xs, ys, cv=cv, scoring=scoring, n_jobs=1 if name.startswith("Random") else -1)
        secs = time.time() - t
        report["cv"][name] = {
            "macro_f1_mean": round(float(res["test_macro_f1"].mean()), 4),
            "macro_f1_std": round(float(res["test_macro_f1"].std()), 4),
            "accuracy_mean": round(float(res["test_accuracy"].mean()), 4),
            "fit_seconds_per_fold": round(float(res["fit_time"].mean()), 1),
            "note": note,
        }
        print(f"{name:32s} F1={report['cv'][name]['macro_f1_mean']:.4f} "
              f"± {report['cv'][name]['macro_f1_std']:.4f}  acc={report['cv'][name]['accuracy_mean']:.4f} "
              f"({secs:.0f}s) {note}")

    # ---- 2. Ajuste fino acotado del Gradient Boosting ----
    print("Ajustando Gradient Boosting...")
    base = candidates()["Gradient Boosting (HGB)"]
    search = RandomizedSearchCV(
        base,
        {"learning_rate": [0.03, 0.05, 0.08, 0.12],
         "max_leaf_nodes": [15, 31, 63],
         "min_samples_leaf": [20, 50, 100],
         "l2_regularization": [0.0, 0.1, 1.0, 5.0],
         "max_iter": [300, 500]},
        n_iter=10, scoring="f1_macro", cv=3, random_state=config.SEED, n_jobs=-1, refit=False)
    search.fit(Xtr, ytr)
    report["tuning"]["Gradient Boosting (HGB)"] = {
        "best_params": search.best_params_, "best_cv_macro_f1": round(float(search.best_score_), 4)}
    print("Mejores parametros:", search.best_params_, round(float(search.best_score_), 4))

    tuned = clone(base).set_params(**search.best_params_)
    res = cross_validate(tuned, Xtr, ytr, cv=cv, scoring=scoring, n_jobs=-1)
    report["cv"]["Gradient Boosting (HGB) ajustado"] = {
        "macro_f1_mean": round(float(res["test_macro_f1"].mean()), 4),
        "macro_f1_std": round(float(res["test_macro_f1"].std()), 4),
        "accuracy_mean": round(float(res["test_accuracy"].mean()), 4),
        "fit_seconds_per_fold": round(float(res["fit_time"].mean()), 1),
        "note": "hiperparámetros de RandomizedSearchCV",
    }
    print("HGB ajustado:", report["cv"]["Gradient Boosting (HGB) ajustado"])

    # ---- 3. Eleccion del ganador (por CV; solo entre modelos que pueden servirse) ----
    servible = {k: v for k, v in report["cv"].items()
                if not k.startswith("Baseline") and not v["note"].startswith("submuestra")}
    winner = max(servible, key=lambda k: servible[k]["macro_f1_mean"])
    print(f"\nGanador por CV: {winner}")
    final = tuned if winner.endswith("ajustado") else candidates()[winner]
    final.fit(Xtr, ytr)

    # ---- 4. Evaluacion unica en TEST ----
    pred = final.predict(Xte)
    classes = [str(c) for c in final.classes_]
    cm = confusion_matrix(yte, pred, labels=classes)
    cr = classification_report(yte, pred, labels=classes, output_dict=True, zero_division=0)
    majority = max((yte == c).mean() for c in classes)
    test = {
        "macro_f1": round(float(f1_score(yte, pred, average="macro")), 4),
        "accuracy": round(float(accuracy_score(yte, pred)), 4),
        "baseline_accuracy": round(float(majority), 4),
        "per_class": {c: {k: round(float(cr[c][k]), 4) for k in ("precision", "recall", "f1-score")}
                      | {"support": int(cr[c]["support"])} for c in classes},
        "confusion_matrix": {"labels": classes, "matrix": cm.tolist()},
        "n_test": int(len(yte)),
    }
    report["winner"] = winner
    report["test"] = test
    print(f"TEST  macro-F1={test['macro_f1']}  accuracy={test['accuracy']}  (baseline {test['baseline_accuracy']})")

    # ---- 5. Artefactos ----
    config.MODELS_DIR.mkdir(exist_ok=True)
    joblib.dump(final, config.MODEL_PATH, compress=3)
    size_mb = config.MODEL_PATH.stat().st_size / 1e6
    metadata = {
        "model_name": winner,
        "model_class": type(final).__name__,
        "classes": classes,
        "n_features": len(vocab),
        "n_train": int(len(ytr)),
        "n_test": int(len(yte)),
        "metrics_test": {k: test[k] for k in ("macro_f1", "accuracy", "baseline_accuracy")},
        "per_class_test": test["per_class"],
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sklearn_version": sklearn.__version__,
        "model_size_mb": round(size_mb, 2),
    }
    priors = {c: round(float((ytr == c).mean()), 4) for c in classes}  # frecuencia base (para el "lift")
    update_metadata(classifier=metadata, class_priors=priors)
    config.REPORTS_DIR.mkdir(exist_ok=True)
    (config.REPORTS_DIR / "metrics.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Modelo guardado en {config.MODEL_PATH} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
