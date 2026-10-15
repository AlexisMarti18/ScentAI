# Dataset crudo

Aqui va `perfumes.csv` (≈127 MB, 131.930 perfumes, 59 columnas), extraido de Fragrantica y publicado en Kaggle.
El archivo **no se versiona** en git (supera el limite de 100 MB de GitHub).

Para **usar la app no lo necesitas** (el modelo ya esta en `models/`). Solo hace falta si queres reentrenar:

1. Descargalo desde Kaggle (busca "Fragrantica perfumes dataset" y elegi el que tiene las columnas
   `accords`, `notes_top`, `notes_middle`, `notes_base`, `notes_flat`, `gender`).
2. Guardalo como `data/raw/perfumes.csv`.
3. Corre el pipeline (ver README principal, seccion 4).

Columnas que usa el proyecto: `id`, `name`, `brand`, `gender`, `vote_count`, `accords`,
`notes_top`, `notes_middle`, `notes_base`, `notes_flat`.
