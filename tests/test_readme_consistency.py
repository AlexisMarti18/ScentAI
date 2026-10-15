"""Verifica que las cifras clave del README coinciden con reports/*.json.

Si cambia el pipeline y se regeneran los reportes, este test avisa que hay que actualizar el README.
Formato: coma decimal, punto de miles, redondeo "mitad hacia arriba".
"""
import json
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")


def reporte(nombre: str) -> dict:
    ruta = ROOT / "reports" / nombre
    if not ruta.exists():
        pytest.skip(f"falta {nombre} (correr pipeline/run_all.py)")
    return json.loads(ruta.read_text(encoding="utf-8"))


def dec(valor, d: int) -> str:
    """0.6125 -> '0,613' (mitad hacia arriba, coma decimal)."""
    q = Decimal(str(valor)).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP)
    return f"{q:f}".replace(".", ",")


def miles(n: int) -> str:
    return f"{int(n):,}".replace(",", ".")


def pct(frac, d: int = 1) -> str:
    return dec(Decimal(str(frac)) * 100, d)


def debe_aparecer(*textos: str) -> None:
    faltan = [t for t in textos if t not in README]
    assert not faltan, f"El README no contiene: {faltan}"


def test_limpieza_y_particion():
    etl = reporte("etl.json")
    p = etl["perceived"]
    debe_aparecer(
        miles(etl["raw_rows"]), miles(etl["final_rows"]), miles(etl["no_accords"]),
        miles(etl["duplicates_removed"]), miles(etl["train_rows"]), miles(etl["test_rows"]),
        miles(etl["conflicting_fingerprints"]), miles(etl["rows_in_conflicting_fingerprints"]),
        miles(p["rows_with_votes"]), miles(p["train_rows_with_votes"]),
        pct(p["train_rows_with_votes"] / etl["train_rows"]) + " %",
        *(miles(etl["final_class_counts"][c]) for c in ("unisex", "female", "male")),
    )


def test_estadisticas_de_votos_y_sesgo_de_etiqueta():
    eda = reporte("eda.json")["perception"]
    debe_aparecer(
        dec(eda["votos_rating"]["media"], 1), dec(eda["votos_percepcion"]["media"], 1),
        str(int(eda["votos_rating"]["mediana"])), str(int(eda["votos_percepcion"]["mediana"])),
        str(int(eda["votos_rating"]["p75"])), str(int(eda["votos_percepcion"]["p75"])),
        str(int(eda["votos_rating"]["p90"])), str(int(eda["votos_percepcion"]["p90"])),
        dec(eda["unisex_percibido_masculino_pct"], 1) + " %",
        dec(eda["unisex_percibido_femenino_pct"], 1) + " %",
        dec(eda["unisex_percibido_intermedio_pct"], 1) + " %",
    )


def test_modelo_de_indice_contra_clasificador():
    idx = reporte("index_metrics.json")
    cv = idx["cv"]
    debe_aparecer(dec(cv["mae_media"], 3), dec(cv["spearman_media"], 3))
    for k in ("N10", "N30", "N100"):
        r = idx["resultados"][k]
        a, a_arg, b = r["A_clasificador_umbral"], r["A_clasificador_argmax"], r["B_indice"]
        debe_aparecer(
            miles(r["n_test"]),
            f"{dec(a['mae'], 3)} → ",
            f"{dec(b['mae'], 3)}",
            f"{dec(a['spearman'], 3)} → ",
            f"{dec(a_arg['zonas_f1_macro'], 3)} → ",
            dec(b["zonas_f1_macro"], 3),
            dec(r["mejora_mae_pct"], 1) + " %",
        )
    caso = idx["caso_prueba"]
    debe_aparecer(dec(caso["B_indice"], 3), dec(caso["A_indice_esperado"], 3))
    assert caso["B_zona"] == "male"
    assert all(idx["criterios"].values()), idx["criterios"]


def test_clasificador_de_etiqueta():
    m = reporte("metrics.json")
    t = m["test"]
    debe_aparecer(pct(t["accuracy"]) + " %", dec(t["macro_f1"], 3), pct(t["baseline_accuracy"]) + " %")
    for clase in ("female", "male", "unisex"):
        debe_aparecer(miles(t["per_class"][clase]["support"]))
    debe_aparecer(dec(m["cv"][m["winner"]]["macro_f1_mean"], 3))


def test_estudio_de_pesos_por_votos():
    vw = reporte("vote_weights.json")
    debe_aparecer(
        dec(vw["esquemas"]["pesos sqrt(votos), tope 100"]["mae"], 4),
        dec(vw["esquemas"]["sin filtro, sin pesos (N>=1)"]["mae"], 4),
        miles(vw["filtros"]["N1"]["filas_train"]), miles(vw["filtros"]["N100"]["filas_train"]),
    )


def test_experimentos_y_robustez():
    ex = reporte("experiments.json")["E1_features"]
    debe_aparecer(*(dec(ex[k]["macro_f1"], 3) for k in ("solo_acordes", "acordes_mas_notas", "solo_notas")))
    ev = reporte("evaluation.json")
    debe_aparecer(dec(ev["brand_split"]["macro_f1"], 3))
