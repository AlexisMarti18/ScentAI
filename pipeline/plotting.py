"""Estilo comun de los graficos del proyecto."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# Paleta apta para daltonismo (una por clase, mismo color en todos los graficos).
GENDER_COLORS = {"female": "#D1495B", "male": "#00798C", "unisex": "#EDAE49"}
NEUTRAL = "#6B7280"
ACCENT = "#3D348B"


def setup() -> None:
    plt.rcParams.update({
        "figure.dpi": 110,
        "savefig.dpi": 130,
        "savefig.bbox": "tight",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.labelsize": 10.5,
        "font.family": "sans-serif",
    })


def save(fig, path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
    print(f"  figura -> {path}")
