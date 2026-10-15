"""Datos de entrenamiento y modelos candidatos."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC

from . import config
from .features import load_vocab, to_matrix
from .parsing import parse_accords


def load_dataset() -> tuple[pd.DataFrame, np.ndarray, list[str]]:
    """Lee el dataset limpio (salida de pipeline/02_etl.py).

    Devuelve (df, X, vocab). X tiene una fila por perfume con intensidades 0-1.
    """
    path = config.DATA_PROCESSED / "clean.csv.gz"
    if not path.exists():
        raise FileNotFoundError("Falta data/processed/clean.csv.gz: ejecuta pipeline/02_etl.py")
    df = pd.read_csv(path, low_memory=False)
    vocab = load_vocab(config.VOCAB_PATH)
    df["accords_dict"] = df["accords"].map(parse_accords)
    X = to_matrix(df["accords_dict"], vocab)
    return df, X, vocab


def candidates(seed: int = config.SEED) -> dict[str, object]:
    """Modelos que se comparan en validacion cruzada (ver README, seccion 3)."""
    return {
        "Baseline (clase mayoritaria)": DummyClassifier(strategy="most_frequent"),
        "Regresión logística": LogisticRegression(
            C=1.0, max_iter=1000),
        "Random Forest": RandomForestClassifier(
            n_estimators=200, min_samples_leaf=5,
            n_jobs=-1, random_state=seed),
        "Gradient Boosting (HGB)": HistGradientBoostingClassifier(
            max_iter=300, learning_rate=0.08, max_leaf_nodes=31,
            early_stopping=True, validation_fraction=0.1, n_iter_no_change=20, random_state=seed),
        "MLP (red neuronal)": MLPClassifier(
            hidden_layer_sizes=(128, 64), early_stopping=True, max_iter=200, random_state=seed),
        "SVM (RBF)": SVC(C=1.0, kernel="rbf", random_state=seed),
    }
