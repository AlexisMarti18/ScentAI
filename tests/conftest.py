import sys
from pathlib import Path

import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from perfume_gender.predictor import Predictor  # noqa: E402

VOCAB = ["aromatic", "floral", "sweet", "woody", "fresh spicy", "powdery"]


@pytest.fixture(scope="session")
def tiny_predictor() -> Predictor:
    """Predictor chico entrenado con datos sinteticos: los tests no dependen del modelo real."""
    rng = np.random.default_rng(0)
    X = rng.random((300, len(VOCAB))).astype("float32")
    # female ~ floral/sweet, male ~ aromatic/woody, unisex ~ el resto
    score_f = X[:, 1] + X[:, 2]
    score_m = X[:, 0] + X[:, 3]
    y = np.where(score_f - score_m > 0.4, "female", np.where(score_m - score_f > 0.4, "male", "unisex"))
    model = LogisticRegression(max_iter=500).fit(X, y)
    return Predictor(model=model, vocab=VOCAB, metadata={"model_name": "tiny", "n_features": len(VOCAB),
                     "n_train": 300, "n_test": 0, "metrics_test": {}})
