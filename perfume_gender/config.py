"""Rutas y constantes compartidas por el pipeline y la API.

Todas las rutas son relativas a la raiz del repositorio (nada de rutas absolutas),
asi el proyecto funciona en cualquier maquina despues de un `git clone`.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DATA_RAW = ROOT / "data" / "raw" / "perfumes.csv"
DATA_PROCESSED = ROOT / "data" / "processed"
MODELS_DIR = ROOT / "models"
REPORTS_DIR = ROOT / "reports"
FIGURES_DIR = ROOT / "docs" / "figures"

MODEL_PATH = MODELS_DIR / "model.joblib"
VOCAB_PATH = MODELS_DIR / "accords_vocab.json"
METADATA_PATH = MODELS_DIR / "metadata.json"

SEED = 42
TEST_SIZE = 0.20
CV_FOLDS = 5

# Clases de la variable objetivo, en el orden en que las devuelve el modelo.
CLASSES = ["female", "male", "unisex"]
CLASS_LABELS_ES = {"female": "Femenino", "male": "Masculino", "unisex": "Unisex"}

# Fragrantica muestra como maximo 8 acordes por perfume; el mas fuerte vale siempre 100.
MAX_ACCORDS = 8
