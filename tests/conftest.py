import sys
from pathlib import Path

import numpy as np
import pytest
from sklearn.linear_model import LinearRegression, LogisticRegression

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from perfume_gender.predictor import Predictor  # noqa: E402

VOCAB = ["aromatic", "floral", "sweet", "woody", "fresh spicy", "powdery"]


@pytest.fixture(scope="session")
def tiny_predictor() -> Predictor:
    """Predictor chico con datos sinteticos: los tests no dependen de los modelos reales."""
    rng = np.random.default_rng(0)
    X = rng.random((400, len(VOCAB))).astype("float32")
    # femenino ~ floral/sweet/powdery, masculino ~ aromatic/woody/fresh spicy
    masc = (X[:, 0] + X[:, 3] + X[:, 4]) - (X[:, 1] + X[:, 2] + X[:, 5])
    index = np.clip(0.5 + masc / 4, 0, 1)
    y = np.where(masc > 0.8, "male", np.where(masc < -0.8, "female", "unisex"))
    classifier = LogisticRegression(max_iter=500).fit(X, y)
    index_model = LinearRegression().fit(X, index)
    metadata = {
        "classifier": {"model_name": "tiny", "n_features": len(VOCAB), "n_train": 400, "n_test": 0,
                       "metrics_test": {"accuracy": 0.6, "macro_f1": 0.5, "baseline_accuracy": 0.5}},
        "index_model": {"n_train": 400, "metrics_test_N10": {"mae": 0.1}},
        "class_priors": {"female": 0.33, "male": 0.15, "unisex": 0.52},
    }
    return Predictor(classifier=classifier, index_model=index_model, vocab=VOCAB, metadata=metadata)
