"""Verificacion de las sugerencias con el modelo real, sobre perfumes del TEST.

Para cada par (zona actual -> zona objetivo) toma hasta 300 perfumes del test cuya zona
predicha es la actual, pide sugerencias y mide:
  * con_sugerencias : % de perfumes que reciben al menos una sugerencia.
  * mejor_llega     : % en que la MEJOR sugerencia deja el indice esperado dentro de la zona objetivo.
  * mejora_media    : cuanto cambia el indice con la mejor sugerencia (en valor absoluto).
  * acciones        : que accion es la mejor sugerencia.
Son indices ESPERADOS por el modelo (no cambios reales de percepcion): es una verificacion de
coherencia, no una prueba de causalidad.

Salida: reports/suggestions.json
Uso: python experiments/suggestions_check.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import json  # noqa: E402
import time  # noqa: E402
from collections import Counter  # noqa: E402

import numpy as np  # noqa: E402

from perfume_gender import config  # noqa: E402
from perfume_gender.modeling import load_dataset  # noqa: E402
from perfume_gender.perception import zone  # noqa: E402
from perfume_gender.predictor import Predictor  # noqa: E402

PARES = (("unisex", "male"), ("unisex", "female"), ("female", "male"), ("male", "female"))
MUESTRA = 300


def main() -> None:
    predictor = Predictor.load()
    df, _, _ = load_dataset()
    test = df[df["split"] == "test"].sample(frac=1, random_state=config.SEED)
    perfiles = []
    for acc in test["accords_dict"]:
        prof = {k: v for k, v in acc.items() if k in predictor.vocab}
        if prof:
            perfiles.append((prof, str(zone(predictor.predict(prof, explain=False)["index"]))))

    out: dict = {"muestra_por_par": MUESTRA, "pares": {}}
    for origen, destino in PARES:
        n = hay = llega = 0
        mejoras, tiempos, acciones = [], [], Counter()
        for prof, z in perfiles:
            if z != origen:
                continue
            n += 1
            t = time.perf_counter()
            res = predictor.suggest(prof, destino)
            tiempos.append(time.perf_counter() - t)
            if res["suggestions"]:
                hay += 1
                top = res["suggestions"][0]
                acciones[top["action"]] += 1
                mejoras.append(abs(top["delta"]))
                llega += str(zone(top["index_after"])) == destino
            if n >= MUESTRA:
                break
        out["pares"][f"{origen}->{destino}"] = {
            "n": n,
            "con_sugerencias_pct": round(100 * hay / n, 1),
            "mejor_llega_pct": round(100 * llega / n, 1),
            "mejora_media": round(float(np.mean(mejoras)), 3),
            "acciones": dict(acciones),
            "ms_medio": round(1000 * float(np.mean(tiempos))),
        }
        print(origen, "->", destino, out["pares"][f"{origen}->{destino}"])

    (config.REPORTS_DIR / "suggestions.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Listo: reports/suggestions.json")


if __name__ == "__main__":
    main()
