"""02 - ETL: limpieza, vocabulario de acordes y particion train/test.

Entrada : data/raw/perfumes.csv
Salidas : data/processed/clean.csv.gz  (dataset limpio + columna `split`)
          models/accords_vocab.json    (vocabulario que usan el modelo y la API)
          reports/etl.json             (estadisticas citadas en el README)
Uso: python pipeline/02_etl.py
"""
import _bootstrap  # noqa: F401

import json

from sklearn.model_selection import train_test_split

from perfume_gender import config
from perfume_gender.data import clean, load_raw
from perfume_gender.features import build_vocab, save_vocab

# Un acorde que aparece en menos perfumes que esto no aporta senal (ver README, seccion 2).
MIN_ACCORD_COUNT = 50


def main() -> None:
    raw = load_raw()
    df, stats = clean(raw)

    vocab_all = build_vocab(df["accords_dict"])
    vocab = build_vocab(df["accords_dict"], min_count=MIN_ACCORD_COUNT)
    dropped = sorted(set(vocab_all) - set(vocab))
    stats.update({"vocab_all": len(vocab_all), "vocab_kept": len(vocab), "vocab_dropped": dropped,
                  "min_accord_count": MIN_ACCORD_COUNT})
    print(f"Vocabulario: {len(vocab_all)} acordes -> {len(vocab)} (descartados: {dropped})")

    # Particion estratificada. Como ya se deduplicaron los perfiles identicos,
    # ningun perfil exacto puede estar a la vez en train y en test.
    idx_train, idx_test = train_test_split(
        df.index, test_size=config.TEST_SIZE, stratify=df["gender"], random_state=config.SEED)
    df["split"] = "train"
    df.loc[idx_test, "split"] = "test"
    stats["train_rows"] = int((df["split"] == "train").sum())
    stats["test_rows"] = int((df["split"] == "test").sum())
    stats["train_class_counts"] = df[df["split"] == "train"]["gender"].value_counts().to_dict()
    stats["test_class_counts"] = df[df["split"] == "test"]["gender"].value_counts().to_dict()

    config.DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    cols = ["id", "brand", "gender", "vote_count", "accords",
            "notes_top", "notes_middle", "notes_base", "notes_flat", "split"]
    df[cols].to_csv(config.DATA_PROCESSED / "clean.csv.gz", index=False)
    save_vocab(vocab, config.VOCAB_PATH)

    config.REPORTS_DIR.mkdir(exist_ok=True)
    (config.REPORTS_DIR / "etl.json").write_text(
        json.dumps(stats, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"Train: {stats['train_rows']:,}  Test: {stats['test_rows']:,}")
    print("Listo.")


if __name__ == "__main__":
    main()
