# Ficha del modelo — ScentAI

Documento breve sobre qué hace el modelo, con qué datos se entrenó, qué tan bien funciona y dónde falla. Las cifras salen de `reports/*.json` (se regeneran con `python pipeline/run_all.py`) y se detallan en el [README](README.md).

## Qué es
Dos modelos de scikit-learn que se usan juntos, con los **acordes** de un perfume y su **intensidad relativa** (0–100) como única entrada:

| Modelo | Archivo | Qué devuelve |
|---|---|---|
| **Índice de masculinidad percibida** (principal) | `models/index_model.joblib` | Posición 0–1 en el espectro femenino ↔ masculino y la zona (femenino < 0,33 · unisex · masculino > 0,67) |
| **Clasificador de la etiqueta `gender`** (complemento) | `models/model.joblib` | Probabilidades femenino / masculino / unisex, lectura femenino vs. masculino y frecuencia base |

## Uso previsto
Orientar a **perfumistas** en la etapa temprana de diseño: estimar hacia qué lado del espectro tiende un perfil de acordes antes de pedir la primera muestra a la esenciera.

**No es** una garantía de cómo se percibirá la fórmula final, ni sirve para decidir por sí solo el posicionamiento comercial de un perfume.

## Datos
Dataset de Kaggle con perfumes de Fragrantica (131.930 filas). Tras la limpieza: 122.955 perfumes con perfil de acordes único. El objetivo del modelo principal se construye con los votos de percepción (`perceived_*`) de 100.541 perfumes. Los votos se usan **solo como objetivo, nunca como entrada**.

## Resultados (conjunto de test, perfumes nunca vistos)
- **Modelo de índice** (perfumes con ≥ 10 votos de percepción): error medio 0,126, correlación de Spearman 0,810, F1 macro por zonas 0,676.
- **Clasificador de la etiqueta**: exactitud 64,7 % (baseline 51,2 %), F1 macro 0,599.

## Limitaciones y sesgos
- **Los acordes son votos de usuarios sobre perfumes ya lanzados**, no fórmulas. El modelo aprende cómo se perciben o comercializan los perfiles existentes.
- **Los votos de percepción no están libres de sesgo:** quienes votan ven antes la etiqueta de género de la marca.
- **Estereotipos de género:** el modelo reproduce las convenciones del mercado (qué acordes se asocian a "femenino" o "masculino"). Esas convenciones son culturales y pueden cambiar; el modelo no las juzga.
- **Zona masculina → tiende a unisex:** una parte de los perfumes percibidos como masculinos (44 % en el test) queda ubicada en la zona intermedia, porque los acordes solos no los distinguen de los unisex.
- **Perfumes con pocos votos son menos confiables** como referencia: el rendimiento baja en perfumes con menos de 5 votos.
- **Solo acordes:** no usa las notas. Un experimento mostró que agregarlas sube el F1 del clasificador de 0,598 a 0,670; no se incluyó porque se asume que el perfumista aún no las define al hacer el pedido (hipótesis a validar con un perfumista).
- Vocabulario cerrado de 72 acordes en inglés (los de Fragrantica); máximo 8 por perfume.

## Datos de entrenamiento y reproducibilidad
Semilla fija (`42`), partición 80/20 hecha antes de entrenar y test usado una sola vez. Las versiones de las librerías están fijadas en `requirements*.txt`; el `.joblib` depende de la versión exacta de scikit-learn.
