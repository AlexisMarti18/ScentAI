# Guía en criollo de ScentAI

**Qué es este documento:** una explicación completa, sin tecnicismos innecesarios, de todo lo que hay en este proyecto: la idea, los conceptos de ciencia de datos, cada archivo, cada bloque de código y cada resultado. Está pensado para alguien que **no** viene de ciencia de datos ni de programación avanzada. Si vos leés esto y al final entendés qué hace cada pieza y por qué está ahí, el documento cumplió.

> **Importante:** las cifras de esta guía son las de la corrida actual del proyecto (están en `README.md` y en la carpeta `reports/`). Si alguien vuelve a entrenar con otros datos, las cifras cambian, pero las explicaciones siguen valiendo.

---

## Cómo usar esta guía

La guía está ordenada de lo general a lo particular. No hace falta leerla de corrido: podés ir directo a lo que necesites.

| Si querés… | Andá a… |
|---|---|
| Entender de qué se trata el proyecto en 5 minutos | [Parte 1](#parte-1-el-proyecto-en-5-minutos) |
| Entender los términos de ciencia de datos (F1, probabilidad, train/test…) | [Parte 2](#parte-2-conceptos-de-ciencia-de-datos-explicados-en-criollo) |
| Entender las herramientas y el vocabulario de programación | [Parte 3](#parte-3-conceptos-de-programación-y-herramientas) |
| Saber qué es cada carpeta y cada archivo | [Parte 4](#parte-4-mapa-del-proyecto-y-recorrido-de-los-datos) |
| Leer el código explicado bloque por bloque | Partes [5](#parte-5-el-paquete-perfume_gender-el-corazón-compartido), [6](#parte-6-el-pipeline-de-datos-y-entrenamiento), [7](#parte-7-la-aplicación-backend-y-frontend) y [8](#parte-8-los-tests-y-los-archivos-de-la-raíz) |
| Saber qué significa cada número de los resultados | [Parte 9](#parte-9-cómo-leer-los-resultados-cada-número-explicado) |
| Resolver dudas y saber qué tocar para cambiar algo | [Parte 10](#parte-10-preguntas-frecuentes-y-guía-práctica) |

**Convenciones:**
- Las cajas con **"En criollo:"** traducen un concepto técnico a palabras de todos los días.
- Las cajas con **"En este proyecto:"** muestran cómo se usa ese concepto acá, con números reales.
- Cuando se muestra código, se explica **bloque por bloque** (grupos de líneas que hacen una sola cosa). Las líneas repetitivas (por ejemplo, los `import`) se explican la primera vez que aparecen.
- Los nombres de archivos y de funciones van `así`.

---

## Índice

- [Parte 1: El proyecto en 5 minutos](#parte-1-el-proyecto-en-5-minutos)
- [Parte 2: Conceptos de ciencia de datos explicados en criollo](#parte-2-conceptos-de-ciencia-de-datos-explicados-en-criollo)
- [Parte 3: Conceptos de programación y herramientas](#parte-3-conceptos-de-programación-y-herramientas)
- [Parte 4: Mapa del proyecto y recorrido de los datos](#parte-4-mapa-del-proyecto-y-recorrido-de-los-datos)
- [Parte 5: El paquete `perfume_gender` (el corazón compartido)](#parte-5-el-paquete-perfume_gender-el-corazón-compartido)
- [Parte 6: El pipeline de datos y entrenamiento](#parte-6-el-pipeline-de-datos-y-entrenamiento)
- [Parte 7: La aplicación (backend y frontend)](#parte-7-la-aplicación-backend-y-frontend)
- [Parte 8: Los tests y los archivos de la raíz](#parte-8-los-tests-y-los-archivos-de-la-raíz)
- [Parte 9: Cómo leer los resultados (cada número explicado)](#parte-9-cómo-leer-los-resultados-cada-número-explicado)
- [Parte 10: Preguntas frecuentes y guía práctica](#parte-10-preguntas-frecuentes-y-guía-práctica)

---

# Parte 1: El proyecto en 5 minutos

## 1.1 El problema, contado como si fuera una charla de café

Imaginá que sos perfumista y estás creando un perfume nuevo. Tenés una idea de cómo querés que huela: "algo amaderado, con cuero y un toque ahumado". Ese perfil se lo mandás a una **esenciera** (el laboratorio que fabrica las esencias), que te prepara una **muestra**. Recién cuando la huelas te das cuenta de si el resultado se "siente" femenino, masculino o algo intermedio. Si no era lo que buscabas, hay que ajustar la fórmula y pedir otra muestra. Cada ida y vuelta cuesta **tiempo y plata**.

**La idea de este proyecto:** que antes de pedir la muestra, cargues en una página web los **acordes** de tu perfume (con qué intensidad), y un programa te diga **hacia qué lado del espectro cae**: más femenino, más masculino o en el medio. Así te ahorrás varias muestras.

> **Acorde:** en perfumería, un acorde es una "familia de olor" que resume el carácter del perfume. Ejemplos: *woody* (amaderado), *sweet* (dulce), *citrus* (cítrico), *leather* (cuero), *smoky* (ahumado). No es un ingrediente concreto: es una impresión general.
>
> **Nota (ingrediente):** es el ingrediente en sí, por ejemplo cedro, pimienta, vainilla. Este proyecto **no** usa las notas, solo los acordes (más adelante se explica por qué).

## 1.2 ¿Cómo hace el programa para "adivinar"?

El programa **aprendió de ejemplos**. Se usó una base de datos pública con **131.930 perfumes reales** (sacada de Fragrantica, un sitio donde la gente carga y vota perfumes, y publicada en Kaggle, una plataforma de datos). De cada perfume se conocen:

- Sus **acordes** y qué tan fuerte es cada uno (por ejemplo: `woody:100|sweet:65|leather:40`).
- Su **género** según la marca (femenino, masculino o unisex).
- Los **votos de la gente** sobre cómo lo percibe (cuántos lo sienten femenino, masculino, unisex, etc.).

Al programa se le mostraron decenas de miles de ejemplos y fue descubriendo **patrones**: "los perfumes con mucho *floral* y *sweet* suelen percibirse femeninos", "los que tienen mucho *aromatic* y *woody* suelen percibirse masculinos". Ese proceso de descubrir patrones se llama **entrenar un modelo**. Una vez entrenado, cuando le das un perfil de acordes **nuevo** que nunca vio, aplica lo aprendido y da su mejor estimación.

> **En criollo:** es como un sommelier que probó cien mil vinos. Si le servís uno nuevo, no lo reconoce exacto, pero por el parecido con los que probó puede decirte "esto huele a un tinto joven, probablemente malbec". El modelo hace lo mismo, pero con números.

## 1.3 ¿Qué devuelve el programa?

Cuando cargás los acordes, la página te muestra:

1. **Una posición en una escala** (el **índice**) de 0 a 1: `0` es "totalmente femenino", `1` es "totalmente masculino", `0,5` es "justo en el medio". Se divide en tres **zonas**: femenino (menos de 0,33), unisex/intermedia (entre 0,33 y 0,67) y masculino (más de 0,67).
2. Una lectura **"femenino vs. masculino"**: ignora la opción "unisex" y reparte 100 % entre los dos extremos (por ejemplo, 30 % femenino / 70 % masculino).
3. Las **probabilidades por etiqueta**: cuánta chance tiene de ser etiquetado femenino, masculino o unisex, comparada con lo habitual.
4. Qué **acordes pesan más** en el resultado: cuántos puntos se mueve el índice si sacás cada acorde.

## 1.4 ¿Por qué hay DOS modelos y no uno?

Al principio el proyecto tenía un solo modelo: un **clasificador** que predecía la etiqueta de género de la marca (femenino / masculino / unisex). Al probarlo con un perfil que a un perfumista le parece claramente masculino (cuero, madera, humo), el modelo respondía **"unisex con 90 % de probabilidad"**. Parecía que el programa "siempre se tira a unisex".

Se investigó la causa y se descubrió algo importante:

- No era un problema de que hubiera **más perfumes unisex** en los datos (se probó "equilibrar" y no solo no ayudó, sino que **empeoró** los resultados).
- El problema es que la etiqueta **"unisex" es una categoría difusa**: mezcla perfumes muy distintos. Entre los perfumes etiquetados "unisex", según los votos de la gente, **14,1 %** se perciben claramente masculinos, **24,9 %** claramente femeninos y **61,0 %** realmente intermedios.

Entonces se agregó un **segundo modelo**, que es el principal: en vez de adivinar la etiqueta, **adivina la posición en la escala** (el índice) que sale de los votos de percepción de la gente. Con eso, el perfil de cuero + madera + humo sale en la zona masculina (índice 0,717), que era lo esperado.

| | Modelo 1: **Clasificador** | Modelo 2: **Índice** (principal) |
|---|---|---|
| Qué adivina | La etiqueta que le puso la marca | Una posición entre 0 y 1 hecha con los votos de la gente |
| Tipo de problema | **Clasificación** (elegir una categoría) | **Regresión** (predecir un número) |
| Archivo del modelo | `models/model.joblib` | `models/index_model.joblib` |
| Para qué se usa hoy | Complemento: probabilidades, lectura femenino vs. masculino, frecuencia base | Resultado principal: la barra del espectro |

## 1.5 ¿Qué tan bien funciona? (versión corta)

- **Modelo de índice:** se equivoca, en promedio, por unos **0,126 puntos** en una escala de 0 a 1. Ubica correctamente la zona (femenino / intermedia / masculino) en cerca del **70 %** de los casos. Es mejor que usar el clasificador para lo mismo: el error baja **20 %**.
- **Clasificador de la etiqueta:** acierta **64,7 %** de las veces, contra **51,2 %** que acertaría un modelo que siempre dice "unisex". Casi nunca confunde femenino con masculino (2 % y 5 %); casi todos sus errores caen en "unisex".

**Honestidad:** el modelo **no es perfecto** ni pretende serlo. Es una **orientación estadística** basada en cómo la gente percibe perfumes ya existentes. No reemplaza el olfato del perfumista. Un dato clave: de los perfumes que la gente percibe como masculinos, el modelo igual ubica al **44 %** en la zona intermedia, porque los acordes solos no alcanzan para distinguirlos de los unisex.

## 1.6 Las piezas del proyecto, en una frase cada una

| Pieza | En una frase |
|---|---|
| **Datos** (`data/`) | El archivo de perfumes que se descargó de Kaggle (no se sube a git por su tamaño). |
| **Pipeline** (`pipeline/`) | Una serie de programas que limpian los datos, entrenan los modelos y miden qué tan bien andan. |
| **Paquete `perfume_gender`** | Código común que usan tanto el pipeline como la aplicación (para que ambos "hablen el mismo idioma"). |
| **Modelos** (`models/`) | Los "cerebros" ya entrenados, guardados en archivos. |
| **Reportes** (`reports/`) | Los resultados de cada paso, en archivos `.json` (de donde salen las cifras del README). |
| **Backend** (`app/backend/`) | Un servidor web que recibe los acordes, consulta a los modelos y devuelve la respuesta. |
| **Frontend** (`app/frontend/`) | La página web que ves en el navegador. |
| **Tests** (`tests/`) | Programas que verifican que todo funcione y que el README no mienta. |
| **Docker / CI** | Formas de empaquetar y de verificar automáticamente el proyecto. |

---

# Parte 2: Conceptos de ciencia de datos explicados en criollo

Esta parte es un **diccionario con ejemplos**. Cada concepto tiene tres capas: qué es en criollo, por qué importa y cómo aparece en este proyecto con números reales. Están ordenados para que cada uno se apoye en los anteriores.

## 2.1 Los datos y sus partes

### Dataset (conjunto de datos)
**En criollo:** una tabla enorme, como una planilla de Excel. Cada **fila** es un caso (acá, un perfume) y cada **columna** es una característica de ese caso (nombre, marca, acordes, género, votos…).

**En este proyecto:** el archivo `perfumes.csv` tiene **131.930 filas** (perfumes) y **59 columnas**. Un `.csv` es un archivo de texto donde los valores van separados por comas: se puede abrir con Excel o con cualquier editor.

### Variable objetivo (target) y variables predictoras (features)
**En criollo:** cuando entrenás un modelo, separás las columnas en dos grupos:
- **Lo que querés adivinar** → la **variable objetivo** (en la jerga: `y`, "target" o "etiqueta").
- **Lo que le das al modelo para que adivine** → las **variables predictoras** (en la jerga: `X`, "features" o "características").

Es como un examen: las **features** son los datos del enunciado y el **target** es la respuesta que el alumno tiene que dar.

**En este proyecto:**

| | Modelo clasificador | Modelo de índice |
|---|---|---|
| **Features (X)** | Los acordes y su intensidad | Los acordes y su intensidad |
| **Target (y)** | La etiqueta `gender`: femenino / masculino / unisex | El índice de masculinidad percibida (un número de 0 a 1) |

Las **features son las mismas** para los dos modelos. Solo cambia la respuesta que se les pide.

### Vector y matriz
**En criollo:** un **vector** es una lista ordenada de números. Una **matriz** es una tabla de números (una pila de vectores). Los modelos de este proyecto no entienden texto como `woody:100|sweet:65`; hay que convertirlo a números.

**En este proyecto:** cada perfume se convierte en un vector de **72 números** (uno por cada acorde posible). Si el perfume tiene `woody:100|sweet:65`, el vector tiene `1,0` en la posición de *woody*, `0,65` en la posición de *sweet* y `0` en las otras 70 posiciones. Con 98.364 perfumes de entrenamiento, la matriz `X` tiene 98.364 filas y 72 columnas.

### Etiqueta contaminada / ruido en las etiquetas
**En criollo:** la "respuesta correcta" que le damos al modelo para aprender **no siempre es una verdad absoluta**. Si la etiqueta la puso una marca por criterios comerciales, puede no reflejar cómo huele realmente el perfume. A eso se le llama **ruido** o **sesgo** en las etiquetas.

**En este proyecto:** es justamente el problema de "unisex": una etiqueta que mezcla perfumes de naturaleza distinta (explicado en [1.4](#14-por-qué-hay-dos-modelos-y-no-uno)).

---

## 2.2 Cómo "aprende" un modelo

### Modelo
**En criollo:** una "fórmula matemática aprendida" que recibe datos y devuelve una estimación. No se programa a mano: se **ajusta** automáticamente a partir de ejemplos.

### Entrenar (fit)
**En criollo:** mostrarle al modelo miles de ejemplos **con la respuesta correcta**, para que ajuste sus "perillas internas" hasta equivocarse lo menos posible. Es como practicar con un examen resuelto.

**En el código:** el método `.fit(X, y)` de scikit-learn. Cuando ves `modelo.fit(X_tr, y_tr)` significa "entrená este modelo con estos ejemplos".

### Predecir (predict)
**En criollo:** usar el modelo ya entrenado con datos nuevos. En el código: `.predict(X)` devuelve la respuesta final (por ejemplo, "masculino") y `.predict_proba(X)` devuelve las probabilidades de cada opción.

### Aprendizaje supervisado
**En criollo:** "supervisado" significa que aprendemos con ejemplos que **tienen la respuesta correcta** (acá: perfumes con su género o con su índice). Es lo opuesto a "no supervisado", donde no hay respuestas y el modelo solo busca agrupaciones. **Todo este proyecto es supervisado.**

### Clasificación vs. regresión
| | Clasificación | Regresión |
|---|---|---|
| Qué predice | **Una categoría** (de un grupo cerrado) | **Un número** (en un rango continuo) |
| Ejemplo cotidiano | "¿Este mail es spam o no?" | "¿Cuánto va a costar esta casa?" |
| En este proyecto | Clasificador de género: femenino / masculino / unisex | Modelo de índice: 0,717 |

### Parámetros vs. hiperparámetros
**En criollo:**
- **Parámetros:** lo que el modelo **aprende solo** al entrenar (por ejemplo, los "cortes" internos de sus árboles). No los tocás.
- **Hiperparámetros:** las **perillas que ajusta la persona** *antes* de entrenar, que controlan cómo aprende el modelo (qué tan rápido, qué tan complejo, cuándo frenar). Ejemplos: `learning_rate`, `max_leaf_nodes`.

Es como una receta: los hiperparámetros son "temperatura del horno y tiempo"; los parámetros son "cómo quedó la masa".

---

## 2.3 Cómo saber si un modelo es bueno (sin engañarse)

### El peligro: memorizar en vez de aprender (overfitting)
**En criollo:** un alumno que se aprende de memoria las respuestas del examen de práctica saca 10 en la práctica, pero se saca 4 cuando le cambian las preguntas. Un modelo puede hacer lo mismo: "memorizar" los ejemplos de entrenamiento y fallar con los casos nuevos. A eso se le llama **sobreajuste** (*overfitting*).

**Cómo se evita:** **nunca se evalúa al modelo con los mismos ejemplos con los que entrenó**. Se guarda aparte un grupo de ejemplos que el modelo no vio nunca.

### Train / Test (entrenamiento y prueba)
**En criollo:** antes de entrenar, se divide el dataset en dos partes:
- **Train (80 %)**: con estos ejemplos el modelo aprende.
- **Test (20 %)**: se guardan "bajo llave" y se usan **una sola vez, al final**, para medir qué tan bien anda con datos que jamás vio. Es el examen final.

**En este proyecto:** de 122.955 perfumes limpios, **98.364 son de train** y **24.591 de test**. Esa división se hace una sola vez (en `pipeline/02_etl.py`) y se guarda en la columna `split`.

> **Regla de oro del proyecto:** el test **no se usa para tomar decisiones** (ni para elegir el modelo, ni para ajustar hiperparámetros). Solo para reportar el resultado final. Si uno decidiera mirando el test, el resultado sería "optimista" porque se estaría haciendo trampa sin querer.

### Estratificado
**En criollo:** al dividir en train y test, se cuida que **cada grupo mantenga la misma proporción de categorías**. Si el 15,5 % de los perfumes son masculinos, tanto el train como el test tienen ~15,5 % masculinos. Sin esto, por mala suerte el test podría quedar con muy pocos masculinos.

### Validación cruzada (cross-validation, CV)
**En criollo:** para comparar modelos sin tocar el test, se usa un truco: se parte el **train** en 5 pedazos (**folds**). Se entrena con 4 pedazos y se prueba con el 5.º; se repite 5 veces rotando cuál queda afuera; y se promedian los 5 resultados. Es como tomar 5 exámenes parciales distintos en vez de uno solo: da una nota más confiable y además muestra **cuánto varía** (el desvío).

```
Pedazos del train:   [A] [B] [C] [D] [E]
Vuelta 1: prueba en A, entrena con B C D E
Vuelta 2: prueba en B, entrena con A C D E
...
Vuelta 5: prueba en E, entrena con A B C D
→ promedio de los 5 resultados  (y su desvío)
```

**En este proyecto:** se usa CV de **5 folds** para comparar los modelos candidatos (resultado: por ejemplo `0,600 ± 0,002`, que significa "promedio 0,600, desvío 0,002"; un desvío chico indica que el modelo es estable).

### Semilla (seed) y reproducibilidad
**En criollo:** muchas partes del entrenamiento usan **azar** (qué filas van a train, cómo se inicializa el modelo). La **semilla** (`SEED = 42`) es un número que "fija" ese azar para que, si volvés a correr todo, **salga exactamente lo mismo**. Es como dejar un dado "cargado" siempre en la misma tirada. El número 42 es solo una convención (un guiño a *La guía del autoestopista galáctico*).

**En este proyecto:** se comprobó que correr el pipeline completo dos veces da resultados idénticos (salvo los tiempos de ejecución).

### Fuga de datos (data leakage)
**En criollo:** cuando el modelo "ve" información que **no debería tener** al momento de predecir, y por eso saca resultados irreales. Ejemplo: querer predecir el género de un perfume usando su descripción que dice literalmente "perfume para mujeres". Sería hacer trampa.

**En este proyecto, cómo se evita:**
- Se **descartan** columnas como `name`, `brand` y `description` como predictores (la descripción contiene "for women/men").
- Los votos de percepción (`perceived_*`) se usan **solo para construir el objetivo (el índice), nunca como entrada**.
- Se **eliminan los perfumes duplicados** antes de dividir en train/test, para que el mismo perfil no esté en los dos lados.

### Baseline (línea base)
**En criollo:** el resultado "mínimo vergonzoso" contra el cual comparar. Si tu modelo no supera al baseline, no sirve para nada.

**En este proyecto:** el baseline del clasificador es un modelo "tonto" que **siempre responde la categoría más frecuente** ("unisex"). Como unisex es el 51,2 % de los perfumes, ese modelo tonto acierta **51,2 %**. El modelo real acierta 64,7 %: mejora, pero no es una maravilla (por eso se habla de "orientación").

---

## 2.4 Probabilidades

### Probabilidad
**En criollo:** un número entre 0 y 1 (o 0 % y 100 %) que expresa **qué tan seguro está el modelo**. Si dice "masculino 70 %", significa "de cada 100 perfumes con este perfil, esperaría que ~70 sean masculinos".

**En este proyecto:** el clasificador devuelve **tres probabilidades que suman 100 %**: femenino, masculino y unisex. Se obtienen con `predict_proba`. La **respuesta final** (`predict`) es simplemente la de mayor probabilidad (`argmax`: "el índice del máximo").

### Calibración
**En criollo:** un modelo está **bien calibrado** si sus probabilidades "dicen la verdad". Si de todos los perfumes a los que les dio "70 %", realmente el 70 % resultó ser de esa clase, está bien calibrado. Un modelo mal calibrado puede decir "99 %" y acertar solo el 80 %.

**Cómo se mide:**
- **Curva de calibración:** un gráfico que compara "lo que dijo el modelo" (eje horizontal) con "lo que realmente pasó" (eje vertical). Si los puntos siguen la diagonal, está calibrado.
- **ECE (Expected Calibration Error, error de calibración esperado):** un número que resume cuánto se aparta de la diagonal. Cerca de 0 es excelente.

**En este proyecto:** el ECE del clasificador es **0,004** para femenino, **0,004** para masculino y **0,010** para unisex (menos de 1 punto porcentual): las probabilidades son muy confiables. Por eso se las muestra al usuario.

---

## 2.5 Métricas del clasificador (las que más se confunden)

Se usan para responder "¿qué tan bien clasifica?". Se explican con el **mismo ejemplo real del proyecto**: la **matriz de confusión** del clasificador en el test.

### Matriz de confusión
**En criollo:** una tabla que cruza **lo que realmente era** (filas) con **lo que el modelo dijo** (columnas). La diagonal son los aciertos.

| Real ↓ / Predicho → | Femenino | Masculino | Unisex | Total real |
|---|---|---|---|---|
| **Femenino** | **5.448** | 143 | 2.596 | 8.187 |
| **Masculino** | 183 | **1.396** | 2.232 | 3.811 |
| **Unisex** | 2.680 | 846 | **9.067** | 12.593 |

Lectura: de 8.187 perfumes realmente femeninos, el modelo acertó 5.448, dijo "masculino" 143 veces y dijo "unisex" 2.596 veces.

### Exactitud (accuracy)
**En criollo:** de todos los casos, **qué porcentaje acertó**. Se suman los aciertos de la diagonal y se divide por el total:

`(5.448 + 1.396 + 9.067) / 24.591 = 15.911 / 24.591 = 64,7 %`

**Su defecto:** si una categoría es muy frecuente, la exactitud puede engañar. Un modelo que siempre dice "unisex" ya tiene 51,2 %. Por eso se usan además las siguientes métricas.

### Precisión (precision)
**En criollo:** cuando el modelo **dice** "masculino", **¿qué tan seguido tiene razón?** Es "de los que marqué como masculinos, cuántos realmente lo eran".

Masculino: el modelo lo marcó `143 + 1.396 + 846 = 2.385` veces; acertó 1.396 → `1.396 / 2.385 = 58,5 %`.

### Exhaustividad (recall)
**En criollo:** de **todos los que realmente eran** masculinos, **¿cuántos logró encontrar?** Es "qué porcentaje de los masculinos reales detecté".

Masculino: había 3.811 reales; detectó 1.396 → `1.396 / 3.811 = 36,6 %`. Este número bajo es la clave de todo el problema: **al modelo se le "escapan" muchos masculinos hacia unisex**.

> **Precisión vs. recall con una analogía:** un detector de metales en un aeropuerto. Alta **precisión** = cuando suena, casi siempre hay metal (pocas falsas alarmas). Alto **recall** = detecta casi todo el metal que hay (no se le escapa nada). Es difícil tener las dos al máximo: si lo hacés muy sensible, detecta todo pero suena por cualquier cosa.

### F1
**En criollo:** un único número que combina precisión y recall (con un promedio especial llamado **media armónica**, que castiga si uno de los dos es bajo). Fórmula: `F1 = 2 × (precisión × recall) / (precisión + recall)`.

Masculino: `2 × (0,585 × 0,366) / (0,585 + 0,366) = 0,451`.

### F1 macro
**En criollo:** el F1 se calcula **por cada categoría** y después se promedian los tres **dándole el mismo peso a cada una**, sin importar cuántos perfumes tenga. "Macro" = "promedio simple de las categorías".

`F1 macro = (F1 femenino + F1 masculino + F1 unisex) / 3 = (0,660 + 0,451 + 0,685) / 3 = 0,599`

**Por qué se usa en vez de la exactitud:** porque castiga cuando el modelo anda mal en una categoría chica (masculino es solo 15,5 % de los datos). Con la exactitud, errar muchos masculinos casi no se nota; con F1 macro sí.

### Soporte (support)
**En criollo:** simplemente **cuántos casos reales** hay de cada categoría en el test. Femenino: 8.187; masculino: 3.811; unisex: 12.593.

---

## 2.6 Métricas del modelo de índice (regresión)

El modelo de índice predice un número, así que se mide distinto: no hay "acierto/error" sino **"qué tan lejos quedó"**.

### Error medio absoluto (MAE)
**En criollo:** el **promedio de cuánto se equivoca** el modelo, sin importar si por arriba o por abajo. Si para un perfume el índice real es 0,80 y el modelo dijo 0,70, el error es 0,10. El MAE es el promedio de esos errores sobre todos los perfumes.

**En este proyecto:** MAE = **0,126**. Es decir: en una escala de 0 a 1, el modelo se equivoca en promedio unos 13 centésimos.

### R² (coeficiente de determinación)
**En criollo:** qué porcentaje de las **diferencias entre perfumes** logra explicar el modelo. 1 = explica todo; 0 = no explica nada (equivale a decir siempre el promedio). **En este proyecto:** 0,656 en la referencia: explica casi dos tercios de la variación del índice.

### Correlación de Spearman
**En criollo:** mide si el modelo **ordena bien** los perfumes, aunque se equivoque en el valor exacto. Si ordenás los perfumes del más femenino al más masculino según los votos reales, y los ordenás según el modelo, ¿se parecen los dos órdenes? 1 = mismo orden perfecto; 0 = orden sin relación. **En este proyecto:** 0,810, un orden bastante parecido.

### F1 macro por zonas
**En criollo:** se convierte el índice (un número) en una **zona** (femenino/intermedia/masculino) tanto para lo real como para lo predicho, y se calcula el F1 macro como si fuera un clasificador de 3 categorías. Sirve para comparar de manera justa con el clasificador. **En este proyecto:** 0,676 el índice vs. 0,613 el clasificador.

---

## 2.7 Desbalance de clases y las "soluciones" que se probaron

### Desbalance
**En criollo:** cuando una categoría tiene **muchos más ejemplos** que otras. Acá: unisex 51,2 %, femenino 33,3 %, masculino 15,5 %.

### Las dos "soluciones" clásicas
1. **Pesos de clase (`class_weight="balanced"`):** le dice al modelo "equivocarte en un masculino cuesta más que equivocarte en un unisex", para compensar que hay menos masculinos.
2. **Submuestreo (undersampling):** tirar ejemplos de las categorías grandes hasta que todas tengan la misma cantidad. Acá implicaba quedarse con solo **36.591 filas** (descartando más de la mitad).

### ¿Funcionaron? No. Se midió (F1 macro / exactitud):

| Estrategia | F1 macro | Exactitud |
|---|---|---|
| Sin tocar nada | **0,598** | **0,644** |
| Con `class_weight` | 0,581 | 0,589 |
| Submuestreo | 0,577 | 0,584 |

**Por qué empeoró:** "equilibrar" fuerza al modelo a marcar más perfumes como masculinos, y se equivoca más. Además **distorsiona las probabilidades** (dejan de ser "verdad"). Por eso **no se equilibra**. Esto fue clave para entender que el problema no era la cantidad de perfumes unisex sino la etiqueta.

---

## 2.8 Los algoritmos que se compararon

Un **algoritmo** es la "familia" de modelo (la técnica matemática). Se compararon seis. No hace falta entender las matemáticas; sí la idea de cada uno:

| Algoritmo | Idea en criollo | Resultado (F1 macro, CV) |
|---|---|---|
| **Baseline** (`DummyClassifier`) | Siempre dice la categoría más frecuente. Es el "modelo tonto" de referencia. | 0,226 |
| **Regresión logística** | Le asigna un "peso" a cada acorde y suma: "*floral* suma puntos hacia femenino, *aromatic* hacia masculino". Es simple y rápido. Pese al nombre, es un clasificador. | 0,572 |
| **Random Forest** (bosque aleatorio) | Arma **cientos de árboles de decisión** (preguntas tipo "¿tiene mucho *woody*? sí → ¿tiene *sweet*? no → …") sobre muestras al azar y **vota**. | 0,572 |
| **SVM** (máquinas de vectores soporte) | Busca la "frontera" que mejor separa las categorías en un espacio de muchas dimensiones. Es lenta con muchos datos, por eso se probó con una **submuestra de 20.000 filas**. | 0,559 |
| **Gradient Boosting (HGB)** | Arma árboles **uno tras otro**, y cada uno intenta **corregir los errores del anterior**. Suele ser el mejor para datos en forma de tabla. | 0,598 (0,600 ajustado) |
| **MLP** (red neuronal) | Capas de "neuronas" matemáticas conectadas. Más flexible, pero más difícil de explicar. | 0,600 |

**Ganador: Gradient Boosting ajustado** (en inglés, `HistGradientBoostingClassifier`). Quedó **empatado técnicamente con el MLP** (0,600 vs. 0,600; la diferencia está dentro del desvío). Se eligió Gradient Boosting porque es más estable, rápido y su archivo pesa solo ~1 MB.

> **Lectura honesta:** los modelos "sofisticados" apenas superan a la regresión logística (unos 3 puntos). Moraleja: **el límite lo pone la información disponible** (solo acordes), no lo sofisticado del algoritmo.

### Los hiperparámetros del Gradient Boosting (las "perillas")
| Hiperparámetro | En criollo | Valor usado (clasificador / índice) |
|---|---|---|
| `max_iter` | Cantidad máxima de árboles que se van agregando. | 300 / 300 |
| `learning_rate` | "Qué tan fuerte" corrige cada árbol a los anteriores. Bajo = aprende lento pero fino. | 0,08 / 0,08 |
| `max_leaf_nodes` | Complejidad máxima de cada árbol (cantidad de "hojas", o sea de respuestas finales posibles). | 63 / 31 |
| `min_samples_leaf` | Mínimo de perfumes que debe haber en cada hoja. Evita que memorice casos aislados. | 20 / 40 |
| `l2_regularization` | Una "multa" por complicarse demasiado (evita el sobreajuste). | 0 (default) |
| `early_stopping` | Frenar antes si el modelo deja de mejorar en un conjunto de control interno. | Activado |
| `validation_fraction` | Qué porción del train se aparta para ese control interno. | 10 % |
| `n_iter_no_change` | Cuántas rondas sin mejorar toleramos antes de frenar. | 20 |

### Ajuste de hiperparámetros: búsqueda aleatoria
**En criollo:** ¿cómo encontrar las mejores "perillas"? **Probar combinaciones.** Probar **todas** sería carísimo, así que se usa **búsqueda aleatoria** (`RandomizedSearchCV`): se sortean 10 combinaciones, se evalúa cada una con validación cruzada (3 folds) y se elige la mejor. Es "probar 10 recetas al azar y quedarse con la más rica".

---

## 2.9 Limpieza de datos: conceptos y decisiones

### Valores faltantes (nulos, NaN)
**En criollo:** celdas **vacías**. Acá, 2.769 perfumes no tenían acordes. Como los acordes son la información principal, **se descartaron** (inventar acordes sería inventar datos).

### Duplicados
**En criollo:** filas repetidas. Acá, 6.206 perfumes tenían un perfil de acordes **idéntico** a otro (por ejemplo, el mismo perfume en distintas concentraciones). Si no se eliminan, el mismo perfil puede caer en train y en test, y el modelo "aprobaría" porque ya vio la respuesta (**fuga de datos**). Se deja **uno por perfil**.

### Etiquetas contradictorias
**En criollo:** 727 perfiles de acordes aparecen con **géneros distintos** (5.741 filas). Criterio: se queda con la etiqueta **más respaldada por votos**.

### Outliers (valores atípicos)
**En criollo:** datos "raros" que se alejan mucho de lo normal. En este proyecto hubo de varios tipos:

| Tipo | Ejemplo | Decisión |
|---|---|---|
| **Acordes ultra-raros** | `tennis ball`, `wet plaster`, `bbq`: aparecen en muy pocos perfumes | Se descartan los acordes que aparecen en menos de 50 perfumes (de 92 quedan **72**). No aportan señal y llevan a memorizar. |
| **Perfumes con pocos acordes** | 6.173 tienen menos de 8 | Se conservan: no son errores, solo tienen menos votos. |
| **Perfumes con pocos votos** | Mediana de 5 votos de percepción | Se prueban varias estrategias (ver 2.10). |
| **Intensidades** | El acorde principal siempre vale 100 | No hay valores fuera de rango: no se recorta nada. |

### Media, mediana y percentiles
Tres formas de resumir "qué es lo típico":
- **Media (promedio):** suma de todo dividida por la cantidad. **Se distorsiona con valores extremos.**
- **Mediana:** el valor del medio si ordenás todo de menor a mayor. **Resiste a los extremos.**
- **Percentil 75 / 90:** el valor por debajo del cual está el 75 % / 90 % de los datos.

**En este proyecto (votos de percepción por perfume):** media **64,5**, mediana **5**, percentil 75 = 24, percentil 90 = 98. La media es alta porque unos pocos perfumes tienen miles de votos, pero **el perfume típico tiene 5**. Ejemplo de por qué la media engaña: si en una habitación hay 9 personas que ganan $100 y una que gana $10.000, la media es $1.090, pero nadie gana eso: la mediana ($100) describe mejor al grupo.

### Escala logarítmica
**En criollo:** cuando los datos van de 0 a 35.000 con casi todos cerca de 0, un gráfico común no se ve. Con una escala **logarítmica** se "comprimen" los valores grandes y se ve bien toda la distribución. En los gráficos del EDA se usa `log10(votos + 1)` (el "+1" es para poder calcular el logaritmo cuando hay 0 votos).

---

## 2.10 Votos: filtrar vs. ponderar

Un perfume con **pocos votos** tiene un índice **poco confiable** (con 1 voto, el índice solo puede valer 0, 0,25, 0,5, 0,75 o 1). Se probaron dos estrategias:

1. **Filtrar:** usar solo perfumes con "al menos N votos". Resultado: no mejora (a partir de N = 50 empeora porque se pierden demasiados datos).
2. **Ponderar:** usar todos los perfumes, pero darle **más peso** al que tiene más votos (**peso de muestra**, `sample_weight`). El peso elegido es la **raíz cuadrada de los votos con un tope en 100**: `peso = √min(votos, 100)`. Con 1 voto pesa 1, con 4 votos pesa 2, con 100 o más pesa 10. Así un perfume con muchísimos votos no domina el entrenamiento.

La mejora de ponderar es chica (≈ 1,5 % del error), pero usa todas las filas con índice y no obliga a elegir un umbral arbitrario.

---

## 2.11 Otras ideas que aparecen en el proyecto

### Importancia por permutación
**En criollo:** ¿qué acordes le importan más al modelo? Se toma una columna (por ejemplo *floral*), se **mezcla al azar** (así deja de tener relación con el resultado) y se mide **cuánto empeora el modelo**. Si empeora mucho, ese acorde era importante. **En este proyecto:** los más importantes son `floral`, `aromatic`, `white floral`, `citrus`, `rose`, `lavender`, `sweet`, `oud`.

### Ablación (experimento de "qué pasa si saco o agrego")
**En criollo:** comparar el modelo con y sin un ingrediente para ver cuánto aporta. Ejemplo: "solo acordes" vs. "acordes + notas" vs. "solo notas".

| Variables | F1 macro | Exactitud |
|---|---|---|
| Solo acordes | 0,598 | 0,644 |
| Acordes + notas | 0,670 | 0,701 |
| Solo notas | 0,667 | 0,698 |

**Lectura:** las notas aportan información extra (~7 puntos de F1). Se decidió **no usarlas** porque se supone que el perfumista aún no las define cuando pide la primera muestra (hipótesis a validar con un perfumista real).

### Partición por grupos (marca)
**En criollo:** la partición común mezcla perfumes al azar. Pero una marca suele tener perfumes parecidos entre sí (flankers). Para probar si el modelo funciona con **marcas que nunca vio**, se arma otra partición donde **todas las filas de una marca van al mismo lado**. Resultado: F1 macro 0,598 (contra 0,599): el modelo generaliza bien a marcas nuevas.

### Correlación de Pearson (el mapa de calor del EDA)
**En criollo:** mide si **dos cosas suben y bajan juntas**: +1 = siempre juntas, −1 = una sube cuando la otra baja, 0 = no se relacionan. El gráfico "co-ocurrencia entre acordes" muestra, por ejemplo, que `white floral` y `floral` suelen aparecer juntos.

### Frecuencia base y "lift"
**En criollo:** la **frecuencia base** es "cuántos perfumes de esa categoría hay en total" (femenino 33,3 %, masculino 15,5 %, unisex 51,2 %). El **lift** compara lo que dice el modelo con esa base: `lift = probabilidad del modelo ÷ frecuencia base`.
- Lift **1** = "igual a lo habitual".
- Lift **2** = "el doble de lo habitual".
- Lift **0,5** = "la mitad de lo habitual".

**Ejemplo (tu composición):** el clasificador dice masculino 7 %. Como la base de masculino es 15,5 %, el lift es 0,45: "la mitad de lo habitual". Y unisex 90 % ÷ 51,2 % = lift 1,76. La respuesta "unisex" no es un hallazgo: es la opción "segura" del modelo.

### Lectura "femenino vs. masculino"
**En criollo:** se **ignora unisex** y se reparte 100 % entre los otros dos. Fórmula: `p_masculino ÷ (p_masculino + p_femenino)`. Con p_fem = 3 % y p_masc = 7 %: `7 ÷ (3 + 7) = 70 %` masculino, 30 % femenino. Es útil porque el modelo casi nunca confunde femenino con masculino (2 % y 5 %).

### Zonas del índice
Los límites son **0,33 y 0,67**: menos de 0,33 = femenino; entre 0,33 y 0,67 = unisex (intermedia); más de 0,67 = masculino. Se eligieron "tercios" aproximados.

---

# Parte 3: Conceptos de programación y herramientas

Esta parte explica el vocabulario técnico que vas a encontrar en el código. Si ya programás, podés saltearla; si no, leela antes de la Parte 5: hace que el código se entienda mucho mejor.

## 3.1 Python: lo que necesitás saber para leer este código

**Python** es el lenguaje en el que está escrito casi todo el proyecto (el pipeline, los modelos y el servidor). Es muy legible: se parece bastante al inglés.

### Variables y tipos de datos
```python
SEED = 42                       # un número entero
nombre = "woody"                # un texto ("string" o "cadena")
intensidad = 84.5               # un número con decimales ("float")
es_valido = True                # verdadero o falso ("bool")
acordes = ["woody", "leather"]  # una lista ordenada
perfil = {"woody": 100, "sweet": 65}   # un diccionario: pares clave → valor
```
- Una **lista** (`[...]`) guarda elementos en orden. Se accede por posición: `acordes[0]` es `"woody"` (se empieza a contar desde **0**).
- Un **diccionario** (`{...}`) guarda pares **clave: valor**. Se accede por clave: `perfil["woody"]` es `100`. Es como una agenda: buscás por nombre y te da el teléfono.
- Un **conjunto** (`set`) es una colección sin repetidos.
- Una **tupla** (`(a, b)`) es una lista que no se puede modificar.

### Funciones
```python
def vote_weight(votes, cap=100):
    """Texto que explica qué hace la función."""
    return np.sqrt(np.minimum(votes, cap))
```
- `def` define una función; lo que está entre paréntesis son sus **parámetros** (los datos que recibe). `cap=100` significa "si no te dan `cap`, usá 100" (valor por defecto).
- `return` es lo que la función **devuelve**.
- El texto entre triples comillas `"""..."""` justo debajo es el **docstring**: la documentación de la función.

### Indentación (los espacios al inicio)
En Python, los **espacios al comienzo de la línea** indican qué código está "adentro" de qué. Lo que está más hacia la derecha pertenece al bloque de arriba (por ejemplo, el cuerpo de una función o de un `if`).

### Condicionales y bucles
```python
if total <= 0:          # si... entonces
    return 0.5
for item in lista:      # para cada elemento de la lista...
    print(item)
```

### Listas por comprensión (list comprehension)
Una forma compacta de construir una lista aplicando una regla:
```python
nombres = [normalize_accord(n) for n in lista if n]
```
Se lee: "para cada `n` de `lista`, si `n` no está vacío, calculá `normalize_accord(n)` y juntá todo en una lista". Existe lo mismo para diccionarios (`{k: v for ...}`) y conjuntos.

### `lambda` (funciones de una línea sin nombre)
`lambda d: max(d.values())` es una mini-función anónima: "dado `d`, devolvé el máximo de sus valores". Se usa para pasar una regla corta a otra función.

### f-strings (texto con variables adentro)
```python
f"{valor:.3f}"   # inserta `valor` con 3 decimales
f"{v:g}"         # inserta v en formato compacto (100.0 se escribe 100)
```

### Importar módulos
`import numpy as np` trae una **librería** (código ya hecho por otros) y le pone el apodo `np`. `from pathlib import Path` trae solo una pieza de esa librería.

### Clases y objetos
Una **clase** es un "molde" para crear objetos que combinan datos y funciones. Ejemplo: la clase `Predictor` guarda los dos modelos y el vocabulario, y tiene funciones como `predict`.
- `@dataclass` es un atajo de Python que escribe automáticamente el código aburrido de una clase que solo guarda datos.
- `@classmethod` marca una función que se llama sobre la clase misma (por ejemplo `Predictor.load()`) y no sobre un objeto ya creado.
- `self` es "el objeto sobre el que estoy trabajando".

### Anotaciones de tipo (`type hints`)
Cosas como `def f(x: float) -> str:` o `dict[str, float]` son **etiquetas informativas**: indican "x es un número con decimales, devuelve texto" o "un diccionario de texto a número". Python **no las exige** en tiempo de ejecución; ayudan a quien lee el código y a las herramientas. `from __future__ import annotations` al inicio de un archivo permite escribirlas de forma más cómoda.

### Manejo de errores (`try / except`)
```python
try:
    app.state.predictor = Predictor.load()
except FileNotFoundError as exc:
    ...  # si falta un archivo, no explota: hace esto en su lugar
```
"Intentá esto; si sale ese error en particular, hacé esto otro". Con `raise` se **lanza** un error a propósito.

### `if __name__ == "__main__":`
Al final de muchos scripts. Significa: "ejecutá `main()` solo si **corrés este archivo directamente**, no si otro archivo lo importa".

### Rutas con `pathlib`
`Path(__file__)` es la ruta del archivo actual. Con `/` se arman rutas: `ROOT / "data" / "raw"`. `.parents[1]` sube dos niveles de carpetas. Se usa para **no escribir rutas absolutas** (como `C:\Users\Ale\...`) y que el proyecto funcione en cualquier computadora.

### Decoradores (`@algo`)
Una línea que empieza con `@` justo arriba de una función le **agrega una capacidad**. En el backend, `@app.get("/api/health")` significa "esta función atiende las visitas a la dirección `/api/health`".

### `async` / `await`
Palabras para código que puede "esperar" sin trabar todo el programa. En el proyecto aparece poco (en el arranque del servidor y en el navegador al pedir datos). Idea: "pedí esto y, mientras tanto, seguí con lo demás".

## 3.2 Las librerías de Python del proyecto

| Librería | Para qué sirve (en criollo) | Ejemplos de uso en el proyecto |
|---|---|---|
| **NumPy** (`np`) | Cálculo con **vectores y matrices** de números, muy rápido. | `np.zeros`, `np.sqrt`, `np.clip`, `np.quantile` |
| **pandas** (`pd`) | Trabajar con **tablas** (como un Excel programable). Su objeto principal es el **DataFrame**. | Leer el CSV, filtrar filas, agrupar |
| **scikit-learn** (`sklearn`) | La caja de herramientas de **Machine Learning**: modelos, métricas, validación cruzada. | Todos los modelos y métricas |
| **SciPy** | Funciones científicas extra. | La correlación de Spearman |
| **joblib** | **Guardar y cargar** modelos entrenados en archivos. | `joblib.dump` / `joblib.load` |
| **matplotlib / seaborn** | Hacer **gráficos**. | Todas las figuras de `docs/figures/` |
| **FastAPI** | Crear el **servidor web** (la API). | `app/backend/main.py` |
| **uvicorn** | El programa que **corre** el servidor FastAPI. | `python -m uvicorn ...` |
| **Pydantic** | **Validar** los datos que llegan al servidor. | `schemas.py` |
| **pytest** | Correr los **tests automáticos**. | Carpeta `tests/` |
| **httpx** | Permite a los tests "visitar" el servidor sin abrir un navegador. | Tests de la API |

### pandas en dos minutos
Un **DataFrame** es una tabla. Operaciones que aparecen en el código:
- `df["gender"]` → la columna `gender` (una **Series**, o sea una columna).
- `df[df["split"] == "train"]` → solo las filas donde `split` vale `"train"` (un **filtro**).
- `df.dropna(subset=["accords"])` → saca las filas donde `accords` está vacío.
- `df["accords"].map(funcion)` → aplica una función a cada celda de la columna.
- `df.groupby([...])...` → agrupa filas y calcula algo por grupo.
- `.value_counts()` → cuenta cuántas veces aparece cada valor.
- `.drop_duplicates(...)` → elimina filas repetidas.
- `df.loc[filas, columna]` → selecciona por etiqueta.

### NumPy en dos minutos
Un **array** es una lista de números con superpoderes: se pueden hacer cuentas con todos a la vez (`x * 2` multiplica cada elemento). Detalles que aparecen:
- `X[:, 0]` = "todas las filas, columna 0".
- `X[mascara]` con una máscara de verdadero/falso = "solo las filas donde la máscara es verdadera".
- `float32` es un formato de número que ocupa la mitad de memoria que `float64`.
- `@` entre dos arrays es **multiplicación de matrices**.

### scikit-learn: el patrón que se repite
Casi todo sigue estos pasos:
```python
modelo = AlgunModelo(hiperparametros...)   # 1. crear el modelo (sin entrenar)
modelo.fit(X_train, y_train)               # 2. entrenarlo
predicciones = modelo.predict(X_test)      # 3. usarlo
```
Además: `clone(modelo)` = "una copia sin entrenar, con las mismas perillas"; `cross_validate(...)` = "hacer validación cruzada"; `train_test_split(...)` = "dividir en train y test".

## 3.3 Archivos de datos y formatos

### CSV
Texto plano con valores separados por coma, una fila por línea. `perfumes.csv` y `clean.csv.gz` (el `.gz` significa que está **comprimido**) usan este formato.

### JSON
Un formato de texto para guardar **datos estructurados**, como diccionarios y listas anidadas:
```json
{"index": 0.7173, "zone": "male", "accords_used": {"woody": 100.0}}
```
Lo entienden casi todos los lenguajes. Todos los archivos de `reports/` y `models/metadata.json` son JSON. Es **la forma estándar en que el servidor y la página web se comunican**.

### `.joblib`
Un archivo **binario** (no se puede leer con un editor de texto) donde se guarda un modelo ya entrenado. Para usarlo hay que cargarlo con `joblib.load`.

### `.png` / `.jpg`
Imágenes: los gráficos y las capturas de la demo.

## 3.4 Cómo se comunican la página y el servidor (API)

### Servidor, cliente y API
- **Servidor (backend):** un programa que **espera pedidos** y responde. Acá corre en tu computadora, en la dirección `http://localhost:8000`.
- **Cliente (frontend):** quien hace los pedidos. Acá es la **página web** en tu navegador.
- **API:** el "menú" de pedidos que el servidor sabe atender. Por ejemplo: "dame la lista de acordes", "predecí con estos acordes".
- **`localhost`** significa "esta misma computadora". **`8000`** es el **puerto**: como el "número de puerta" por donde entra el servidor.

### HTTP y sus métodos
Es el "idioma" de la web. Los métodos que se usan:
- **GET**: pedir información (no cambia nada). Ej.: `GET /api/accords`.
- **POST**: enviar datos para que el servidor los procese. Ej.: `POST /api/predict` envía los acordes.

### Códigos de estado (los números de respuesta)
| Código | Significa | Cuándo aparece acá |
|---|---|---|
| **200** | Todo bien | Respuesta normal |
| **422** | Los datos enviados no son válidos | Acorde desconocido, lista vacía, más de 8 acordes |
| **503** | Servicio no disponible | Faltan los modelos |

### Endpoint
Cada "dirección" de la API: `/api/health`, `/api/accords`, `/api/predict`, `/api/model/info`.

### CORS
Una regla de seguridad de los navegadores. Acá se permite solo el acceso desde `localhost` / `127.0.0.1` (tu propia computadora).

### Validación de entradas
Nunca hay que confiar en lo que llega al servidor. Se verifica que los acordes existan, que las intensidades estén entre 0 y 100 y que no sean más de 8. Lo hacen Pydantic (`schemas.py`) y el predictor (`predictor.py`).

## 3.5 Frontend: HTML, CSS y JavaScript

Una página web se arma con **tres lenguajes**, cada uno con un rol:

| Lenguaje | Rol | Analogía (una casa) | Archivo |
|---|---|---|---|
| **HTML** | La **estructura**: títulos, botones, tablas | Los ladrillos y las paredes | `index.html` |
| **CSS** | El **aspecto**: colores, tamaños, espacios | La pintura y la decoración | `styles.css` |
| **JavaScript (JS)** | El **comportamiento**: qué pasa al tocar un botón | La electricidad y las llaves de luz | `app.js` |

### Conceptos de HTML
- **Etiquetas (tags):** `<h1>`, `<p>`, `<button>`; se abren y se cierran (`<p>texto</p>`).
- **`id` y `class`:** nombres para encontrar o estilizar un elemento. El `id` es único; una `class` se puede repetir.
- **Atributos ARIA** (`aria-label`, `role`): información extra para **lectores de pantalla** (accesibilidad).
- **`hidden`:** oculta un elemento.

### Conceptos de CSS
- **Variables** (`--female: #f472b6`): valores con nombre que se reutilizan.
- **Grid y flex:** formas de acomodar elementos en filas y columnas.
- **Media queries** (`@media (max-width: 800px)`): reglas que se activan solo en pantallas chicas (celulares).
- **`prefers-reduced-motion`:** respeta a quienes pidieron menos animaciones en su sistema.
- **Gradiente:** degradé de colores (la barra del espectro).

### Conceptos de JavaScript
- **`const` / `let`:** declarar variables (`const` no se reasigna).
- **Funciones flecha:** `(x) => x * 2`, equivalentes a `lambda`.
- **DOM:** la representación de la página como un "árbol" de elementos que JS puede leer y modificar. `document.getElementById("verdict")` encuentra un elemento.
- **`addEventListener`:** "cuando pase tal cosa (un clic), ejecutá esta función".
- **`fetch`:** pedirle datos al servidor.
- **`Map`:** un diccionario con orden.
- **Plantillas de texto:** `` `Índice ${valor}` `` inserta variables en un texto.
- **`?.` y `??`:** "acceder solo si existe" y "usar este valor si el otro es nulo".
- **`textContent` en vez de `innerHTML`:** se usa para insertar texto de forma **segura** (así nadie puede inyectar código malicioso).
- **Debounce:** esperar un instante (180 ms) a que el usuario deje de mover un control antes de consultar al servidor, para no saturarlo.
- **`localStorage`:** una pequeña memoria del navegador, propia de cada sitio, donde la página guarda cosas como el tema elegido (claro u oscuro). Sobrevive aunque cierres la pestaña.
- **`matchMedia`:** permite preguntarle al navegador cosas como "¿el usuario prefiere tema claro?" o "¿pidió menos animaciones?".
- **`IntersectionObserver`:** una herramienta que avisa **cuándo un elemento entra o sale de la pantalla**. Se usa para mostrar la barra flotante del celular.
- **`history.replaceState`:** cambia la dirección de la página (por ejemplo, agrega `#modelo`) sin recargarla.
- **SVG:** un formato de imagen **vectorial** (hecho de líneas y formas, no de píxeles), que se ve nítido a cualquier tamaño. El logo y los íconos son SVG.
- **Atributos `data-*`:** datos propios que se guardan en un elemento (`data-theme`, `data-zone`) y que el CSS puede leer para cambiar el aspecto.

## 3.6 Entornos, dependencias y empaquetado

### Entorno virtual (`.venv`)
**En criollo:** una "burbuja" de Python, propia de este proyecto, donde se instalan las librerías **sin mezclarlas con las de otros proyectos**. Se crea con `python -m venv .venv`.

### `requirements.txt` y versiones fijadas
Lista de las librerías necesarias. `numpy==2.5.2` significa "exactamente esta versión". Fijar versiones asegura que el proyecto **se comporte igual en todas las computadoras**. Es especialmente crítico con scikit-learn: el archivo `.joblib` solo se puede cargar de forma confiable con la **misma versión** con la que se guardó.

El proyecto tiene dos listas:
- `requirements-app.txt`: lo mínimo para **usar** la app.
- `requirements.txt`: la anterior **más** lo necesario para el pipeline (pandas, matplotlib) y los tests (pytest).

### Git y GitHub
- **Git:** un sistema que **guarda el historial** de cambios del proyecto. Cada **commit** es una "foto" con un mensaje que explica qué cambió.
- **GitHub:** un sitio web donde se **sube** (`git push`) el repositorio para compartirlo.
- **`.gitignore`:** lista de cosas que Git **no debe subir** (el dataset gigante, el entorno virtual, los documentos de trabajo).
- **`.gitattributes`:** reglas de cómo guardar los archivos (por ejemplo, el tipo de salto de línea; Windows y Linux usan distintos y esto evita avisos).

### Docker
- **Imagen:** una "caja cerrada" con todo lo necesario para correr la app: Python, las librerías en sus versiones exactas y el código.
- **Contenedor:** la imagen **funcionando**.
- **`Dockerfile`:** la **receta** para armar la imagen, línea por línea.
- **`.dockerignore`:** qué **no** meter en la imagen (el dataset, los tests…).
- **Para qué sirve:** que cualquiera, en cualquier computadora, corra la app **idéntica**, sin instalar Python ni librerías ("en mi máquina anda" deja de ser un problema).

### CI (integración continua) y GitHub Actions
Un **robot de GitHub** que, cada vez que subís cambios, **corre automáticamente los tests** en un servidor limpio. Si algo falla, te avisa. Está definido en `.github/workflows/tests.yml`.

### Tests automáticos
Programas que **verifican que el código hace lo que dice**. Si alguien cambia algo y rompe una función, el test falla y avisa. Se corren con `python -m pytest tests -q`.

---

# Parte 4: Mapa del proyecto y recorrido de los datos

## 4.1 Qué es cada carpeta y cada archivo (vista de pájaro)

```
ScentAI/
├── README.md                    La presentación técnica del proyecto (4 secciones).
├── GUIA_EN_CRIOLLO.md           Este documento.
├── MODEL_CARD.md                Ficha del modelo: usos, datos, límites y sesgos.
│
├── requirements.txt             Librerías para TODO (app + pipeline + tests).
├── requirements-app.txt         Librerías mínimas para USAR la app.
├── run.bat / run.sh             Atajos para levantar la app (Windows / Linux-Mac).
├── Dockerfile / .dockerignore   Receta para empaquetar la app en Docker.
├── .gitignore / .gitattributes  Reglas para Git.
├── .github/workflows/tests.yml  El "robot" que corre los tests en GitHub.
│
├── perfume_gender/              CÓDIGO COMPARTIDO (pipeline + app lo usan).
│   ├── config.py                Rutas y constantes.
│   ├── parsing.py               Lee el texto de acordes ("woody:100|sweet:65").
│   ├── perception.py            Calcula el índice de masculinidad percibida.
│   ├── features.py              Convierte acordes en vectores de números.
│   ├── data.py                  Lee y limpia el dataset crudo.
│   ├── modeling.py              Carga datos de entrenamiento y define los modelos candidatos.
│   └── predictor.py             Junta modelos + vocabulario y hace las predicciones.
│
├── pipeline/                    LOS PASOS DE DATOS Y ENTRENAMIENTO (se corren en orden).
│   ├── 01_eda.py                Explora los datos y hace gráficos.
│   ├── 02_etl.py                Limpia los datos y los divide en train/test.
│   ├── 03_experiments.py        Experimentos (¿notas? ¿equilibrar? ¿filtrar votos?).
│   ├── 04_train.py              Entrena y elige el clasificador de la etiqueta.
│   ├── 05_train_index.py        Entrena el modelo principal (índice).
│   ├── 06_evaluate.py           Evaluación extra del clasificador (calibración, etc.).
│   ├── run_all.py               Corre todos los pasos en orden.
│   ├── _bootstrap.py            Ayudante para que los scripts encuentren el código compartido.
│   └── plotting.py              Estilo común de los gráficos.
│
├── experiments/vote_weights.py  Estudio: ¿filtrar o ponderar por votos?
│
├── app/
│   ├── backend/                 EL SERVIDOR (FastAPI).
│   │   ├── main.py              Las "direcciones" (endpoints) del servidor.
│   │   └── schemas.py           Reglas de qué datos se aceptan y se devuelven.
│   └── frontend/                LA PÁGINA WEB.
│       ├── index.html           Estructura.
│       ├── styles.css           Aspecto (temas claro y oscuro, adaptable a celular).
│       ├── app.js               Comportamiento.
│       └── assets/              Logo (logo.svg) e isotipo/ícono (logo-mark.svg).
│
├── models/                      Los modelos ya entrenados y su información.
│   ├── model.joblib             Clasificador de la etiqueta.
│   ├── index_model.joblib       Modelo del índice (principal).
│   ├── accords_vocab.json       La lista de los 72 acordes válidos.
│   └── metadata.json            Datos sobre los modelos (versión, métricas, frecuencias base).
│
├── reports/                     Resultados de cada paso, en .json.
├── docs/figures/                Los gráficos y capturas que usa el README.
├── data/raw/                    Acá va perfumes.csv (no se sube a Git).
└── tests/                       Tests automáticos.
```

> Las carpetas `data/processed/` (datos limpios intermedios), `.venv/` (entorno virtual), `docs/spec-*.md` y `tasks/` existen en tu computadora pero **no se suben a Git**.

## 4.2 El recorrido completo de los datos, de punta a punta

Pensalo como una **fábrica con una línea de producción**. Cada estación recibe lo que dejó la anterior.

```
 ┌────────────────┐   ┌───────────────┐   ┌────────────────┐   ┌───────────────────┐
 │ perfumes.csv   │ → │ 01 EDA        │   │ 02 ETL         │ → │ clean.csv.gz       │
 │ (131.930 filas)│   │ (mirar y      │   │ (limpiar,      │   │ + vocabulario      │
 │ sin procesar   │   │  graficar)    │   │ dividir, índice│   │ (72 acordes)       │
 └────────────────┘   └───────────────┘   └────────────────┘   └─────────┬─────────┘
                                                                            │
              ┌────────────────────────────────────────────────────────────┤
              ▼                                                            ▼
     ┌─────────────────┐                                          ┌──────────────────┐
     │ 03 Experimentos │                                          │ 04 Entrenar el   │
     │ (decisiones)    │                                          │ clasificador     │──→ models/model.joblib
     └─────────────────┘                                          └────────┬─────────┘
                                                                           ▼
                                                                  ┌──────────────────┐
                                                                  │ 05 Entrenar el   │
                                                                  │ modelo de índice │──→ models/index_model.joblib
                                                                  └────────┬─────────┘
                                                                           ▼
                                                                  ┌──────────────────┐
                                                                  │ 06 Evaluar       │──→ reports/, docs/figures/
                                                                  └──────────────────┘
```

### Un ejemplo concreto, perfume por perfume

Tomemos un perfume inventado de la base de datos y sigámoslo por todo el camino.

**Paso 0: en el archivo crudo.** Una fila del CSV (versión simplificada):

| id | gender | vote_count | accords | perceived_female | perceived_male_leaning | perceived_male | … |
|---|---|---|---|---|---|---|---|
| 1234 | male | 40 | `woody:100\|leather:75\|smoky:61` | 2 | 6 | 10 | … |

**Paso 1: parseo** (`parsing.py`). El texto `woody:100|leather:75|smoky:61` se convierte en un diccionario de Python: `{"woody": 100.0, "leather": 75.0, "smoky": 61.0}`.

**Paso 2: limpieza** (`data.py`). Se verifica que tenga acordes, que la etiqueta sea válida y que no haya otro perfume con exactamente el mismo perfil (si lo hubiera, se queda uno).

**Paso 3: el índice** (`perception.py`). Con los votos: 2 de "femenino" (peso 0), 6 de "tiende a masculino" (peso 0,75), 10 de "masculino" (peso 1). Total de votos: 18.
`índice = (2×0 + 6×0,75 + 10×1) / 18 = 14,5 / 18 = 0,806` → zona **masculina**.

**Paso 4: división** (`02_etl.py`). El perfume se asigna al azar (con semilla fija) a **train** o a **test**.

**Paso 5: vectorización** (`features.py`). Con el vocabulario de 72 acordes (en orden alfabético), el perfume se convierte en un vector de 72 posiciones: todo ceros salvo `woody = 1,0`, `leather = 0,75`, `smoky = 0,61`.

**Paso 6: entrenamiento** (`04` y `05`). Si el perfume está en train, los modelos "aprenden" de él: el clasificador aprende "estos acordes → male"; el modelo de índice aprende "estos acordes → 0,806" (con peso √18 ≈ 4,2 porque tiene 18 votos).

**Paso 7: en la aplicación.** Un usuario carga `woody 100, leather 75, smoky 60` en la página. El servidor:
1. Valida (acordes conocidos, entre 1 y 8, intensidades de 0 a 100).
2. **Reescala** para que el acorde más fuerte valga 100 (acá ya vale 100).
3. Lo convierte en el vector de 72 números.
4. Le pregunta al **modelo de índice**: devuelve `0,6836`.
5. Le pregunta al **clasificador**: devuelve `femenino 2,95 %, masculino 17,86 %, unisex 79,19 %`.
6. Calcula la lectura femenino vs. masculino (`0,1786 / (0,0295 + 0,1786) = 85,8 %` masculino) y el lift.
7. Calcula la influencia de cada acorde (quitándolos de a uno).
8. Devuelve todo en JSON; la página lo dibuja.

## 4.3 Las dos "etapas" de la vida del proyecto

Es útil distinguir dos momentos:

| | **Etapa de entrenamiento** | **Etapa de uso** |
|---|---|---|
| Qué pasa | Se procesan los datos y se **crean** los modelos | Se **usan** los modelos ya creados |
| Quién lo hace | El **pipeline** (`pipeline/`) | La **aplicación** (`app/`) |
| Qué necesita | El dataset (`perfumes.csv`) y la librería completa | Solo los modelos (`models/`) |
| Con qué frecuencia | Rara vez (solo si cambian los datos o el criterio) | Cada vez que alguien usa la página |
| Resultado | `models/*.joblib`, `reports/*.json`, `docs/figures/*.png` | La respuesta en pantalla |

**Por eso un perfumista puede usar la app sin tener el dataset:** los modelos entrenados viajan dentro del repositorio.

---

# Parte 5: El paquete `perfume_gender` (el corazón compartido)

Este paquete es **la única fuente de verdad** de cómo se interpretan los datos. Lo usan tanto el pipeline (al entrenar) como la aplicación (al predecir). Eso es importante: si el entrenamiento y la predicción procesaran los acordes de forma distinta, el modelo recibiría datos "en otro idioma" y fallaría.

El archivo `__init__.py` (casi vacío: solo tiene un comentario) existe para que Python reconozca la carpeta como un **paquete** importable (`from perfume_gender import config`).

---

## 5.1 `perfume_gender/config.py`: rutas y constantes

**Para qué sirve:** un solo lugar donde están definidas todas las rutas de archivos y los valores fijos del proyecto. Así, si algo cambia, se cambia en un solo sitio.

```python
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
```
**Bloque 1 (raíz del proyecto).** `__file__` es la ruta de este archivo (`.../perfume_gender/config.py`). `.resolve()` la convierte en ruta absoluta; `.parents[1]` sube dos niveles (la carpeta `perfume_gender` y luego la raíz del proyecto). Así `ROOT` siempre apunta a la carpeta del proyecto, **esté donde esté** en la computadora.

```python
DATA_RAW = ROOT / "data" / "raw" / "perfumes.csv"
DATA_PROCESSED = ROOT / "data" / "processed"
MODELS_DIR = ROOT / "models"
REPORTS_DIR = ROOT / "reports"
FIGURES_DIR = ROOT / "docs" / "figures"
```
**Bloque 2 (carpetas).** Se arman las rutas con el operador `/`. Son: el CSV crudo, la carpeta de datos procesados, de modelos, de reportes y de figuras.

```python
MODEL_PATH = MODELS_DIR / "model.joblib"
INDEX_MODEL_PATH = MODELS_DIR / "index_model.joblib"
VOCAB_PATH = MODELS_DIR / "accords_vocab.json"
METADATA_PATH = MODELS_DIR / "metadata.json"
```
**Bloque 3 (archivos de modelos).** El clasificador, el modelo de índice, el vocabulario de acordes y los metadatos.

```python
SEED = 42
TEST_SIZE = 0.20
CV_FOLDS = 5
```
**Bloque 4 (parámetros del experimento).**
- `SEED = 42`: la semilla del azar (para que todo sea reproducible).
- `TEST_SIZE = 0.20`: el 20 % de los perfumes va a test.
- `CV_FOLDS = 5`: la validación cruzada usa 5 pedazos.

```python
CLASSES = ["female", "male", "unisex"]
CLASS_LABELS_ES = {"female": "Femenino", "male": "Masculino", "unisex": "Unisex"}
```
**Bloque 5 (clases).** Los nombres internos (en inglés, como vienen en el dataset) y su traducción al español para los gráficos.

```python
MAX_ACCORDS = 8
```
**Bloque 6.** Máximo de acordes por perfume: Fragrantica muestra 8 como máximo, y el acorde más fuerte vale siempre 100.

---

## 5.2 `perfume_gender/parsing.py`: leer el texto de acordes

**Para qué sirve:** en el dataset, los acordes vienen como un texto: `"woody:100|sweet:65|fresh spicy:47"`. Este archivo lo traduce a un diccionario de Python que el programa puede usar, y normaliza los nombres (para que `"Woody"`, `" woody "` y `"WOODY"` sean lo mismo).

```python
import re
ACCORD_ALIASES = {"powder": "powdery"}
_WS = re.compile(r"\s+")
```
**Bloque 1 (preparativos).**
- `re` es la librería de **expresiones regulares** (patrones de texto).
- `ACCORD_ALIASES` es un diccionario de **sinónimos**: en los datos aparecen `powder` y `powdery` para lo mismo, así que se unifican en `powdery`.
- `_WS = re.compile(r"\s+")` crea un patrón que significa "uno o más espacios en blanco seguidos" (espacios, tabuladores…). El guion bajo inicial es una convención: "esto es de uso interno".

```python
def normalize_accord(name: str) -> str:
    n = _WS.sub(" ", str(name).strip().lower())
    return ACCORD_ALIASES.get(n, n)
```
**Bloque 2: `normalize_accord`.** Recibe el nombre de un acorde y devuelve su versión "estándar":
1. `str(name)`: se asegura de que sea texto.
2. `.strip()`: saca espacios al principio y al final.
3. `.lower()`: pasa a minúsculas.
4. `_WS.sub(" ", ...)`: si hay varios espacios seguidos en el medio, deja uno solo (`"fresh   spicy"` → `"fresh spicy"`).
5. `ACCORD_ALIASES.get(n, n)`: si el nombre está en la tabla de sinónimos lo reemplaza; si no, lo deja igual.

Ejemplos: `"  Fresh  Spicy "` → `"fresh spicy"`; `"Powder"` → `"powdery"`.

```python
def parse_accords(raw: object) -> dict[str, float]:
    result: dict[str, float] = {}
    if raw is None or (isinstance(raw, float) and raw != raw):
        return result
    for item in str(raw).split("|"):
        name, sep, value = item.rpartition(":")
        if not sep:
            continue
        try:
            intensity = float(value.strip())
        except ValueError:
            continue
        key = normalize_accord(name)
        if key:
            result[key] = max(result.get(key, 0.0), intensity)
    return result
```
**Bloque 3: `parse_accords`.** Convierte el texto completo en diccionario.
- **Línea del `if raw is None ...`:** si no hay valor (vacío) devuelve un diccionario vacío. El truco `raw != raw` detecta un **NaN** (un "no-número", que es como pandas marca las celdas vacías): un NaN es el único valor que **no es igual a sí mismo**.
- **`str(raw).split("|")`:** parte el texto por cada `|` → `["woody:100", "sweet:65", ...]`.
- **`item.rpartition(":")`:** parte cada pedazo en el **último** `:` y devuelve `(antes, el separador, después)`. Se usa el **último** dos puntos porque así funciona aunque el nombre del acorde tuviera uno adentro. Ej.: `"woody:100"` → `("woody", ":", "100")`.
- **`if not sep: continue`:** si no había `:` (el pedazo está mal formado), se **saltea** ese pedazo.
- **`try / float(...)`:** convierte `"100"` en el número `100.0`. Si no es un número (`ValueError`), también se saltea.
- **`key = normalize_accord(name)`:** estandariza el nombre.
- **`max(result.get(key, 0.0), intensity)`:** si el mismo acorde apareciera dos veces (por ejemplo `powder` y `powdery`), se queda con la intensidad **mayor**.

Resultado: `parse_accords("woody:100|sweet:65")` → `{"woody": 100.0, "sweet": 65.0}`. Las intensidades quedan en la escala original de 0 a 100.

---

## 5.3 `perfume_gender/perception.py`: el índice de masculinidad percibida

**Para qué sirve:** transforma los **votos de la gente** en un número de 0 a 1, y define las **zonas** y el **peso de entrenamiento**. Es la pieza que da origen al modelo principal.

```python
from typing import TYPE_CHECKING
import numpy as np
if TYPE_CHECKING:
    import pandas as pd
```
**Bloque 1 (imports).** `pandas` solo se importa "para que los tipos se vean bien" (`TYPE_CHECKING` es `False` al correr el programa). Así la aplicación **no necesita instalar pandas** para funcionar (es una librería pesada), solo NumPy.

```python
PESOS = {
    "perceived_female": 0.0,
    "perceived_female_leaning": 0.25,
    "perceived_unisex": 0.5,
    "perceived_male_leaning": 0.75,
    "perceived_male": 1.0,
}
PERCEIVED_COLUMNS = list(PESOS)
```
**Bloque 2 (los pesos de cada tipo de voto).** Cada persona votó una de cinco opciones; a cada opción se le asigna un valor en el espectro:

| Voto | Peso |
|---|---|
| "se siente femenino" | 0 |
| "tiende a femenino" | 0,25 |
| "se siente unisex" | 0,5 |
| "tiende a masculino" | 0,75 |
| "se siente masculino" | 1 |

`PERCEIVED_COLUMNS` es solo la lista de los nombres de esas cinco columnas.

```python
ZONE_LIMITS = (0.33, 0.67)
VOTE_CAP = 100
```
**Bloque 3.** Los límites de las zonas (0,33 y 0,67) y el tope de votos para el peso de entrenamiento (100).

```python
def perception_votes(votes):
    return votes[PERCEIVED_COLUMNS].sum(axis=1)
```
**Bloque 4: `perception_votes`.** Suma, **fila por fila**, los cinco tipos de voto: devuelve el **total de votos de percepción** de cada perfume (`axis=1` significa "sumá hacia el costado, a lo largo de las columnas").

```python
def perception_index(votes):
    total = perception_votes(votes)
    score = sum(votes[c] * w for c, w in PESOS.items())
    return (score / total).where(total > 0)
```
**Bloque 5: `perception_index`.** Calcula el índice:
- `total`: votos totales por perfume.
- `score`: la suma de `votos × peso` de cada tipo.
- `score / total`: el **promedio ponderado** (el índice).
- `.where(total > 0)`: si el perfume **no tiene votos**, el resultado se deja vacío (NaN) en lugar de dividir por cero.

Ejemplo: 10 votos "masculino" y 10 "unisex" → `(10×1 + 10×0,5) / 20 = 0,75`.

```python
def zone(index):
    index = np.asarray(index, dtype=float)
    return np.where(index < ZONE_LIMITS[0], "female",
                    np.where(index > ZONE_LIMITS[1], "male", "unisex"))
```
**Bloque 6: `zone`.** Convierte un número en su zona: menor a 0,33 → `"female"`; mayor a 0,67 → `"male"`; el resto → `"unisex"`. `np.where(condición, si_sí, si_no)` es un "if" aplicado a muchos valores a la vez.

```python
def vote_weight(votes, cap=VOTE_CAP):
    return np.sqrt(np.minimum(np.asarray(votes, dtype=float), cap))
```
**Bloque 7: `vote_weight`.** El peso para el entrenamiento: `np.minimum(votos, 100)` limita a 100 y `np.sqrt` saca la raíz cuadrada. 1 voto → 1; 4 votos → 2; 100 o más → 10.

---

## 5.4 `perfume_gender/features.py`: de acordes a números

**Para qué sirve:** los modelos solo entienden **números**. Este archivo arma el **vocabulario** (la lista de acordes posibles) y convierte cada perfume en un vector.

```python
def build_vocab(accord_dicts, min_count=1):
    counts = {}
    for d in accord_dicts:
        for k in d:
            counts[k] = counts.get(k, 0) + 1
    return sorted(k for k, c in counts.items() if c >= min_count)
```
**`build_vocab`.** Arma la lista alfabética de acordes.
1. Recorre todos los perfumes y **cuenta en cuántos aparece cada acorde** (`counts[k] = counts.get(k, 0) + 1`: "sumale uno a lo que ya tenía, empezando de 0").
2. Se queda solo con los que aparecen al menos `min_count` veces. Con `min_count=50` quedan 72 acordes (se descartan 20 muy raros).
3. `sorted(...)` los ordena alfabéticamente. **El orden importa**: la posición de cada acorde en el vector es siempre la misma.

```python
def rescale_to_max(accords):
    top = max(accords.values(), default=0.0)
    if top <= 0:
        return {}
    return {k: v * 100.0 / top for k, v in accords.items()}
```
**`rescale_to_max`.** En Fragrantica las intensidades son **relativas**: el acorde dominante vale siempre 100. Para que lo que escribe el usuario "hable el mismo idioma" que los datos, se reescala para que el más fuerte valga 100. Ej.: `{"woody": 40, "sweet": 20}` → `{"woody": 100, "sweet": 50}`. `max(..., default=0.0)` evita un error si el diccionario está vacío.

```python
def to_matrix(accord_dicts, vocab):
    index = {a: i for i, a in enumerate(vocab)}
    rows = list(accord_dicts)
    X = np.zeros((len(rows), len(vocab)), dtype=np.float32)
    for r, d in enumerate(rows):
        for name, value in d.items():
            j = index.get(normalize_accord(name))
            if j is not None:
                X[r, j] = value / 100.0
    return X
```
**`to_matrix` (la conversión).** Es la pieza central.
1. `index`: un diccionario `acorde → posición` (por ejemplo `"woody" → 70`).
2. `X = np.zeros((n_perfumes, n_acordes))`: una matriz **llena de ceros**.
3. Para cada perfume y cada acorde que tiene: busca su posición `j` y escribe `valor / 100` (para que quede entre 0 y 1).
4. Si el acorde **no está en el vocabulario** (`j is None`), se **ignora**.
5. `float32` ahorra memoria.

```python
def vectorize(accords, vocab):
    return to_matrix([accords], vocab)[0]
```
**`vectorize`.** Convierte **un solo** perfume en su vector (lo envuelve en una lista, usa `to_matrix` y toma la primera fila).

```python
def save_vocab(vocab, path): ...
def load_vocab(path): ...
```
**`save_vocab` / `load_vocab`.** Guardan y leen la lista de acordes en `models/accords_vocab.json`. `ensure_ascii=False` permite guardar acentos; `indent=1` lo deja legible.

---

## 5.5 `perfume_gender/data.py`: leer y limpiar el dataset

**Para qué sirve:** lee `perfumes.csv` y le aplica todas las reglas de limpieza.

```python
RAW_COLUMNS = ["id", "name", "brand", "gender", "vote_count", "accords",
               "notes_top", "notes_middle", "notes_base", "notes_flat",
               *PERCEIVED_COLUMNS]
```
**Bloque 1.** De las **59 columnas** del CSV solo se leen las 15 necesarias (`*PERCEIVED_COLUMNS` "desparrama" las cinco columnas de percepción dentro de la lista). Leer menos columnas ahorra memoria y tiempo.

```python
def load_raw(path=DATA_RAW):
    if not Path(path).exists():
        raise FileNotFoundError("No se encontro ... Descarga perfumes.csv de Kaggle ...")
    return pd.read_csv(path, usecols=RAW_COLUMNS, low_memory=False)
```
**Bloque 2: `load_raw`.** Si el archivo no existe, **avisa con un mensaje claro** de qué hacer. Si existe, lo lee con pandas (`usecols` = solo esas columnas; `low_memory=False` = que lea en una sola pasada para no confundirse con los tipos).

```python
def fingerprint(accords):
    return "|".join(f"{k}:{v:g}" for k, v in sorted(accords.items()))
```
**Bloque 3: `fingerprint` ("huella digital").** Convierte un perfil de acordes en un texto único y ordenado, por ejemplo `"leather:75|smoky:61|woody:100"`. Dos perfumes con exactamente los mismos acordes y las mismas intensidades tienen **la misma huella**: así se detectan los duplicados.

### La función `clean`: los pasos de limpieza en orden

```python
stats = {"raw_rows": len(df), "raw_class_counts": ...}
df = df.copy()
```
`stats` es un diccionario donde se van anotando las **estadísticas de cada paso** (cuántas filas se descartaron, etc.), que luego se guardan en `reports/etl.json`. `df.copy()` hace una copia para no modificar la tabla original.

```python
stats["no_accords"] = int(df["accords"].isna().sum())
df = df.dropna(subset=["accords"])
```
**Paso 1: sacar los perfumes sin acordes** (2.769). Se anota cuántos eran y se descartan.

```python
df["accords_dict"] = df["accords"].map(parse_accords)
empty = df["accords_dict"].map(len) == 0
df = df[~empty]
```
**Paso 2: convertir el texto en diccionario y sacar los que quedan vacíos.** `~empty` es "lo contrario de `empty`" (la `~` invierte verdadero/falso). En esta base no hubo ninguno (0).

```python
bad_label = ~df["gender"].isin(CLASSES)
df = df[~bad_label]
```
**Paso 3: sacar etiquetas de género inválidas** (que no sean `female`, `male` o `unisex`). En esta base: ninguna.

```python
df["fp"] = df["accords_dict"].map(fingerprint)
df["vote_count"] = df["vote_count"].fillna(0)
df["weight"] = df["vote_count"] + 1
```
**Paso 4: preparar la deduplicación.** Se calcula la huella de cada perfume, se reemplazan votos vacíos por 0 y se define un **peso** `votos + 1` (el "+1" para que un perfume con 0 votos igual cuente algo).

```python
weights = df.groupby(["fp", "gender"])["weight"].sum().unstack(fill_value=0)
winner = weights.idxmax(axis=1)
n_labels = (weights > 0).sum(axis=1)
```
**Paso 5: resolver las etiquetas contradictorias.**
- `groupby(["fp","gender"])["weight"].sum()`: por cada **huella** y cada **género**, suma los pesos (cuánta "gente" respalda esa combinación).
- `.unstack(...)`: reorganiza para que cada huella sea una fila y haya una columna por género.
- `winner = weights.idxmax(axis=1)`: para cada huella, **el género con más respaldo**.
- `n_labels`: en cuántos géneros distintos aparece la huella (si es más de uno, hay conflicto).

```python
keep = df[df["gender"] == df["fp"].map(winner)]
keep = keep.sort_values("vote_count", ascending=False).drop_duplicates("fp")
keep = keep.sort_index().reset_index(drop=True)
```
**Paso 6: quedarse con una fila por perfil.**
1. Se conservan solo las filas cuyo género coincide con el **ganador** de su huella.
2. Se ordenan de más a menos votos y se hace `drop_duplicates("fp")`: queda **una sola fila por huella**, la de más votos.
3. Se restaura el orden original y se renumera.

El resultado final: **122.955 perfumes**.

```python
return keep, stats
```
Devuelve la tabla limpia **y** las estadísticas.

---

## 5.6 `perfume_gender/modeling.py`: datos de entrenamiento y modelos candidatos

```python
def load_dataset():
    path = config.DATA_PROCESSED / "clean.csv.gz"
    if not path.exists():
        raise FileNotFoundError("Falta data/processed/clean.csv.gz: ejecuta pipeline/02_etl.py")
    df = pd.read_csv(path, low_memory=False)
    vocab = load_vocab(config.VOCAB_PATH)
    df["accords_dict"] = df["accords"].map(parse_accords)
    X = to_matrix(df["accords_dict"], vocab)
    return df, X, vocab
```
**`load_dataset`.** La "puerta de entrada" de todos los scripts de entrenamiento: lee el dataset ya limpio (el que dejó el ETL), carga el vocabulario, convierte los acordes de cada perfume a diccionario y de ahí a la **matriz X**. Devuelve tres cosas: la **tabla** (`df`), la **matriz de features** (`X`) y el **vocabulario** (`vocab`). Si el archivo no existe, avisa qué paso hay que correr antes.

```python
def update_metadata(**sections):
    meta = {}
    if config.METADATA_PATH.exists():
        meta = json.loads(config.METADATA_PATH.read_text(encoding="utf-8"))
    meta.update(sections)
    config.METADATA_PATH.parent.mkdir(exist_ok=True)
    config.METADATA_PATH.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
```
**`update_metadata`.** `models/metadata.json` lo escriben **dos scripts distintos** (el del clasificador y el del índice), cada uno con su sección. Esta función **lee lo que ya hay**, le agrega o reemplaza las secciones nuevas (`meta.update(sections)`) y lo vuelve a guardar, de modo que un script no pise lo que escribió el otro. `**sections` significa "recibí cualquier cantidad de parámetros con nombre".

```python
def candidates(seed=config.SEED):
    return {
        "Baseline (clase mayoritaria)": DummyClassifier(strategy="most_frequent"),
        "Regresión logística": LogisticRegression(C=1.0, max_iter=1000),
        "Random Forest": RandomForestClassifier(n_estimators=200, min_samples_leaf=5, n_jobs=-1, random_state=seed),
        "Gradient Boosting (HGB)": HistGradientBoostingClassifier(max_iter=300, learning_rate=0.08, max_leaf_nodes=31, early_stopping=True, validation_fraction=0.1, n_iter_no_change=20, random_state=seed),
        "MLP (red neuronal)": MLPClassifier(hidden_layer_sizes=(128, 64), early_stopping=True, max_iter=200, random_state=seed),
        "SVM (RBF)": SVC(C=1.0, kernel="rbf", random_state=seed),
    }
```
**`candidates`: los seis participantes del "torneo".** Devuelve un diccionario `nombre → modelo sin entrenar`. Detalles de cada uno:
- `DummyClassifier(strategy="most_frequent")`: el baseline; siempre responde la clase más frecuente.
- `LogisticRegression(C=1.0, max_iter=1000)`: `C` controla cuánto se "regulariza" (1,0 = valor estándar); `max_iter=1000` = hasta 1000 intentos de ajuste.
- `RandomForestClassifier(n_estimators=200, min_samples_leaf=5, n_jobs=-1)`: 200 árboles; cada hoja con al menos 5 perfumes; `n_jobs=-1` = "usá todos los núcleos del procesador".
- `HistGradientBoostingClassifier(...)`: ver [2.8](#28-los-algoritmos-que-se-compararon). "Hist" viene de *histogram*: agrupa los valores en "canastas" para ir más rápido.
- `MLPClassifier(hidden_layer_sizes=(128, 64), ...)`: red neuronal con dos capas ocultas, de 128 y 64 neuronas.
- `SVC(C=1.0, kernel="rbf")`: SVM con núcleo RBF (una forma de trazar fronteras curvas).
- `random_state=seed`: fija el azar de cada modelo.

---

## 5.7 `perfume_gender/predictor.py`: el cerebro de la aplicación

**Para qué sirve:** junta los dos modelos y el vocabulario en un solo objeto y expone una función `predict` que recibe acordes y devuelve **todo** lo que muestra la página.

### Las piezas sueltas

```python
NEUTRAL_EFFECT = 0.005

class InvalidAccordsError(ValueError):
    """La entrada tiene acordes desconocidos, vacios o demasiados."""
```
- `NEUTRAL_EFFECT`: si quitar un acorde mueve el índice menos de 0,005 (medio punto), se considera que ese acorde es **neutro**.
- `InvalidAccordsError`: un tipo de error propio. Sirve para distinguir "el usuario mandó datos malos" (→ error 422) de un error inesperado.

```python
def male_vs_female(p_female, p_male):
    total = p_female + p_male
    if total <= 0:
        return {"female": 0.5, "male": 0.5}
    return {"female": p_female / total, "male": p_male / total}
```
**`male_vs_female`.** Reparte 100 % entre femenino y masculino ignorando unisex. Con `p_female = 0,03` y `p_male = 0,07`: total 0,10 → 30 % y 70 %. Si ambas fueran 0 (caso raro), devuelve 50/50 para no dividir por cero.

```python
def lift(probabilities, priors):
    return {c: p / priors[c] if priors.get(c) else 0.0 for c, p in probabilities.items()}
```
**`lift`.** Para cada clase divide la probabilidad por su frecuencia base. Si no hay frecuencia base para esa clase, devuelve 0 (en vez de fallar).

### La clase `Predictor`

```python
@dataclass
class Predictor:
    classifier: object
    index_model: object
    vocab: list[str]
    metadata: dict
```
**Los cuatro datos que guarda:** el clasificador, el modelo de índice, el vocabulario y los metadatos (que incluyen las frecuencias base `class_priors`).

```python
@classmethod
def load(cls, model_path=..., index_path=..., vocab_path=..., metadata_path=...):
    for p in (model_path, index_path, vocab_path, metadata_path):
        if not Path(p).exists():
            raise FileNotFoundError(...)
    return cls(classifier=joblib.load(model_path), index_model=joblib.load(index_path),
               vocab=load_vocab(vocab_path),
               metadata=json.loads(Path(metadata_path).read_text(encoding="utf-8")))
```
**`load`.** Verifica que los cuatro archivos existan (si falta alguno, error con instrucciones) y los **carga**. `cls(...)` crea un `Predictor` con esos cuatro datos.

```python
def clean_input(self, accords):
    cleaned = {}
    for name, value in accords.items():
        key = normalize_accord(name)
        cleaned[key] = max(cleaned.get(key, 0.0), float(value))
    cleaned = {k: v for k, v in cleaned.items() if v > 0}
    if not cleaned:
        raise InvalidAccordsError("Ingresa al menos un acorde con intensidad mayor a 0.")
    if len(cleaned) > config.MAX_ACCORDS:
        raise InvalidAccordsError(...)
    unknown = sorted(set(cleaned) - set(self.vocab))
    if unknown:
        raise InvalidAccordsError(f"Acordes desconocidos: {', '.join(unknown)}")
    return rescale_to_max(cleaned)
```
**`clean_input`: la "aduana" de la entrada.** En orden:
1. Normaliza los nombres (y si el usuario mandó dos veces el mismo acorde, se queda con la mayor intensidad).
2. Descarta los acordes con intensidad 0 o negativa.
3. Si **no queda ninguno**, error.
4. Si hay **más de 8**, error.
5. Calcula qué acordes **no están en el vocabulario** (`set(cleaned) - set(self.vocab)` es una resta de conjuntos: "lo que está en uno y no en el otro"); si hay alguno, error que lista cuáles.
6. Si todo está bien, **reescala** para que el más fuerte valga 100.

```python
def _x(self, accords):
    return vectorize(accords, self.vocab).reshape(1, -1)

def _index(self, accords):
    return float(np.clip(self.index_model.predict(self._x(accords))[0], 0.0, 1.0))
```
- `_x`: convierte los acordes en vector y lo pone como "una fila" (`reshape(1, -1)` = "1 fila, las columnas que haga falta"), que es el formato que esperan los modelos de scikit-learn.
- `_index`: le pide el índice al regresor y lo **limita entre 0 y 1** (`np.clip`), porque un regresor a veces devuelve valores levemente fuera de rango (por ejemplo 1,03).

```python
def predict(self, accords, explain=True):
    cleaned = self.clean_input(accords)
    index = self._index(cleaned)
    proba = self.classifier.predict_proba(self._x(cleaned))[0]
    classes = [str(c) for c in self.classifier.classes_]
    probs = {c: float(p) for c, p in zip(classes, proba)}
    priors = self.metadata.get("class_priors") or {c: 1 / len(classes) for c in classes}
    result = {
        "index": round(index, 4),
        "zone": str(zone(index)),
        "male_vs_female": {...},
        "class_probabilities": {...},
        "lift": {...},
        "accords_used": {...},
    }
    if explain:
        result["influences"] = self._influences(cleaned, index)
    return result
```
**`predict`: la función principal.**
1. Limpia/valida la entrada.
2. Pide el **índice** al regresor.
3. Pide las **tres probabilidades** al clasificador (`predict_proba(...)[0]` → la primera y única fila).
4. `zip(classes, proba)` junta cada nombre de clase con su probabilidad.
5. Obtiene las frecuencias base (`priors`); si faltaran, usa 1/3 para cada una.
6. Arma el diccionario con todos los resultados, redondeados.
7. Si `explain` es verdadero, agrega la **influencia de cada acorde**.

```python
def _influences(self, cleaned, index):
    out = []
    for name in cleaned:
        rest = {k: v for k, v in cleaned.items() if k != name}
        if not rest:
            continue
        effect = index - self._index(rescale_to_max(rest))
        toward = "neutral" if abs(effect) < NEUTRAL_EFFECT else ("male" if effect > 0 else "female")
        out.append({"accord": name, "index_effect": round(effect, 4), "pushes_toward": toward})
    out.sort(key=lambda i: -abs(i["index_effect"]))
    return out
```
**`_influences`: "¿qué pasa si saco este acorde?".** Para cada acorde del perfil:
1. Arma el perfil **sin** ese acorde (`rest`). Si se quedaría sin nada, lo saltea.
2. Reescala y le pregunta el índice al modelo.
3. `effect = índice_con_el_acorde − índice_sin_el_acorde`. **Positivo** = ese acorde **empuja hacia masculino**; **negativo** = hacia femenino.
4. Si el efecto es chiquito (< 0,005), se marca "neutral".
5. Al final ordena de **mayor a menor influencia** (`key=lambda i: -abs(...)`).

> **Limitación para entender:** esto mide el efecto de **quitar** un acorde, no una "importancia universal". Si dos acordes hacen lo mismo, quitar solo uno puede no cambiar nada (por eso en la composición de ejemplo `cannabis`, `chocolate` y `aldehydic` salen con 0 puntos).

---

# Parte 6: El pipeline de datos y entrenamiento

El **pipeline** ("tubería") es la serie de scripts que se corren **en orden** para pasar de "datos crudos" a "modelos entrenados y resultados". Cada script es un archivo de Python que se ejecuta desde la terminal (por ejemplo `python pipeline/02_etl.py`). Todos se pueden correr de una vez con `python pipeline/run_all.py`.

**Patrón común de todos los scripts:**
```python
import _bootstrap  # noqa: F401

def main() -> None:
    ...            # acá está todo el trabajo

if __name__ == "__main__":
    main()
```
- La primera línea es un ayudante (se explica abajo).
- `main()` contiene el trabajo.
- Las últimas dos líneas significan: "si me ejecutaron directamente, corré `main()`".

---

## 6.1 `pipeline/_bootstrap.py`: el ayudante de arranque

**Problema que resuelve:** cuando ejecutás `python pipeline/01_eda.py`, Python solo busca módulos en la carpeta `pipeline/`. Pero los scripts necesitan importar `perfume_gender`, que vive **una carpeta más arriba**. Este archivo le agrega la raíz del proyecto a la lista de lugares donde Python busca.

```python
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
```
- `sys.path` es la **lista de carpetas** donde Python busca lo que le pedís importar.
- Se calcula la raíz del proyecto y, si todavía no está en la lista, se **agrega al principio** (`insert(0, ...)`).

```python
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8")
    except Exception:
        pass
```
- `sys.stdout` es la "salida de pantalla" del programa y `sys.stderr` la de errores. Se les fuerza la codificación **UTF-8** para que los acentos y símbolos (`≥`, `→`) **no rompan** en la consola de Windows. Si no se puede (`except`), se ignora (`pass` = "no hagas nada").

**Por qué se importa así:** `import _bootstrap  # noqa: F401`. Lo importante no es usar algo de ese archivo, sino que **al importarlo se ejecuta su código**. El comentario `noqa: F401` le dice a las herramientas de revisión de código "sí, sé que este import parece no usarse, está bien".

---

## 6.2 `pipeline/plotting.py`: el estilo común de los gráficos

**Para qué sirve:** que todos los gráficos del proyecto se vean **consistentes** (mismos colores, mismos estilos).

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
```
`matplotlib.use("Agg")` elige un modo "sin ventanas": en vez de abrir una ventana para cada gráfico, lo **dibuja directo a un archivo**. Es necesario para correr scripts sin pantalla (por ejemplo en un servidor). **Tiene que ir antes** de importar `pyplot`.

```python
GENDER_COLORS = {"female": "#D1495B", "male": "#00798C", "unisex": "#EDAE49"}
NEUTRAL = "#6B7280"
ACCENT = "#3D348B"
```
La **paleta**: rojo-rosado para femenino, azul verdoso para masculino, amarillo-naranja para unisex, gris neutro y violeta de acento. Está pensada para que se distingan bien incluso con daltonismo. Los colores están en formato **hexadecimal** (`#RRGGBB`: cantidad de rojo, verde y azul).

```python
def setup():
    plt.rcParams.update({"figure.dpi": 110, "savefig.dpi": 130, "savefig.bbox": "tight",
        "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
        "grid.alpha": 0.25, "axes.titlesize": 13, "axes.titleweight": "bold",
        "axes.labelsize": 10.5, "font.family": "sans-serif"})
```
**`setup`.** Cambia la configuración global de los gráficos: resolución (`dpi`), recortar márgenes sobrantes (`bbox: tight`), **sacar los bordes** de arriba y la derecha, mostrar una cuadrícula suave, tamaños de título y etiquetas, y tipo de letra.

```python
def save(fig, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
    print(f"  figura -> {path}")
```
**`save`.** Crea la carpeta destino si no existe (`mkdir(parents=True, exist_ok=True)`), guarda la figura como imagen, la **cierra** (libera memoria) e imprime qué archivo creó.

---

## 6.3 `pipeline/01_eda.py`: mirar los datos antes de tocarlos

**EDA** significa *Exploratory Data Analysis* (análisis exploratorio de datos): **mirar, contar y graficar** los datos para entenderlos antes de tomar decisiones. Este script no entrena nada: produce **figuras** y el archivo `reports/eda.json`.

```python
raw = load_raw()
df, stats = clean(raw)
report = {"cleaning": stats}
```
Lee el CSV, lo limpia con `clean` y empieza un diccionario `report` donde se van guardando los hallazgos.

### Figura 1: distribución de las clases (`eda_01_clases.png`)
Muestra con barras cuántos perfumes hay de cada género, **antes y después de limpiar**. `x - w/2` y `x + w/2` desplazan las barras para ponerlas lado a lado. Encima de cada barra se escribe el porcentaje. Guarda `baseline_majority`: el porcentaje de la categoría mayoritaria (51,2 %), que es el **baseline**.

### Figura 2: acordes por perfume y votos (`eda_02_...`)
- A la izquierda: cuántos perfumes tienen 1, 2, … 8 acordes. Casi todos (116.782) tienen 8.
- A la derecha: un **diagrama de caja** (*boxplot*) de los votos según la cantidad de acordes, en escala logarítmica. Una "caja" muestra dónde está la mitad central de los datos; la línea roja es la mediana. `showfliers=False` oculta los puntos extremos para que se vea bien.

### Figura 3: distribución de votos (`eda_03_votos.png`)
Un **histograma** (barras que cuentan cuántos perfumes caen en cada rango) de los votos en escala log. Las líneas rojas punteadas marcan 5 y 20 votos. Guarda mediana, percentiles, máximo y cuántos perfumes tienen menos de 5 votos o exactamente 0.

### Figura 4: intensidades (`eda_04_intensidades.png`)
Junta **todas las intensidades de todos los acordes de todos los perfumes** en una sola lista (`np.concatenate`) y grafica las menores a 100 (el acorde principal siempre es 100 y distorsionaría el gráfico). Además verifica **que el acorde principal de cada perfume sea 100** (`top_accord_always_100: true`) y guarda mínimo, mediana y percentil 5 de las intensidades.

### Figura 5: frecuencia de acordes (`eda_05_...`)
Construye el vocabulario y la matriz `X`, y calcula en **qué porcentaje de perfumes aparece cada acorde** (`(X > 0).mean(axis=0)`: "¿es mayor que 0? → verdadero/falso → promedio por columna"). Grafica los 30 más frecuentes (`barh` = barras horizontales). Guarda también los 8 acordes más raros con sus conteos.

### Figura 6: qué acordes distinguen femenino de masculino (`eda_06_...`)
Calcula la **intensidad media de cada acorde en los perfumes femeninos y en los masculinos**, y la **diferencia**. Una barra positiva (rosa) = "el acorde es más fuerte en los femeninos"; negativa (azul) = "en los masculinos". Se grafican los 12 más "masculinos" y los 12 más "femeninos". Resultado: femeninos → floral, white floral, fruity, sweet, rose, powdery, vanilla; masculinos → aromatic, fresh spicy, woody, warm spicy, citrus, amber, lavender, leather.

### Figura 7: correlación entre acordes (`eda_07_...`)
Calcula la **correlación** (qué tan seguido van juntos) entre los 25 acordes más frecuentes y la dibuja como **mapa de calor** (`imshow`): rojo = suelen aparecer juntos, azul = suelen excluirse. `vmin/vmax` fijan la escala de colores.

### Figura 8: etiqueta vs. percepción (`eda_08_...`) — la figura clave
```python
df["perc_votes"] = perception_votes(df)
df["perc_index"] = perception_index(df)
fiables = df[df["perc_votes"] >= 30]
```
Calcula el índice y se queda con los perfumes con **al menos 30 votos de percepción** (27.568), porque con pocos votos el índice es poco confiable. Dibuja tres histogramas (uno por etiqueta): **cómo se distribuye el índice percibido dentro de cada etiqueta de marca**. Las líneas punteadas son los límites 0,33 y 0,67.

```python
uni = zone(fiables.loc[fiables["gender"] == "unisex", "perc_index"].values)
```
Toma los perfumes etiquetados "unisex" y calcula en qué **zona** cae cada uno según los votos. Guarda en el reporte: **14,1 % masculino, 24,9 % femenino y 61,0 % intermedio**. También guarda las estadísticas de votos (media, mediana, percentiles 75 y 90) de los dos tipos de votos.

**Qué muestra la figura:** los femeninos (picos cerca de 0,1) y los masculinos (cerca de 0,85) están **bien definidos**, pero los "unisex" forman una **nube ancha centrada en 0,5**: es una categoría difusa.

Al final guarda todo en `reports/eda.json` (`default=str` convierte cualquier cosa rara en texto para que se pueda guardar).

---

## 6.4 `pipeline/02_etl.py`: limpiar y preparar los datos

**ETL** = *Extract, Transform, Load* (extraer, transformar, cargar): leer los datos, arreglarlos y guardarlos listos para usar.

**Entradas y salidas:**
- Entrada: `data/raw/perfumes.csv`.
- Salidas: `data/processed/clean.csv.gz` (datos limpios + división train/test + índice), `models/accords_vocab.json` (los 72 acordes) y `reports/etl.json` (estadísticas).

```python
MIN_ACCORD_COUNT = 50
```
Un acorde que aparece en menos de 50 perfumes se descarta del vocabulario.

```python
raw = load_raw()
df, stats = clean(raw)
```
Lee y limpia (ver [5.5](#55-perfume_genderdatapy-leer-y-limpiar-el-dataset)).

```python
vocab_all = build_vocab(df["accords_dict"])
vocab = build_vocab(df["accords_dict"], min_count=MIN_ACCORD_COUNT)
dropped = sorted(set(vocab_all) - set(vocab))
```
Arma el vocabulario completo (92 acordes) y el reducido (72). `dropped` es la diferencia: los 20 acordes descartados (`tennis ball`, `bbq`, `wet plaster`…). Se anotan en `stats`.

```python
idx_train, idx_test = train_test_split(df.index, test_size=config.TEST_SIZE,
                                       stratify=df["gender"], random_state=config.SEED)
df["split"] = "train"
df.loc[idx_test, "split"] = "test"
```
**La división train/test:**
- `train_test_split` de scikit-learn divide los números de fila al azar: 80 % / 20 %.
- `stratify=df["gender"]`: **estratificada** (mantiene las proporciones de género).
- `random_state=config.SEED`: semilla fija.
- Se crea una columna `split` con `"train"` o `"test"` para cada perfume. Así **todos los scripts posteriores usan exactamente la misma división**.

Comentario clave del código: *"Como ya se deduplicaron los perfiles idénticos, ningún perfil exacto puede estar a la vez en train y en test"*.

```python
df["perc_votes"] = perception_votes(df)
df["perc_index"] = perception_index(df)
with_votes = df["perc_votes"] >= 1
```
Calcula el total de votos de percepción y el **índice** de cada perfume; marca cuáles tienen al menos 1 voto (los únicos que tienen índice).

```python
stats["perceived"] = {"rows_with_votes": ..., "train_rows_with_votes": ..., "test_rows_with_votes": ...,
                      "votes_mean": ..., "votes_median": ..., "votes_p75": ..., "votes_p90": ...,
                      "rating_votes_mean": ..., ...}
```
Guarda las estadísticas que cita el README: **100.541** perfumes con votos (**80.465** en train, el 81,8 %); media de votos de percepción 64,5 y mediana 5; media de votos de rating 172,5 y mediana 13.

```python
cols = ["id", "brand", "gender", "vote_count", "accords", "notes_top", ..., "split", *PERCEIVED_COLUMNS, "perc_votes", "perc_index"]
df[cols].to_csv(config.DATA_PROCESSED / "clean.csv.gz", index=False)
save_vocab(vocab, config.VOCAB_PATH)
```
Guarda el CSV limpio con **solo las columnas necesarias** (`index=False` = sin la columna de numeración de pandas). La extensión `.gz` hace que pandas lo **comprima** automáticamente. También guarda el vocabulario y, al final, el reporte `etl.json`.

---

## 6.5 `pipeline/03_experiments.py`: tres experimentos para decidir

**Para qué sirve:** antes de elegir modelo, se prueban **tres preguntas de datos** con un modelo rápido, y las respuestas fundamentan decisiones del proyecto. Usa una **validación interna**: aparta el 20 % del train (nunca toca el test).

### Funciones ayudantes

```python
def notes_matrix(df, top=300):
    ...
```
**`notes_matrix`.** Arma una matriz de las **300 notas más frecuentes** (ingredientes), con un `1` si el perfume la tiene y `0` si no. Se usa **solo en el experimento 1** (el proyecto no usa notas en producción). Combina cuatro columnas de notas (`notes_top`, `notes_middle`, `notes_base`, `notes_flat`); usa un `set` por perfume para no repetir y un `Counter` para contar qué notas son más frecuentes.

```python
def model(class_weight=None):
    return HistGradientBoostingClassifier(max_iter=200, learning_rate=0.1, class_weight=class_weight, ...)
```
**`model`.** Un Gradient Boosting rápido y simple para los experimentos. El parámetro `class_weight` permite probar la versión "equilibrada".

```python
def score(clf, Xtr, ytr, Xva, yva, mask_va=None):
    t = time.time()
    clf.fit(Xtr, ytr)
    pred = clf.predict(Xva)
    if mask_va is not None:
        pred, yva = pred[mask_va], yva[mask_va]
    return {"macro_f1": ..., "accuracy": ..., "seconds": ...}
```
**`score`.** Entrena, predice y devuelve F1 macro, exactitud y cuántos segundos tardó. `mask_va` permite evaluar solo sobre algunas filas.

### Experimento E1: ¿acordes, notas o ambos?
Entrena tres modelos iguales con distintas entradas y compara: **solo acordes** (0,598), **acordes + notas** (0,670) y **solo notas** (0,667). `np.hstack([X, N])` pega las dos matrices lado a lado. **Conclusión:** las notas aportan ~7 puntos de F1, pero se decidió no usarlas porque se asume que el perfumista aún no las tiene definidas.

### Experimento E2: ¿conviene equilibrar las clases?
Prueba **sin pesos**, **`class_weight="balanced"`** y **submuestreo** (dejar todas las clases con la misma cantidad que la más chica: `rng.choice(..., n_min, replace=False)` sortea `n_min` filas de cada clase). Resultado: **no equilibrar** es lo mejor (ver [2.7](#27-desbalance-de-clases-y-las-soluciones-que-se-probaron)).

### Experimento E3: ¿conviene filtrar por votos de rating?
Entrena quedándose solo con perfumes con al menos 0, 5, 20 y 50 votos (de rating), y evalúa en toda la validación y en la parte "confiable" (≥ 20 votos). Resultado: casi no cambia (0,596 a 0,602) mientras se pierde mucho dato (de 78.691 a 23.311 filas): **no se filtra**.

Guarda todo en `reports/experiments.json`.

---

## 6.6 `pipeline/04_train.py`: entrenar y elegir el clasificador

**Para qué sirve:** compara los 6 candidatos con **validación cruzada**, afina el mejor, lo entrena con todo el train y lo evalúa **una sola vez en el test**.

```python
SVM_SUBSAMPLE = 20_000
```
La SVM es muy lenta con muchos datos, así que se la evalúa con una muestra de 20.000 filas (el `_` en `20_000` es solo para leer mejor el número).

```python
def stratified_subsample(y, n, seed):
    rng = np.random.default_rng(seed)
    idx = []
    for c in np.unique(y):
        pool = np.where(y == c)[0]
        idx.append(rng.choice(pool, int(round(n * len(pool) / len(y))), replace=False))
    return np.sort(np.concatenate(idx))
```
**`stratified_subsample`.** Saca una **muestra más chica manteniendo las proporciones de cada clase**: para cada clase, elige al azar una cantidad proporcional a su tamaño.

### Paso 0: preparar
```python
df, X, vocab = load_dataset()
tr = (df["split"] == "train").values
te = ~tr
Xtr, ytr, Xte, yte = X[tr], df.loc[tr, "gender"].values, X[te], df.loc[te, "gender"].values
```
Carga los datos y separa la matriz y las etiquetas en **train** (`Xtr`, `ytr`) y **test** (`Xte`, `yte`) usando la columna `split`.

```python
cv = StratifiedKFold(n_splits=config.CV_FOLDS, shuffle=True, random_state=config.SEED)
scoring = {"macro_f1": "f1_macro", "accuracy": "accuracy"}
```
Define la **validación cruzada estratificada de 5 pedazos** (mezclando antes de partir) y las dos métricas a medir.

### Paso 1: comparar candidatos por validación cruzada
```python
for name, est in candidates().items():
    ...
    res = cross_validate(est, Xs, ys, cv=cv, scoring=scoring, n_jobs=...)
    report["cv"][name] = {"macro_f1_mean": ..., "macro_f1_std": ..., "accuracy_mean": ..., "fit_seconds_per_fold": ..., "note": note}
```
Para cada uno de los 6 modelos: ejecuta la validación cruzada y guarda **el promedio y el desvío del F1 macro**, la exactitud media y cuánto tardó. A la SVM se le da la submuestra. `n_jobs=-1` usa todos los núcleos (para el Random Forest se usa 1, porque ese modelo ya usa todos internamente).

### Paso 2: afinar el Gradient Boosting
```python
search = RandomizedSearchCV(base, {...opciones...}, n_iter=10, scoring="f1_macro", cv=3,
                            random_state=config.SEED, n_jobs=-1, refit=False)
search.fit(Xtr, ytr)
```
Prueba **10 combinaciones al azar** de estas opciones: `learning_rate` ∈ {0,03; 0,05; 0,08; 0,12}; `max_leaf_nodes` ∈ {15, 31, 63}; `min_samples_leaf` ∈ {20, 50, 100}; `l2_regularization` ∈ {0; 0,1; 1; 5}; `max_iter` ∈ {300, 500}. Cada una se evalúa con validación cruzada de 3 pedazos. `refit=False` = "no reentrenes el ganador, solo decime cuál fue".

```python
tuned = clone(base).set_params(**search.best_params_)
res = cross_validate(tuned, Xtr, ytr, cv=cv, scoring=scoring, n_jobs=-1)
```
Crea un modelo nuevo con la **mejor combinación** (`clone` = copia sin entrenar; `set_params(**...)` aplica las perillas ganadoras) y lo evalúa con la misma validación cruzada de 5 pedazos para poder compararlo con los demás. Mejores perillas: `learning_rate=0,08`, `max_leaf_nodes=63`, `min_samples_leaf=20`, `max_iter=300`, `l2_regularization=0`.

### Paso 3: elegir al ganador
```python
servible = {k: v for k, v in report["cv"].items()
            if not k.startswith("Baseline") and not v["note"].startswith("submuestra")}
winner = max(servible, key=lambda k: servible[k]["macro_f1_mean"])
final = tuned if winner.endswith("ajustado") else candidates()[winner]
final.fit(Xtr, ytr)
```
Entre los modelos **"servibles"** (se excluye el baseline, que es un modelo tonto, y la SVM, que solo se probó con una submuestra y no entrega probabilidades de forma nativa) se elige el de **mayor F1 macro medio** en validación cruzada. Luego se **entrena el ganador con todo el train**. **Importante:** hasta acá el test no se usó.

### Paso 4: el examen final (test)
```python
pred = final.predict(Xte)
cm = confusion_matrix(yte, pred, labels=classes)
cr = classification_report(yte, pred, labels=classes, output_dict=True, zero_division=0)
majority = max((yte == c).mean() for c in classes)
```
Predice sobre el test **por única vez** y calcula: la **matriz de confusión**, el **reporte por clase** (precisión, recall, F1, soporte) y el **baseline** (la proporción de la clase mayoritaria en el test). `zero_division=0` evita errores si una clase no se predijera nunca.

### Paso 5: guardar
```python
joblib.dump(final, config.MODEL_PATH, compress=3)
...
update_metadata(classifier=metadata, class_priors=priors)
```
Guarda el modelo (`compress=3` lo comprime), arma los **metadatos** (nombre del modelo, clases, cantidad de features, tamaño, versión de scikit-learn, fecha de entrenamiento…) y las **frecuencias base** (`priors`: qué proporción de cada clase hay en el train, que luego se usa para el *lift*). Guarda `reports/metrics.json`.

---

## 6.7 `pipeline/05_train_index.py`: entrenar el modelo principal

**Para qué sirve:** entrena el **regresor del índice** y lo compara contra el clasificador.

```python
N_REFERENCIA = 10
N_SENSIBILIDAD = (10, 30, 100)
ZONE_LABELS = ["female", "unisex", "male"]
COMPOSICION = {"alcohol": 9, "cannabis": 15, "chocolate": 16, "woody": 84, "aldehydic": 5, "leather": 75, "smoky": 61}
```
- La **evaluación de referencia** se hace con perfumes de **al menos 10 votos** de percepción; también se reporta con 30 y 100 (para ver si el resultado se sostiene).
- `COMPOSICION` es **el perfil de ejemplo** aportado por un usuario (el "caso de prueba").

```python
def nuevo_regresor(seed=config.SEED):
    return HistGradientBoostingRegressor(max_iter=300, learning_rate=0.08, max_leaf_nodes=31,
        min_samples_leaf=40, early_stopping=True, validation_fraction=0.1, n_iter_no_change=20, random_state=seed)
```
**`nuevo_regresor`.** Crea un Gradient Boosting **para regresión** (predice números). Sus perillas son **fijas**: no se ajustaron con el test.

```python
def metricas(real, pred, zonas_pred=None):
    zr = zone(real)
    zp = zone(pred) if zonas_pred is None else zonas_pred
    return {"mae": ..., "r2": ..., "spearman": ..., "zonas_f1_macro": ..., "zonas_exactitud": ...}
```
**`metricas`.** Calcula las cinco métricas del modelo de índice (ver [2.6](#26-métricas-del-modelo-de-índice-regresión)). Convierte lo real y lo predicho a **zonas** para el F1 por zonas.

```python
def curva(real, pred, bins=10):
    edges = np.quantile(pred, np.linspace(0, 1, bins + 1))
    ids = np.clip(np.digitize(pred, edges[1:-1]), 0, bins - 1)
    return (np.array([pred[ids == b].mean() ...]), np.array([real[ids == b].mean() ...]))
```
**`curva`.** Prepara los datos del **gráfico de calibración**: ordena los perfumes por valor predicho, los reparte en 10 grupos de igual tamaño (**deciles**: `np.quantile` y `np.digitize`) y calcula, en cada grupo, el índice predicho promedio y el índice real promedio. Si el modelo es bueno, ambos coinciden.

### El flujo de `main`

**1. Cargar y elegir las filas de entrenamiento.**
```python
tr = es_train & (votos >= 1)
X_tr, y_tr, w_tr = X[tr], indice[tr], vote_weight(votos[tr])
```
Solo se entrena con perfumes **de train** que tengan **al menos 1 voto de percepción** (80.465, el 81,8 % del train). Cada uno tiene su **peso** `√min(votos, 100)`.

**2. Validación cruzada.**
```python
for k, (a, b) in enumerate(KFold(config.CV_FOLDS, shuffle=True, random_state=config.SEED).split(X_tr)):
    m = nuevo_regresor().fit(X_tr[a], y_tr[a], sample_weight=w_tr[a])
    fiable = votos[tr][b] >= N_REFERENCIA
    p = np.clip(m.predict(X_tr[b][fiable]), 0, 1)
    cv_mae.append(...); cv_sp.append(...)
```
Divide el train en 5 pedazos (`KFold`, que no es "estratificado" porque no hay clases en una regresión). Entrena con 4 (pasándole los **pesos** con `sample_weight`), predice en el 5.º **solo sobre los perfumes con ≥ 10 votos** (los confiables) y guarda error y Spearman. Resultado: **MAE 0,126 ± 0,001** y **Spearman 0,809 ± 0,004**.

**3. Entrenar el modelo final.**
```python
modelo = nuevo_regresor().fit(X_tr, y_tr, sample_weight=w_tr)
```
Con todo el train con votos y los pesos.

**4. Evaluación única en test: A contra B.**
```python
clasificador = joblib.load(config.MODEL_PATH)
proba = clasificador.predict_proba(X)
for n in N_SENSIBILIDAD:
    te = es_test & (votos >= n)
    trn = es_train & (votos >= n)
    y_te = indice[te]
    m_clase = np.array([indice[trn & (df["gender"] == c).values].mean() for c in clases])
    pred_a = proba[te] @ m_clase
    argmax_a = np.array(clases)[proba[te].argmax(axis=1)]
    pred_b = np.clip(modelo.predict(X[te]), 0, 1)
```
Para cada umbral de votos (10, 30, 100):
- **Modelo A (el clasificador convertido a índice):** como el clasificador no da un número sino probabilidades, se calcula un **índice esperado**: `p_fem × índice_medio_fem + p_masc × índice_medio_masc + p_unisex × índice_medio_unisex`. El "índice medio de cada clase" sale del train (`m_clase`; por ejemplo el índice medio de los masculinos es ~0,81 y el de los unisex ~0,47). `proba[te] @ m_clase` es esa suma en forma de multiplicación de matrices.
- **A con "argmax":** alternativa donde la zona de A es simplemente la clase más probable.
- **Modelo B:** la predicción directa del regresor (limitada a [0, 1]).

Se calculan las métricas de cada uno y la **mejora del error**: `100 × (MAE_A − MAE_B) / MAE_A` (20,1 % en el nivel de referencia).

**5. Criterios de éxito.**
```python
criterios = {
  "mae_10pct_menor_en_N10": ...mejora >= 10,
  "spearman_no_peor_en_N10": ...,
  "zonas_f1_macro_065_en_N10": ...>= 0.65,
  "mismo_patron_en_N30_y_N100": ...,
}
```
Se escribieron **antes** de mirar los resultados: el modelo nuevo solo se adopta si (1) baja el error al menos 10 %, (2) no empeora Spearman, (3) llega a F1 por zonas de 0,65 y (4) lo mismo se repite con 30 y 100 votos. Los cuatro se cumplieron.

**6. El caso de prueba.** Pasa la composición del usuario por los dos modelos: el clasificador dice **femenino 3 % / masculino 7 % / unisex 90 %** (índice esperado 0,479, al medio), el modelo de índice dice **0,717 → zona masculina**.

**7. Gráficos y archivos.** Genera: `index_calibracion.png`, `index_metricas.png`, `index_zonas.png`. Guarda `models/index_model.joblib`, la sección `index_model` de `metadata.json` y `reports/index_metrics.json`.

---

## 6.8 `pipeline/06_evaluate.py`: evaluación extra del clasificador

**Para qué sirve:** genera los gráficos y análisis adicionales del clasificador para el README. Lee los resultados que dejaron los pasos anteriores.

1. **Matriz de confusión como gráfico** (`model_confusion.png`): cada celda muestra el **porcentaje por fila** y el conteo. `cm / cm.sum(axis=1, keepdims=True)` divide cada fila por su total.
2. **Comparación de modelos** (`model_comparacion.png`): barras horizontales del F1 macro de cada candidato, con "bigotes" que muestran el desvío (`xerr`); el ganador en rosa.
3. **Experimentos** (`model_experimentos.png`): barras de E1 (qué información usar) y E2 (cómo tratar el desbalance).
4. **Calibración** (`model_calibracion.png` y los ECE). Para cada clase compara "probabilidad predicha" vs. "frecuencia observada" con `calibration_curve` (10 grupos de igual tamaño). El ECE se calcula a mano: promedia, por grupo, cuánto se aparta lo observado de lo predicho, ponderado por el tamaño del grupo.
5. **Importancia por permutación** (`model_importancia.png`): con 6.000 perfumes de test elegidos al azar, `permutation_importance` mezcla cada acorde 5 veces y mide cuánto cae el F1 macro. Guarda los 15 más importantes.
6. **Rendimiento según votos** (en el reporte): F1 y exactitud por tramos de votos de rating (0–4, 5–19, 20–99, 100+).
7. **Robustez por marca**: `GroupShuffleSplit` con **grupos = marca** hace una partición donde ninguna marca está en los dos lados; se entrena un modelo nuevo (`clone(model)`) y se mide. Resultado: F1 macro 0,598, igual que con partición aleatoria (0,599): el modelo funciona con marcas que no vio.

Guarda `reports/evaluation.json`.

---

## 6.9 `pipeline/run_all.py`: todo de una

```python
STEPS = ["01_eda.py", "02_etl.py", "03_experiments.py", "04_train.py",
         "05_train_index.py", "06_evaluate.py", "../experiments/vote_weights.py"]

for step in STEPS:
    print(f"\n=== {step} ===", flush=True)
    t = time.time()
    subprocess.run([sys.executable, str(here / step)], check=True)
    print(f"({time.time() - t:.0f}s)", flush=True)
```
Recorre la lista **en orden** y ejecuta cada script como un **proceso aparte** (`subprocess.run`) con el mismo Python (`sys.executable`). `check=True` hace que, **si un paso falla, todo se detiene** (no tiene sentido seguir con datos incompletos). Imprime cuánto tardó cada paso.

---

## 6.10 `experiments/vote_weights.py`: ¿filtrar o ponderar por votos?

Un estudio **aparte del pipeline principal** que justifica la decisión de usar pesos `√votos`. Usa **solo el train** y evalúa en perfumes con ≥ 30 votos de percepción.

```python
def evaluar(X, y, v, a, b, n_min, pesos, seed):
    ia = a[v[a] >= n_min]
    m = regresor(seed).fit(X[ia], y[ia], sample_weight=pesos(v[ia].astype(float)))
    vb = b[v[b] >= N_VALIDACION]
    pred = np.clip(m.predict(X[vb]), 0, 1)
    return len(ia), mae(...), spearman(...)
```
Entrena con las filas `a` que tengan al menos `n_min` votos, usando la función de pesos indicada; evalúa en las filas `b` con ≥ 30 votos.

**Parte 1:** prueba filtros de 1, 3, 5, 10, 15, 20, 30, 50 y 100 votos **sin pesos** (una partición).
**Parte 2:** compara 8 "esquemas" (sin filtro, filtro mínimo 5, distintos topes, `√votos`, combinaciones) con **3 particiones distintas** (semillas 42, 7 y 123) y promedia.

**Resultado:** filtrar no ayuda; ponderar mejora apenas (~1,5 %). Se elige `√votos con tope 100`. Los resultados quedan en `reports/vote_weights.json` y se muestran también en la pestaña "El modelo" de la página.

---

# Parte 7: La aplicación (backend y frontend)

La aplicación es lo que usa el perfumista. Tiene dos mitades que se hablan por internet (aunque acá, en el mismo equipo):

```
  Tu navegador (frontend)                       Servidor (backend)
  ┌───────────────────────┐   POST /api/predict   ┌───────────────────────────┐
  │ index.html + app.js   │ ───────────────────→  │ main.py (FastAPI)         │
  │ "tengo estos acordes" │   (acordes en JSON)   │  → predictor.py           │
  │                       │ ←───────────────────  │  → modelos .joblib        │
  │ dibuja el resultado   │   (resultado en JSON) │                           │
  └───────────────────────┘                       └───────────────────────────┘
```

---

## 7.1 `app/backend/schemas.py`: qué datos se aceptan y se devuelven

**Para qué sirve:** define la **forma exacta** de los mensajes. Con esto, FastAPI **valida automáticamente** que lo que llega sea correcto y **documenta** la API sola (en `http://localhost:8000/docs`).

**Pydantic** es la librería que hace esas validaciones: cada clase describe un "formulario" y sus campos con reglas.

```python
class AccordInput(BaseModel):
    name: str = Field(min_length=1, max_length=40, examples=["woody"])
    intensity: float = Field(gt=0, le=100, description="Intensidad relativa 0-100", examples=[80])
```
**`AccordInput` (un acorde que manda el usuario).**
- `name`: texto de 1 a 40 caracteres.
- `intensity`: número **mayor que 0** (`gt` = greater than) y **menor o igual a 100** (`le` = less or equal).
- `examples`: ejemplos que aparecen en la documentación.

```python
class PredictRequest(BaseModel):
    accords: list[AccordInput] = Field(min_length=1, max_length=MAX_ACCORDS)
    model_config = {"json_schema_extra": {"example": {...}}}
```
**`PredictRequest` (el pedido completo).** Una **lista de acordes**, con al menos 1 y como máximo 8. `model_config` agrega un ejemplo para la documentación.

```python
class Influence(BaseModel):
    accord: str
    index_effect: float = Field(description="Cambio del indice al quitar el acorde (+ = empuja a masculino)")
    pushes_toward: str = Field(description="male | female | neutral")
```
**`Influence`.** Un renglón de "qué acordes pesan más": el acorde, cuánto cambia el índice si se quita y hacia dónde empuja.

```python
class PredictResponse(BaseModel):
    index: float = Field(ge=0, le=1, ...)
    zone: str
    male_vs_female: dict[str, float]
    class_probabilities: dict[str, float]
    lift: dict[str, float]
    accords_used: dict[str, float]
    influences: list[Influence]
```
**`PredictResponse` (la respuesta).** Los siete elementos que devuelve el servidor: índice (entre 0 y 1), zona, lectura femenino vs. masculino, probabilidades por clase, *lift*, los acordes que realmente se usaron (ya normalizados y reescalados) y las influencias. `ge` = greater or equal.

---

## 7.2 `app/backend/main.py`: el servidor

```python
from __future__ import annotations
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
```
**Imports.** `FastAPI` crea la aplicación, `HTTPException` permite devolver errores con código de estado, `CORSMiddleware` aplica la regla de seguridad CORS y `StaticFiles` sirve archivos (la página web).

```python
log = logging.getLogger("perfume_gender")
FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"
```
- `log`: un "registro" para anotar mensajes del servidor (por ejemplo "Modelo cargado").
- `FRONTEND_DIR`: la carpeta donde está la página web (`app/frontend`).

### El arranque (`lifespan`)
```python
@asynccontextmanager
async def lifespan(app):
    try:
        app.state.predictor = Predictor.load()
        log.info("Modelo cargado: %s", ...)
    except FileNotFoundError as exc:
        app.state.predictor = None
        app.state.load_error = str(exc)
        log.warning("%s", exc)
    yield
```
**"Lo que hace el servidor al encenderse".** `lifespan` define el ciclo de vida: **todo lo que está antes del `yield`** se ejecuta al arrancar.
- Carga el `Predictor` (los dos modelos) **una sola vez**, y lo guarda en `app.state` (un "cajón compartido" de la aplicación). Cargar un modelo es lento; hacerlo en cada pedido sería un desperdicio.
- Si faltan los archivos (`FileNotFoundError`), el servidor **arranca igual** pero con el predictor vacío y deja un aviso. Después `/api/health` informa `model_missing`. Así el error es claro en vez de que el servidor "se muera".

### La aplicación y su configuración
```python
app = FastAPI(title="...", description="...", version="2.0.0", lifespan=lifespan)
```
Crea la aplicación con su título, descripción y versión (que se ven en `/docs`).

```python
app.add_middleware(CORSMiddleware,
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_methods=["GET", "POST"], allow_headers=["Content-Type"])
```
**CORS (seguridad).** Solo se permite que páginas que vienen de `localhost` o `127.0.0.1` (tu propia computadora) llamen a la API, solo con los métodos GET y POST. La expresión regular `^http://(localhost|127\.0\.0\.1)(:\d+)?$` significa: "empieza con `http://`, luego `localhost` o `127.0.0.1`, y opcionalmente `:` seguido de un número de puerto".

```python
def get_predictor():
    predictor = getattr(app.state, "predictor", None)
    if predictor is None:
        raise HTTPException(503, "Modelo no disponible. ...")
    return predictor
```
**`get_predictor`.** Función ayudante: devuelve el predictor o, si no está cargado, responde **503 "servicio no disponible"** con un mensaje explicativo.

### Los endpoints (las "direcciones" que atiende)
```python
@app.get("/api/health")
def health():
    ok = getattr(app.state, "predictor", None) is not None
    return {"status": "ok" if ok else "model_missing"}
```
**`GET /api/health`** ("chequeo de salud"): responde `{"status": "ok"}` si todo anda. Sirve para comprobar rápido que el servidor y los modelos están vivos (se usa, por ejemplo, para verificar Docker).

```python
@app.get("/api/accords")
def accords():
    p = get_predictor()
    return {"accords": p.vocab, "max_accords": config.MAX_ACCORDS}
```
**`GET /api/accords`:** devuelve la lista de los 72 acordes válidos y el máximo (8). La página la usa para dibujar los botones de acordes.

```python
@app.post("/api/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    p = get_predictor()
    try:
        return p.predict({a.name: a.intensity for a in req.accords})
    except InvalidAccordsError as exc:
        raise HTTPException(422, str(exc)) from exc
```
**`POST /api/predict`: el endpoint principal.**
- `req: PredictRequest` hace que FastAPI **valide** lo que llegó con las reglas de `schemas.py` (si no cumple, responde 422 solo).
- `{a.name: a.intensity for a in req.accords}` convierte la lista de acordes en el diccionario que espera el predictor.
- Si el predictor detecta un problema (acorde desconocido, etc.), responde **422** con el mensaje.
- `response_model=PredictResponse` asegura que la respuesta tenga el formato definido.

```python
@app.get("/api/model/info")
def model_info():
    p = get_predictor()
    info = {"metadata": p.metadata}
    for key, fname in (("classifier_metrics", "metrics.json"), ("index_metrics", "index_metrics.json"),
                       ("experiments", "experiments.json"), ("vote_weights", "vote_weights.json"),
                       ("eda", "eda.json")):
        path = config.REPORTS_DIR / fname
        if path.exists():
            info[key] = json.loads(path.read_text(encoding="utf-8"))
    return info
```
**`GET /api/model/info`:** junta los metadatos con los reportes del pipeline (`reports/*.json`) y los devuelve. Es lo que usa la pestaña "El modelo". **Nada está escrito a mano en la página**: todos los números salen de los reportes reales, así que no pueden quedar desactualizados.

```python
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
```
**Servir la página web.** Cualquier dirección que no sea de la API (`/`, `/app.js`, `/styles.css`) se atiende entregando los archivos de `app/frontend`. `html=True` hace que `/` entregue `index.html`. **Va al final** a propósito: si estuviera al principio taparía los endpoints de la API.

---

## 7.3 `app/frontend/index.html`: la estructura de la página

La página tiene una **barra superior** (logo, pestañas y botón de tema), **dos pestañas** ("Predictor" y "El modelo"), un **pie** y, solo en celular, una **barra flotante** con el resultado. Se explica por zonas.

### `<head>` (información de la página)
```html
<html lang="es" data-theme="dark">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#0f0d12">
<link rel="icon" type="image/svg+xml" href="assets/logo-mark.svg">
```
- `lang="es"`: le avisa al navegador y a los lectores de pantalla que el idioma es español.
- `data-theme="dark"`: un **atributo propio** (los `data-*` sirven para guardar datos en un elemento) que indica el tema. El CSS lee este valor para elegir los colores.
- `viewport`: hace que la página se **adapte al ancho del celular**.
- `theme-color`: el color con que el celular pinta la barra del navegador.
- `link rel="icon"`: el **ícono de la pestaña** del navegador (el isotipo en formato SVG).

```html
<script>
  (function () {
    var t = null;
    try { t = localStorage.getItem("scentai-theme"); } catch (e) { }
    if (t !== "light" && t !== "dark") t = matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
    document.documentElement.dataset.theme = t;
  })();
</script>
```
**Un script mínimo que corre antes de dibujar la página.** Decide el tema: si el usuario ya eligió uno antes, lo lee de `localStorage` (una pequeña memoria del navegador); si no, mira la preferencia del sistema operativo (`prefers-color-scheme`). Se hace **antes** del primer dibujo para evitar el "parpadeo" (que la página se vea oscura un instante y luego cambie a clara). El `try/catch` es porque algunos navegadores bloquean `localStorage` (por ejemplo, en modo privado): en ese caso simplemente no hay preferencia guardada.

### Cabecera y pestañas
```html
<a class="skip-link" href="#main">Saltar al contenido</a>
<header class="topbar"> ... brand ... <nav class="tabs" role="tablist"> ... </nav> <button id="theme-toggle"> ... </header>
```
- **`skip-link`:** un enlace oculto que aparece al presionar `Tab` en el teclado y permite **saltar directo al contenido** sin recorrer la barra superior (accesibilidad).
- **`brand`:** el logo (`assets/logo-mark.svg`) y el nombre "Scent**AI**" (la parte "AI" va en cursiva y con el degradé de la marca).
- **Pestañas:** dos botones con `role="tab"`, `aria-selected` (cuál está activa) y `aria-controls` (qué panel controlan). El inactivo tiene `tabindex="-1"` para que la navegación con flechas del teclado funcione bien.
- **`theme-toggle`:** el botón del sol/luna. Su ícono lo inserta JavaScript.

### El aviso de error y el "anunciador"
```html
<div id="banner" class="banner" role="alert" hidden> ... <button id="banner-close"> ... </div>
<p class="sr-only" id="sr-status" role="status" aria-live="polite"></p>
```
- `banner`: la franja roja de error (oculta con `hidden`), ahora con un botón para **cerrarla**.
- `sr-status`: un párrafo invisible (`sr-only`) donde JavaScript escribe mensajes como "Ejemplo Floral dulce cargado" o "Tiende a masculino. Índice 0,72". Los **lectores de pantalla** lo leen en voz alta sin interrumpir (`aria-live="polite"`).

### Pestaña "Predictor"
**El "hero" (portada):** una etiqueta "Para perfumistas", el título grande (`<h1>`: "¿Hacia qué lado del espectro cae tu perfume?") y una bajada explicativa.

**El "workspace" (área de trabajo)** tiene dos columnas:

*Columna izquierda (tarjeta `builder`), con dos pasos numerados:*
1. **"Elegí los acordes":** el contador `n / 8`; los **ejemplos** (`#presets`, ahora tarjetas con nombre y tres acordes de muestra); el **buscador** con ícono de lupa y un botón para borrar el texto; una línea de estado (`chips-status`: "72 acordes disponibles" o "5 de 72 acordes"); y la nube de **botones de acordes** (`#chips`) dentro de un contenedor con scroll.
2. **"Ajustá la intensidad":** el botón "Limpiar todo", las filas con deslizadores (`#selected`) y, mientras no hay ninguno, un cuadro vacío con una explicación (`selected-empty`).

*Columna derecha (`aside.summary`, la tarjeta de resultado):*
- **Estado vacío** (`result-empty`): el isotipo, "Tu resultado aparece acá" y un botón **"Probar un ejemplo"** (carga el primer ejemplo).
- **Resultado** (`#result`, oculto hasta que haya predicción): el título "Posición en el espectro", el veredicto (`verdict`) junto al **número del índice** (`index-num`, con la etiqueta "índice"), el **espectro** (`spectrum-track` con su `spectrum-marker`, más la escala con "Femenino / Unisex / Masculino"), una frase explicativa (`verdict-sub`) y el aviso de que es orientación estadística.

**La "lectura detallada"** (`#details`, oculta hasta que haya resultado) está **debajo**, a todo el ancho, y tiene tres tarjetas: *Femenino vs. masculino* (`duel`), *Probabilidad según la etiqueta de género* (`bars`) y *Qué acordes pesan más* (`influences`, con un eje "← Femenino / Masculino →" debajo).

> **Cambio de diseño:** antes todo el resultado estaba apretado en una tarjeta. Ahora arriba queda **lo esencial** (posición e índice) y debajo el **detalle**, lo que hace la pantalla más clara.

### Pestaña "El modelo"
Una portada ("Qué hay detrás del resultado") y varias tarjetas con **tablas vacías** que JavaScript rellena con los reportes: los cuatro indicadores del modelo de índice (`tiles`, con "esqueletos" de carga mientras llegan los datos), la comparación índice vs. clasificador (`cmp-table`), el estudio de pesos (`weights-table`), el análisis etiqueta vs. percepción (`bias-text`, `exp-table`) y los datos del clasificador (`cv-table`, `cm-table`, `class-table`).

### Pie y barra flotante
- **`footer`:** el isotipo y la leyenda del proyecto.
- **`minibar`:** un botón fijo en la parte de abajo que **solo aparece en celular**, cuando ya bajaste y el resultado quedó fuera de pantalla. Muestra el veredicto, el índice y una mini barra con el marcador; al tocarlo, vuelve al resultado.

```html
<script src="app.js"></script>
```
Al final se carga el JavaScript, para que los elementos de arriba ya existan cuando el código los busque.

---

## 7.4 `app/frontend/styles.css`: el aspecto

El archivo está organizado en secciones (con comentarios de cabecera). Lo más importante:

### Los "tokens" de diseño (variables) y los dos temas
```css
:root {
  --bg: #0f0d12;  --surface: #17141c;  --text: #f3eee6;  ...
  --female: #f472a6;  --unisex: #f4c76a;  --male: #5aa9f7;
  --female-t: #f58db6;  --unisex-t: #f4c76a;  --male-t: #7bb8f8;
  --s-1: 0.25rem; ... --s-7: 3rem;
  color-scheme: dark;
}
:root[data-theme="light"] { --bg: #f6f1ea;  --surface: #fffdf9;  --text: #1d1822; ... color-scheme: light; }
```
- Las **variables CSS** (`--nombre`) son valores con nombre que se reutilizan con `var(--nombre)`. Si cambiás una, cambia en toda la página.
- **Dos temas:** el bloque `:root` define el **oscuro** (por defecto) y `:root[data-theme="light"]` **redefine las mismas variables** para el claro. Cuando JavaScript cambia `data-theme`, toda la página cambia de colores sola.
- **Colores de datos con dos versiones:** `--female` (para **rellenos**: barras, gráficos) y `--female-t` (para **texto**). En el tema claro el texto necesita colores **más oscuros** para que se lea bien sobre fondo claro (contraste), mientras que el relleno puede ser más vivo. Lo mismo para unisex y masculino.
- **Escala de espaciado:** `--s-1` a `--s-7` son múltiplos de 4 píxeles; usar siempre los mismos valores da **ritmo visual** consistente.
- **Tipografías:** se usan las que ya trae el sistema (`system-ui`, y una serif tipo "Palatino/Georgia" para los títulos). No se descarga nada de internet.

La idea de diseño, escrita en el propio archivo: el **degradé rosa → dorado → azul del espectro es el único color de marca**; el resto de la interfaz es neutro (marfil y tinta), así los colores de datos significan **siempre lo mismo** (rosa = femenino, dorado = intermedio, azul = masculino).

### Reglas generales
- `[hidden] { display: none !important; }`: garantiza que lo marcado `hidden` **se oculte siempre**, aunque otra regla le diga lo contrario.
- `body::before`: una **"aureola" decorativa**: dos luces suaves (rosa a la izquierda, azul a la derecha) con `radial-gradient` detrás del título.
- `:focus-visible`: un **contorno visible** cuando navegás con el teclado, igual en todos los controles.
- `.sr-only`, `.skip-link`: elementos para lectores de pantalla y para saltar contenido.

### Componentes
| Parte | Qué hace |
|---|---|
| `.btn`, `.icon-btn` | Botones (primario, secundario, "fantasma" y de solo ícono). |
| `.topbar` | Barra superior **pegajosa** (`position: sticky`): queda fija arriba al bajar. Tiene un efecto de vidrio esmerilado (`backdrop-filter: blur`). |
| `.brand-ai` | El "AI" del nombre, con el degradé de la marca **recortado al texto** (`background-clip: text`). |
| `.tabs` | Las pestañas como un **control segmentado**: la activa (`aria-selected="true"`) tiene fondo propio. |
| `.pane` / `.pane.active` | Cada panel; solo el activo se muestra, con una pequeña animación de entrada. |
| `.workspace` | La cuadrícula de **dos columnas** (constructor / resultado). La columna del resultado es `position: sticky`: **te sigue al hacer scroll** en escritorio. |
| `.step`, `.step-num` | Los pasos numerados 1 y 2. |
| `.presets`, `.preset` | Los ejemplos como **tarjetas** en tres columnas; el seleccionado (`aria-current="true"`) tiene el borde resaltado. |
| `.chips-scroll`, `.chip` | La nube de acordes con scroll; los elegidos se rellenan con el color de acento y muestran un tilde. |
| `.row` | Cada acorde elegido: nombre, deslizador, valor y botón de quitar. |
| `.tile`, `table`, `.cm` | Los indicadores y tablas de la pestaña del modelo; la fila ganadora (`tr.best`) lleva una marca a la izquierda. |

### El deslizador personalizado
```css
input[type="range"] { --pct: 50%; ... }
input[type="range"]::-webkit-slider-runnable-track {
  background: linear-gradient(to right, var(--accent) var(--pct), var(--surface-3) var(--pct));
}
```
Los deslizadores nativos no pintan "lo ya recorrido". Acá se usa una **variable `--pct`** que **JavaScript actualiza** con la posición del deslizador, y un degradé de dos colores con un corte justo en ese porcentaje: la parte izquierda aparece rellena. Hay reglas separadas para Chrome/Edge (`-webkit-`) y Firefox (`-moz-`), porque cada navegador nombra distinto las partes del control.

### El espectro
```css
.spectrum-track { background: linear-gradient(90deg, var(--female) 0%, var(--female) 18%, var(--unisex) 40%, var(--unisex) 60%, var(--male) 82%, var(--male) 100%); }
.spectrum-track::before { left: 33%; }   .spectrum-track::after { left: 67%; }
.spectrum-marker { position: absolute; transform: translate(-50%, -50%); transition: left 0.3s ...; }
```
- La barra es un **degradé horizontal** rosa → dorado → azul.
- Los pseudo-elementos `::before` y `::after` dibujan **dos separadores finos** en el **33 %** y el **67 %**: son **los límites de las zonas** (0,33 y 0,67). Si algún día cambian esos límites en `perception.py`, hay que mover estos dos valores.
- El **marcador** es un círculo; JavaScript fija su `left` en porcentaje (índice × 100), y `transition` lo hace **deslizarse** con suavidad.
- La escala de abajo tiene tres columnas proporcionales (33 / 34 / 33) y **resalta la zona actual**: `.spectrum[data-zone="male"] [data-zone="male"]` significa "dentro de un espectro cuya zona es 'male', pintá la etiqueta 'male' de su color". El veredicto se colorea de forma parecida con `[data-zone="..."] .verdict`.

### Las barras de influencia "divergentes"
```css
.dtrack::before { left: 50%; ... }          /* línea central */
.dbar.female { right: 50%; background: var(--female); }
.dbar.male   { left: 50%;  background: var(--male); }
```
Cada acorde tiene una pista con una **línea en el centro**: si empuja hacia femenino, su barra **crece hacia la izquierda** (rosa); hacia masculino, **hacia la derecha** (azul); si es neutro, solo un puntito. Así se ve de un vistazo hacia qué lado empuja cada acorde y cuánto.

### Los "esqueletos" de carga
`.skeleton` con `animation: shimmer`: mientras llegan los datos del servidor, se muestran cajas grises con un **brillo que se desplaza** (`@keyframes shimmer`), en vez de un espacio vacío. Es una pista visual de que "está cargando".

### La barra flotante
```css
.minibar { position: fixed; bottom: ...; display: none; }
@media (max-width: 960px) { .minibar:not([hidden]) { display: flex; } body.has-minibar { padding-bottom: 84px; } }
```
Está **fija** abajo de la pantalla (`position: fixed`). Solo se muestra en pantallas de **960 px o menos** y cuando JavaScript no la tiene oculta. `body.has-minibar` agrega espacio abajo para que no tape el contenido.

### Adaptación a distintos tamaños
Los `@media` son reglas que se activan según el tamaño de pantalla:
- **≤ 960 px:** las dos columnas pasan a una; el resultado deja de ser pegajoso; aparece la barra flotante.
- **≤ 720 px:** las cuadrículas de dos columnas pasan a una.
- **≤ 560 px:** menos espacios; cada fila de acorde se reorganiza en dos renglones (nombre y quitar arriba, deslizador y valor abajo).
- **≤ 480 px:** los ejemplos pasan a dos columnas.
- **≤ 380 px:** se oculta el nombre "ScentAI" (queda solo el logo) para que entren las pestañas.
- **`pointer: coarse`:** en pantallas **táctiles** los botones son más grandes (más fáciles de tocar).
- **`prefers-reduced-motion: reduce`:** si el usuario pidió menos movimiento en su sistema, se **desactivan las animaciones**.

---

## 7.5 `app/frontend/app.js`: el comportamiento

Está dividido en secciones comentadas. Se explican en orden.

### Constantes y estado
```javascript
"use strict";
const CLASS_ES = { female: "Femenino", ... };       const ZONE_TEXT = { female: "Tiende a femenino", ... };
const CLASS_COLOR = { female: "var(--female)", ... }; const CLASS_TEXT = { female: "var(--female-t)", ... };
const ZONE_LIMITS = [0.33, 0.67];   const NEAR_LIMIT = 0.04;
const PRESETS = { "Fresco aromático": {...}, "Floral dulce": {...}, "Amaderado ahumado": {...} };
const ICONS = { sun: '<circle .../>', moon: '...', search: '...', ... };
```
- Los diccionarios traducen nombres internos al español y a colores (de relleno y de texto).
- **`ZONE_LIMITS` es una copia** de los límites de `perfume_gender/perception.py`. Se usa solo para **avisar cuando el índice está cerca de un borde** (a menos de `NEAR_LIMIT` = 0,04). Un comentario del código lo aclara. Si se cambian los límites, hay que cambiarlos en **tres lugares**: `perception.py`, esta constante y los separadores del CSS.
- `PRESETS`: los tres **ejemplos**.
- `ICONS`: el dibujo (en SVG) de cada ícono de la interfaz (sol, luna, lupa, cruz, tilde…). Así no hace falta descargar ninguna librería de íconos.

```javascript
const state = { vocab: [], max: 8, selected: new Map(), filter: "", timer: null, seq: 0,
                chipEls: new Map(), rows: new Map(), presetEls: new Map(), hasResult: false, summaryVisible: true, lastZone: null };
const dom = {};
```
`state` es **la memoria de la página**. Además de lo que ya existía (acordes válidos, seleccionados, buscador, temporizador y contador de pedidos), ahora guarda **referencias a elementos ya creados** (`chipEls`, `rows`, `presetEls`) para **reutilizarlos** en lugar de volver a dibujar todo, si hay resultado (`hasResult`), si el resultado se ve en pantalla (`summaryVisible`) y la última zona (`lastZone`). `dom` guarda los nodos del resultado que se crean **una sola vez** y después solo se actualizan.

### Herramientas de ayuda
- **`$(id)`:** atajo para buscar un elemento por su `id`.
- **`el(tag, props, ...hijos)`:** función propia que **crea elementos HTML**. Usa `textContent` (no `innerHTML`) para el texto, lo que es **seguro** contra inyección de código.
- **`icon(nombre)`:** construye un ícono SVG a partir de `ICONS`. Aquí sí se usa `innerHTML`, pero **solo con constantes del propio código**, nunca con datos externos.
- **`fmt`, `pct`, `nEs`:** formatean números al estilo argentino (coma decimal, punto de miles).
- **`announce(msg)`:** escribe en el párrafo `sr-status` para que los lectores de pantalla lo anuncien.
- **`showBanner(msg)`:** muestra u oculta la franja de error.
- **`api(path, options)`:** el pedido único al servidor (`fetch`); si la respuesta no es exitosa, lanza un error con el mensaje del servidor.

### El tema (claro / oscuro)
- **`applyTheme(theme, persist)`:** cambia `data-theme` en el documento, actualiza el texto del botón (accesibilidad), cambia el ícono (sol ↔ luna) y el `theme-color` de la barra del celular. Solo **guarda** la elección en `localStorage` si `persist` es verdadero (o sea, si el usuario la eligió a mano).
- **`initTheme()`:** conecta el botón y **escucha los cambios del sistema operativo** (`matchMedia(...).addEventListener("change", ...)`): si el usuario nunca eligió un tema, la página lo acompaña.

### Las pestañas
- **`selectTab(btn)`:** marca la pestaña activa (`aria-selected`, y `tabIndex` para que solo la activa esté en el orden del teclado), muestra el panel correspondiente, actualiza la dirección con `history.replaceState` (la pestaña "El modelo" queda como `#modelo`, así se puede **enlazar directo**) y vuelve arriba.
- **`initTabs()`:** conecta los clics y el **teclado**: flechas izquierda/derecha, `Home` y `End` cambian de pestaña (es la convención de accesibilidad para pestañas). Si la dirección ya trae `#modelo`, abre esa pestaña al cargar.

### Elegir acordes
- **`skeletonChips`:** mientras llega el vocabulario, muestra 20 botones "esqueleto" de distinto ancho.
- **`buildChips`:** **crea los 72 botones una sola vez** y los guarda en `state.chipEls`.
- **`updateChips`:** en vez de volver a dibujar, **actualiza los botones existentes**: oculta los que no coinciden con la búsqueda, marca los elegidos (`aria-pressed`) y les agrega un **tilde**, deshabilita los demás si ya hay 8, y actualiza el texto de estado ("Llegaste al máximo de 8 acordes…" o "5 de 72 acordes"). Se hace así para **no perder el foco del teclado**: si se destruyeran y recrearan los botones, quien navega con `Tab` perdería su posición.
- **`toggle(name)`:** agrega (con intensidad inicial 70) o quita un acorde.
- **`removeAccord(name)`:** quita un acorde y **mueve el foco** al siguiente (o al buscador), porque el botón que se usó desaparece.
- **`setFill(slider)`:** calcula qué porcentaje del deslizador está recorrido y lo escribe en la variable CSS `--pct` (para que se pinte la parte izquierda).
- **`buildRow` / `renderSelected`:** crean una fila por acorde (nombre, deslizador, valor, quitar) y **reutilizan las existentes**: las que ya no están se eliminan, las nuevas se crean, se **reordenan** si hace falta, y si un ejemplo cambió una intensidad se actualiza el deslizador. También actualizan el contador `n / 8` (con la clase `full` al llegar al máximo).
- **`changed()`:** cualquier cambio actualiza botones, filas y ejemplos, y programa una predicción.

### Los ejemplos
- **`presetEntries`:** toma los acordes de un ejemplo que existan en el vocabulario (máximo 8).
- **`updatePresets`:** marca (`aria-current`) el ejemplo cuyo contenido coincide **exactamente** con lo que hay elegido, para que se vea cuál está activo.
- **`applyPreset(label)`:** reemplaza la selección por ese ejemplo y lo anuncia ("Ejemplo Floral dulce cargado").

### Predecir
```javascript
function schedulePredict() { clearTimeout(state.timer); state.timer = setTimeout(predict, 180); }
```
**"Debounce" (retardo antiparpadeo):** cada cambio cancela el temporizador anterior y arranca uno de 180 ms; así, al mover un deslizador **no se hace un pedido por cada píxel**, sino uno cuando te frenás.

```javascript
async function predict() {
  if (!state.selected.size) { ++state.seq; ...ocultar resultado...; return; }
  const seq = ++state.seq;
  ... POST /api/predict ...
  if (seq !== state.seq) return;   // llegó tarde: se descarta
  renderResult(data);
  ... finally: quitar aria-busy ...
}
```
- Si no hay acordes, oculta el resultado y **también incrementa `seq`**, para que cualquier respuesta que estuviera en camino **se descarte** (no debe aparecer un resultado de acordes que ya no están).
- **`seq`** es un número de secuencia por pedido: si una respuesta vieja llega después de lanzar una nueva, se ignora.
- Mientras espera, marca la tarjeta con `aria-busy` (para lectores de pantalla); lo quita al terminar (`finally` se ejecuta siempre, con éxito o con error).
- Los errores se muestran en la franja roja, **solo si el pedido es el más reciente**.

### Mostrar el resultado
- **`neighbourZone(index, zone)`:** si el índice está a menos de 0,04 de un límite (0,33 o 0,67), devuelve **cuál es la zona vecina**. Con eso la página escribe: *"Está cerca del límite con la zona unisex: un pequeño cambio de intensidad podría cambiar la lectura."* Es una forma honesta de decir que **los límites son una convención** y que un resultado pegado al borde es poco firme.
- **`buildResultDom()`:** crea **una sola vez** los elementos de la lectura "femenino vs. masculino" y de las tres barras de probabilidad.
- **`renderResult(data)`**, en orden:
  1. **Espectro:** escribe `data-zone` en el resultado y el espectro (de ahí sale el color), el veredicto, el número del índice, mueve el marcador (`left = índice × 100 %`), actualiza la descripción accesible y la frase (con el aviso de borde si corresponde). Solo **anuncia por voz** cuando **cambia la zona** (para no repetir lo mismo en cada movimiento).
  2. **Femenino vs. masculino:** actualiza los dos porcentajes y los anchos de la barra de dos tramos.
  3. **Probabilidades por etiqueta:** actualiza las tres barras y el *lift* (`×0,5`).
  4. **Influencias:** dibuja hasta 8 filas. Para cada una calcula los puntos (índice × 100, con signo `+` o `−`), arma una descripción accesible ("woody: empuja hacia masculino, +6 pts") y fija el ancho de la barra **proporcional al mayor efecto** (`maxAbs`): el acorde de mayor influencia ocupa la mitad de la pista y los demás, una proporción.
  5. **Barra flotante:** actualiza su veredicto, índice, color y marcador.

### La barra flotante (celular)
- **`updateMinibar()`:** se muestra si **hay resultado y la tarjeta del resultado no está a la vista**.
- **`initMinibar()`:** usa un **`IntersectionObserver`** (una herramienta del navegador que avisa **cuándo un elemento entra o sale de la pantalla**) para saber si la tarjeta del resultado se ve (al menos 20 %). Al tocar la barra, la página **vuelve al resultado** con scroll suave (o directo, si el usuario pidió menos movimiento).

### La pestaña del modelo (`renderModel`)
Recibe lo que devolvió `/api/model/info` y **rellena** los cuatro indicadores (ahora cada uno con una **descripción corta** debajo, por ejemplo "Qué tan bien ordena los perfumes de femenino a masculino (1 = orden perfecto)"), la tabla A → B por umbral de votos, el estudio de pesos (resaltando la fila `pesos sqrt`), el texto del sesgo de la etiqueta (porcentajes leídos del reporte), el experimento de notas y las tablas del clasificador. Los encabezados de tabla llevan `scope="col"` (accesibilidad). Si un reporte no existe, esa parte se omite. **Nada está escrito a mano**: todo sale de la API.

### Los controles y el arranque (`initControls`, `init`)
- **`initControls`:** conecta el buscador (con un botón para borrarlo y la tecla `Esc`), el botón "Limpiar todo" (que devuelve el foco al buscador y lo anuncia), el cierre del aviso, los botones de ejemplos (cada uno muestra los tres primeros acordes) y "Probar un ejemplo".
- **`init`:** al abrir la página: coloca los íconos (recorre los elementos con `data-icon` y les inserta el SVG), inicia tema, pestañas, controles y barra flotante, muestra los esqueletos, pide la **lista de acordes** (y crea los botones) y después la **información del modelo**. Si falla el primer pedido (servidor apagado), muestra en el panel de acordes "No se pudieron cargar los acordes" y la franja roja. Un mensaje como **"Failed to fetch"** significa que el navegador no pudo conectarse al servidor (por ejemplo, porque no estaba corriendo).

### Accesibilidad: resumen de lo que hace la interfaz
Es una parte del diseño que vale la pena conocer, porque no se ve pero importa:
- **Teclado:** todo se puede usar sin mouse; hay enlace para saltar al contenido, contorno de foco visible y flechas para las pestañas.
- **Lectores de pantalla:** etiquetas (`aria-label`), regiones que anuncian cambios (`aria-live`) y descripciones de cada barra y del espectro.
- **Preferencias del usuario:** tema claro/oscuro del sistema, y menos animaciones si lo pidió.
- **Contraste:** colores de texto distintos de los de relleno, para que se lea bien en ambos temas.

---

# Parte 8: Los tests y los archivos de la raíz

## 8.1 Los tests: por qué existen y cómo leerlos

Un **test** es un programita que ejecuta una parte del código con una entrada conocida y verifica que la salida sea la esperada. Si alguien rompe algo sin querer, el test **falla y avisa**. Se corren con:

```bash
python -m pytest tests -q
```
(`-q` = "quiet": muestra poco). Hoy hay **40 tests** y todos pasan. Un test típico usa `assert` ("afirmá que…"): `assert resultado == esperado`. Si la afirmación es falsa, el test falla.

### `tests/conftest.py`: el ayudante de todos los tests

```python
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
VOCAB = ["aromatic", "floral", "sweet", "woody", "fresh spicy", "powdery"]
```
Agrega la raíz del proyecto para poder importar `perfume_gender` y define un **vocabulario mini de 6 acordes**.

```python
@pytest.fixture(scope="session")
def tiny_predictor() -> Predictor:
    rng = np.random.default_rng(0)
    X = rng.random((400, len(VOCAB))).astype("float32")
    masc = (X[:, 0] + X[:, 3] + X[:, 4]) - (X[:, 1] + X[:, 2] + X[:, 5])
    index = np.clip(0.5 + masc / 4, 0, 1)
    y = np.where(masc > 0.8, "male", np.where(masc < -0.8, "female", "unisex"))
    classifier = LogisticRegression(max_iter=500).fit(X, y)
    index_model = LinearRegression().fit(X, index)
    metadata = {...}
    return Predictor(classifier=classifier, index_model=index_model, vocab=VOCAB, metadata=metadata)
```
**La "fixture" `tiny_predictor`.** Una *fixture* es un **preparativo reutilizable** que pytest entrega a los tests que lo piden. Esta arma un **predictor de juguete** con datos **inventados**:
- 400 perfumes aleatorios de 6 acordes.
- Se define a propósito que `aromatic`, `woody` y `fresh spicy` empujan hacia **masculino**, y `floral`, `sweet` y `powdery` hacia **femenino**.
- Se entrenan dos modelos muy simples (regresión logística y regresión lineal).

**Por qué se hace así:** los tests **no dependen de los modelos reales** (que pueden cambiar al reentrenar) y corren en una fracción de segundo. `scope="session"` = se construye una sola vez para todos los tests. `default_rng(0)` = semilla fija.

### `tests/test_parsing_features.py` (9 tests)
Verifican el **parseo y la vectorización**:
| Test | Qué comprueba |
|---|---|
| `test_parse_basic` | `"woody:100\|sweet:65"` → `{"woody": 100.0, "sweet": 65.0}` |
| `test_parse_accord_names_with_spaces_and_case` | Que mayúsculas y espacios sobrantes se normalicen |
| `test_parse_merges_powder_alias` | Que `powder` y `powdery` se unifiquen (y se quede el mayor valor) |
| `test_parse_ignores_garbage_and_nulls` | Que `None`, vacíos, pedazos sin `:` o con valores no numéricos no rompan nada |
| `test_normalize_accord` | `"  Powder "` → `"powdery"` |
| `test_build_vocab_min_count` | Que el vocabulario filtre por cantidad mínima de apariciones |
| `test_vectorize_scales_to_unit_range_and_ignores_unknown` | Que 100 → 1,0, 50 → 0,5 y un acorde desconocido se ignore |
| `test_to_matrix_shape` | Que la matriz tenga la forma correcta |
| `test_rescale_to_max` | Que el acorde más fuerte pase a valer 100 |

### `tests/test_perception.py` (8 tests)
Verifican el **índice**:
- Solo votos masculinos → 1,0; solo femeninos → 0,0; solo unisex → 0,5.
- 10 masculinos + 10 unisex → 0,75 (promedio ponderado).
- Sin votos → resultado vacío (NaN), no un error de división por cero.
- El total de votos suma bien.
- Los **límites de las zonas** (`0,33` ya es unisex; `0,67` todavía es unisex; `0,68` es masculino).
- `vote_weight`: 1 → 1; 4 → 2; 100 → 10; 10.000 → 10 (el tope).

### `tests/test_predictor.py` (6 tests)
- `male_vs_female(0,03; 0,07)` → 30 % / 70 %; y con ambas en 0 → 50/50.
- `lift`: 0,30 sobre una base de 0,15 → 2,0; si falta la base → 0.
- El predictor rechaza una entrada vacía.
- Une alias y mayúsculas (`"Powder": 30` y `"powdery": 60` → un solo `powdery` reescalado a 100).

### `tests/test_api.py` (10 tests)
Prueban el **servidor completo** sin abrir un navegador.

```python
@pytest.fixture()
def client(monkeypatch, tiny_predictor):
    monkeypatch.setattr(Predictor, "load", classmethod(lambda cls, *a, **k: tiny_predictor))
    from app.backend.main import app
    with TestClient(app) as c:
        yield c
```
- **`monkeypatch`:** una herramienta de pytest para **reemplazar temporalmente** una pieza del código. Acá se le dice a `Predictor.load` "no cargues los modelos reales: devolvé el predictor de juguete". Así el servidor arranca con los modelos falsos.
- **`TestClient`** simula un navegador que hace pedidos al servidor, sin red.
- `yield` entrega el cliente al test y, cuando termina, se limpia todo.

Tests: el chequeo de salud devuelve `ok`; la lista de acordes incluye `woody` y el máximo 8; la respuesta tiene exactamente los 7 campos esperados y valores coherentes (índice entre 0 y 1, probabilidades que suman 1); **un perfil masculino queda del lado masculino y uno femenino del lado femenino**; las **influencias tienen el signo correcto**; la **entrada se reescala**; un acorde desconocido da **422** con un mensaje que lo nombra; entradas inválidas (lista vacía, intensidad 0, 9 acordes) dan 422; `/api/model/info` incluye los metadatos; y la página principal se sirve (contiene "ScentAI").

### `tests/test_readme_consistency.py` (7 tests)
**Una idea poco común y muy útil:** verificar que **las cifras escritas en el README coinciden con los reportes**. Si alguien reentrena y los números cambian, pero se olvida de actualizar el README, este test **falla**.

```python
def dec(valor, d):  # 0.6125 -> '0,613'
    q = Decimal(str(valor)).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP)
    return f"{q:f}".replace(".", ",")
def miles(n):       # 98364 -> '98.364'
    return f"{int(n):,}".replace(",", ".")
```
Dos funciones que escriben los números **al estilo del README** (coma decimal, punto de miles, redondeo "para arriba" en la mitad). `debe_aparecer(...)` verifica que cada texto esté en el README. Seis tests revisan el README y cubren: limpieza y partición, estadísticas de votos y sesgo de la etiqueta, comparación índice vs. clasificador (incluyendo que los cuatro criterios de éxito sean verdaderos y que el caso de prueba sea "masculino"), métricas del clasificador, estudio de pesos y experimentos/robustez. El séptimo test hace lo mismo con **esta guía**: verifica que las cifras clave que cita (tamaños de train y test, porcentajes de la etiqueta "unisex", error medio, exactitud…) sigan coincidiendo con los reportes. Si falta un reporte, el test se **saltea** (`pytest.skip`) con un aviso.

---

## 8.2 Los archivos de la raíz

### `requirements-app.txt` y `requirements.txt`
```text
numpy==2.5.2
scipy==1.18.1
scikit-learn==1.9.0
joblib==1.6.0
fastapi==0.141.1
uvicorn==0.53.0
pydantic==2.13.5
```
`requirements-app.txt` es el **mínimo para usar la app**. `requirements.txt` empieza con `-r requirements-app.txt` (= "incluí todo lo de ese archivo") y agrega `pandas`, `matplotlib`, `seaborn` (para el pipeline) y `pytest`, `httpx` (para los tests). Las versiones están **fijadas** con `==`.

### `run.bat` (Windows)
```bat
@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
    echo Creando entorno virtual e instalando dependencias...
    python -m venv .venv || goto :error
    .venv\Scripts\python.exe -m pip install -r requirements-app.txt || goto :error
)
echo Abri http://localhost:8000 en el navegador  (Ctrl+C para detener)
.venv\Scripts\python.exe -m uvicorn app.backend.main:app --host 127.0.0.1 --port 8000
goto :eof
:error
echo No se pudo preparar el entorno. ...
exit /b 1
```
Un **script de Windows** (`.bat`) con comandos de la consola:
- `@echo off`: no mostrar cada comando.
- `cd /d "%~dp0"`: ir a la carpeta donde está el archivo (`%~dp0` = "la carpeta de este script"), para que funcione sin importar desde dónde lo abras.
- `if not exist ...`: **si no existe el entorno virtual**, lo crea (`python -m venv .venv`) e instala las dependencias. `|| goto :error` significa "si el comando anterior falla, saltá a `:error`".
- `uvicorn app.backend.main:app`: **enciende el servidor**. Se lee: "del módulo `app.backend.main`, la variable `app`". `--host 127.0.0.1` = solo accesible desde tu computadora; `--port 8000` = el puerto.
- `:error` / `exit /b 1`: el bloque que se ejecuta si algo falló: muestra un mensaje y termina con código de error.

### `run.sh` (Linux / Mac)
Lo mismo en el lenguaje de la consola de Linux/Mac (**bash**): `set -e` = "frená si algún comando falla"; `cd "$(dirname "$0")"` = "andá a la carpeta del script"; `[ ! -x .venv/bin/python ]` = "si no existe el Python del entorno"; `exec ...` = "reemplazá este proceso por el servidor".

### `Dockerfile`
```dockerfile
FROM python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements-app.txt .
RUN pip install --no-cache-dir -r requirements-app.txt
COPY perfume_gender ./perfume_gender
COPY app ./app
COPY models ./models
COPY reports ./reports
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
Una receta, **instrucción por instrucción**:
| Línea | Qué hace |
|---|---|
| `FROM python:3.14-slim` | Parte de una imagen oficial que ya trae Python 3.14 en su versión "slim" (liviana). |
| `ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1` | Dos ajustes: no generar archivos temporales de Python, y mostrar los mensajes del servidor en el momento. |
| `WORKDIR /app` | La carpeta de trabajo dentro de la imagen. |
| `COPY requirements-app.txt .` y `RUN pip install ...` | Copia la lista de librerías y las instala. Se hace **antes** de copiar el código: si solo cambia el código, Docker reutiliza esta capa y el armado es más rápido (las imágenes se arman en **capas** y se guardan en caché). `--no-cache-dir` evita guardar archivos de descarga (imagen más chica). |
| `COPY perfume_gender ...` etc. | Copia el código, los modelos y los reportes. |
| `EXPOSE 8000` | Documenta que el servidor usa el puerto 8000. |
| `CMD [...]` | El comando que se ejecuta al **iniciar el contenedor**: enciende el servidor. Usa `--host 0.0.0.0` porque **dentro del contenedor** el servidor tiene que aceptar conexiones de afuera (si escuchara solo en `127.0.0.1`, no podrías entrar desde tu navegador). |

### `.dockerignore`
Lista de lo que **no se copia** a la imagen: `.git`, `.venv`, `data` (el CSV de 127 MB), `pipeline`, `experiments`, `tests`, `docs`, `tasks`, los `*.md`, los scripts `run.*` y `requirements.txt`. Resultado: la imagen contiene solo lo necesario para **usar** la app (`app`, `models`, `perfume_gender`, `reports`, `requirements-app.txt`).

### `.gitignore`
Lista de lo que Git **no sube**:
- `data/raw/*` (menos `README.md`) y `data/processed/`: los datos pesados.
- `__pycache__/`, `*.py[cod]`, `.pytest_cache/`, `.venv/`: archivos temporales y entornos.
- `docs/spec-*.md` y `tasks/`: documentos de trabajo.
- `.claude/`, `.vscode/`, `.idea/`, `.DS_Store`, `Thumbs.db`: configuración local y basura del sistema.

### `.gitattributes`
```text
* text=auto eol=lf
*.bat text eol=crlf
*.joblib binary
*.png binary
*.gz binary
```
Reglas de cómo Git trata los archivos: los de texto se guardan con saltos de línea tipo **LF** (estándar de Linux/Mac; Windows usa CRLF, y esa diferencia genera avisos molestos); los `.bat` mantienen CRLF (Windows lo necesita); y los `.joblib`, `.png`, `.gz` son **binarios** (Git no debe intentar interpretarlos como texto).

### `.github/workflows/tests.yml` (el "robot" de verificación)
```yaml
name: tests
on:
  push:
    branches: [main]
  pull_request:
jobs:
  pytest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.14", cache: pip, cache-dependency-path: requirements*.txt }
      - name: Instalar dependencias
        run: python -m pip install -r requirements.txt
      - name: Correr tests
        run: python -m pytest tests -q
```
**YAML** es un formato de configuración basado en sangrías. Dice: "**cuando** alguien suba cambios a `main` o abra un *pull request*, **en una máquina Ubuntu limpia** de GitHub: (1) descargá el código (`checkout`), (2) instalá Python 3.14 (con caché de librerías), (3) instalá las dependencias y (4) corré los tests". Si algo falla, GitHub marca el cambio en rojo.

### `data/raw/README.md`
Instrucciones de **dónde conseguir** `perfumes.csv` (Kaggle), dónde guardarlo y qué columnas usa el proyecto. Es el único archivo de `data/raw/` que se versiona.

### `README.md`, `MODEL_CARD.md` y esta guía
- **`README.md`**: la presentación técnica en 4 secciones (dataset, ETL, entrenamiento, uso).
- **`MODEL_CARD.md`**: una "ficha" breve del modelo: qué es, uso previsto, datos, resultados, **limitaciones y sesgos**. Es una buena práctica de transparencia en Machine Learning.
- **`GUIA_EN_CRIOLLO.md`**: este documento.

---

## 8.3 La carpeta `models/`

| Archivo | Qué es |
|---|---|
| `model.joblib` | El **clasificador** entrenado (~1 MB). |
| `index_model.joblib` | El **regresor del índice** entrenado (~0,5 MB). |
| `accords_vocab.json` | La lista de los **72 acordes** válidos, en orden alfabético. **El orden es esencial**: la posición de cada acorde en el vector depende de él. |
| `metadata.json` | Información sobre los modelos, dividida en tres secciones. |

La estructura de `metadata.json`:
```json
{
  "classifier":  { "model_name": "...", "classes": [...], "n_features": 72, "n_train": 98364, "metrics_test": {...}, "per_class_test": {...}, "sklearn_version": "...", ... },
  "index_model": { "model_class": "HistGradientBoostingRegressor", "n_train": 80465, "zone_limits": [0.33, 0.67], "metrics_test_N10": {...}, ... },
  "class_priors": { "female": 0.3329, "male": 0.155, "unisex": 0.5121 }
}
```
- `classifier` e `index_model`: datos de cada modelo (qué es, con cuántos perfumes se entrenó, sus métricas, la versión de scikit-learn y la fecha).
- `class_priors`: las **frecuencias base** de cada clase en el train (la API las usa para calcular el *lift*).

## 8.4 La carpeta `reports/`: los resultados de cada paso

Cada paso del pipeline deja un archivo JSON con sus resultados. **Todas las cifras del README y de la página salen de acá.**

| Archivo | Lo genera | Contenido |
|---|---|---|
| `eda.json` | `01_eda.py` | Estadísticas exploratorias: acordes por perfume, votos, intensidades, acordes más raros, y el análisis etiqueta vs. percepción (14,1 / 24,9 / 61,0 %). |
| `etl.json` | `02_etl.py` | Cuántas filas se descartaron en cada paso, duplicados, vocabulario, tamaños de train/test, cuántos perfumes tienen votos. |
| `experiments.json` | `03_experiments.py` | Resultados de los tres experimentos (notas, equilibrar, filtrar votos). |
| `metrics.json` | `04_train.py` | Validación cruzada de cada candidato, ajuste de hiperparámetros, ganador y resultado en test. |
| `index_metrics.json` | `05_train_index.py` | Validación cruzada del regresor, comparación A vs. B, criterios de éxito, caso de prueba. |
| `evaluation.json` | `06_evaluate.py` | Error de calibración (ECE), acordes más importantes, rendimiento por votos, robustez por marca. |
| `vote_weights.json` | `experiments/vote_weights.py` | Estudio de filtros y pesos por votos. |

(Los archivos con **tiempos de ejecución** pueden variar un poco entre corridas; todo lo demás es idéntico.)

## 8.5 La carpeta `docs/figures/`: los gráficos

| Archivo | Qué muestra |
|---|---|
| `eda_01_clases.png` | Cuántos perfumes hay de cada género, antes y después de limpiar. |
| `eda_02_acordes_por_perfume.png` | Cantidad de acordes por perfume y su relación con los votos. |
| `eda_03_votos.png` | La distribución de votos (cola larga). |
| `eda_04_intensidades.png` | Distribución de las intensidades de los acordes. |
| `eda_05_frecuencia_acordes.png` | Los 30 acordes más frecuentes. |
| `eda_06_acordes_por_genero.png` | Qué acordes distinguen más a femeninos de masculinos. |
| `eda_07_correlacion.png` | Qué acordes suelen aparecer juntos. |
| `eda_08_etiqueta_vs_percepcion.png` | **La figura clave:** cómo se distribuye el índice percibido dentro de cada etiqueta. |
| `model_comparacion.png` | F1 macro de cada modelo candidato. |
| `model_experimentos.png` | Notas vs. acordes y cómo tratar el desbalance. |
| `model_confusion.png` | La matriz de confusión del clasificador. |
| `model_calibracion.png` | Calibración de las probabilidades. |
| `model_importancia.png` | Los acordes más importantes para el clasificador. |
| `index_calibracion.png` | Calibración del índice: A (clasificador) vs. B (modelo de índice). |
| `index_metricas.png` | Error y Spearman de A vs. B según el mínimo de votos. |
| `index_zonas.png` | Matriz de confusión de las **zonas** del índice. |
| `demo_predictor.jpg`, `demo_resultado.jpg` | Capturas de la página funcionando. |

---

# Parte 9: Cómo leer los resultados (cada número explicado)

Esta parte toma los resultados reales del proyecto y te enseña a **leerlos**. Para cada cifra: qué mide, de dónde sale y qué conclusión permite sacar.

## 9.1 Los datos: de 131.930 a 122.955 perfumes

| Paso | Filas | Qué pasó |
|---|---|---|
| Dataset crudo | **131.930** | Todo lo que trae el CSV. |
| Sin acordes | −2.769 → 129.161 | Perfumes sin información de acordes: se descartan. |
| Duplicados | −6.206 → **122.955** | Perfumes con un perfil de acordes idéntico a otro: queda uno. |
| Train | **98.364** | El 80 %: con estos se entrena. |
| Test | **24.591** | El 20 %: examen final. |
| Con votos de percepción | **100.541** | Los que tienen índice (80.465 en train, el **81,8 %** del train). |

**Cómo se reparten los géneros** (tras limpiar): unisex **51,2 %** (62.962), femenino **33,3 %** (40.936), masculino **15,5 %** (19.057).

## 9.2 La etiqueta "unisex" no es lo que parece

De los perfumes etiquetados "unisex" con **al menos 30 votos de percepción** (13.247 perfumes), según el índice:

| Zona real (según los votos de la gente) | Porcentaje |
|---|---|
| Masculina | **14,1 %** |
| Intermedia (realmente unisex) | **61,0 %** |
| Femenina | **24,9 %** |

**Cómo leerlo:** la mayoría (61 %) sí es intermedia, pero casi **4 de cada 10** se inclinan claramente hacia un extremo. Una etiqueta que mezcla eso es difícil de predecir, y por eso un clasificador de la etiqueta se refugia en "unisex". Es el argumento central para tener un modelo de índice.

## 9.3 El clasificador de la etiqueta (modelo complementario)

### Comparación de modelos (validación cruzada de 5 pedazos, F1 macro)
| Modelo | F1 macro (promedio ± desvío) | Exactitud |
|---|---|---|
| Baseline (siempre unisex) | 0,226 | 0,512 |
| Regresión logística | 0,572 ± 0,002 | 0,634 |
| Random Forest | 0,572 ± 0,003 | 0,643 |
| SVM (submuestra de 20.000) | 0,559 ± 0,006 | 0,633 |
| Gradient Boosting | 0,598 ± 0,002 | 0,646 |
| MLP (red neuronal) | 0,600 ± 0,004 | 0,646 |
| **Gradient Boosting ajustado** | **0,600 ± 0,002** | **0,647** |

**Cómo leerlo:** el baseline tiene un F1 macro de solo 0,226 aunque su exactitud sea 0,512, porque nunca acierta masculino ni femenino: con F1 macro "queda en evidencia". Los modelos reales rondan 0,57–0,60: la diferencia entre ellos es **chica**. Eso indica que el techo lo pone la información (solo acordes).

### Resultado final en el test
- **Exactitud: 64,7 %** (el baseline acierta 51,2 %).
- **F1 macro: 0,599**.

| Clase | Precisión | Recall | F1 | Perfumes |
|---|---|---|---|---|
| Femenino | 65,5 % | 66,5 % | 0,660 | 8.187 |
| Masculino | 58,5 % | **36,6 %** | 0,451 | 3.811 |
| Unisex | 65,3 % | 72,0 % | 0,685 | 12.593 |

**Cómo leerlo:** al modelo le va parecido en femenino y unisex, y **mucho peor en masculino**: de cada 100 perfumes realmente masculinos, solo encuentra ~37. Los otros ~63 los manda casi todos a "unisex" (2.232 de los 3.811). Cuando **dice** "masculino", acierta el 58,5 %.

**La matriz de confusión en porcentajes por fila:**
| Real ↓ / Predicho → | Femenino | Masculino | Unisex |
|---|---|---|---|
| Femenino | 67 % | **2 %** | 32 % |
| Masculino | **5 %** | 37 % | 59 % |
| Unisex | 21 % | 7 % | 72 % |

Las dos celdas resaltadas son las más importantes para el usuario: el modelo **casi nunca confunde femenino con masculino** (2 % y 5 %). Sus errores van hacia la "zona gris" (unisex). Por eso la lectura "femenino vs. masculino" es muy confiable.

### Otros análisis del clasificador
- **Calibración:** el error de calibración (ECE) es 0,004 / 0,004 / 0,010. Las probabilidades son confiables.
- **Robustez por marca:** F1 macro **0,598** con marcas nunca vistas (vs. 0,599 con partición al azar).
- **Según la cantidad de votos de rating del perfume** (F1 macro): 0–4 votos **0,570** · 5–19 **0,587** · 20–99 **0,624** · 100+ **0,616**. Con perfumes poco votados le va peor, algo esperable.
- **Acordes más importantes:** `floral`, `aromatic`, `white floral`, `citrus`, `rose`, `lavender`, `sweet`, `oud`.

### Los tres experimentos de datos
| Pregunta | Resultado | Decisión |
|---|---|---|
| ¿Ayudan las notas? | Solo acordes 0,598 · Acordes + notas **0,670** · Solo notas 0,667 | Las notas aportan ~7 puntos, pero **no se usan** (el perfumista aún no las tiene definidas, a validar). |
| ¿Conviene equilibrar? | Sin pesos **0,598** · `class_weight` 0,581 · Submuestreo 0,577 | **No equilibrar**. |
| ¿Conviene filtrar por votos de rating? | Mínimo 0: 0,598 · 5: 0,602 · 20: 0,601 · 50: 0,596 | **No filtrar** (no mejora y se pierde dato). |

## 9.4 El modelo de índice (modelo principal)

### Cómo se entrenó
- Con **80.465** perfumes de train que tienen al menos 1 voto de percepción.
- Con pesos `√min(votos, 100)`.
- Validación cruzada de 5 pedazos: **error medio 0,126 ± 0,001** y **Spearman 0,809 ± 0,004**.

### La comparación A contra B en el test
**A** = el clasificador convertido a índice. **B** = el modelo de índice.

| Votos de percepción mínimos | Perfumes de test | Error A → B | Spearman A → B | F1 por zonas A → B |
|---|---|---|---|---|
| **≥ 10** (referencia) | 9.618 | 0,157 → **0,126** (−20,1 %) | 0,800 → **0,810** | 0,613 → **0,676** |
| ≥ 30 | 5.430 | 0,156 → 0,122 (−21,9 %) | 0,811 → 0,824 | 0,616 → 0,689 |
| ≥ 100 | 2.370 | 0,160 → 0,125 (−22,2 %) | 0,821 → 0,832 | 0,610 → 0,684 |

**Cómo leerlo, columna por columna:**
- **Votos mínimos:** la evaluación se hace solo con perfumes con suficientes votos para que el índice real sea confiable. Se repite con tres exigencias para verificar que el resultado **no depende del umbral elegido**.
- **Error A → B:** el error medio baja alrededor de un **20 %** en los tres casos. Es la mejora principal.
- **Spearman A → B:** sube apenas (+0,01). Significa que **el orden entre perfumes casi no mejora**: los acordes dan la misma información. Lo que mejora es **dónde se ubica** cada perfume en la escala.
- **F1 por zonas A → B:** el modelo B acierta mejor la zona (0,676 vs. 0,613).

### ¿Por qué mejora el error pero no tanto el orden?
La **curva de calibración** (`index_calibracion.png`) lo explica: A, al convertir probabilidades en un índice esperado, queda **comprimido hacia el centro** (rara vez llega a valores extremos como 0,1 o 0,9), mientras que B sigue la **diagonal ideal**. Ordenan parecido, pero B **estima la escala mejor**.

### Cuidado con una trampa de la comparación
B se evalúa contra el índice, que es **con lo que fue entrenado** (A no). Eso lo favorece en esta comparación. Para predecir la **etiqueta** de la marca, el clasificador sigue siendo el indicado. Por eso el README lo aclara.

### La matriz de zonas (`index_zonas.png`)
| Zona real ↓ / Zona predicha → | Femenino | Unisex | Masculino |
|---|---|---|---|
| **Femenino** (4.153) | **80 %** (3.338) | 19 % (791) | 1 % (24) |
| **Unisex** (3.275) | 17 % (570) | **67 %** (2.191) | 16 % (514) |
| **Masculino** (2.190) | 3 % (58) | **44 %** (964) | 53 % (1.168) |

**Cómo leerlo:** el modelo acierta el 80 % de los femeninos, 67 % de los intermedios y **53 % de los masculinos**. Casi nunca confunde los extremos entre sí (1 % y 3 %). El punto débil, que el README y la ficha del modelo reconocen: el **44 % de los perfumes percibidos como masculinos** termina en la zona intermedia, porque los acordes solos no los distinguen del todo.

### El caso de prueba (la composición del usuario)
`alcohol 9, cannabis 15, chocolate 16, woody 84, aldehydic 5, leather 75, smoky 61`:

| | Resultado |
|---|---|
| **Clasificador** | femenino 3 % · masculino 7 % · **unisex 90 %** → índice esperado **0,479** (en el medio) |
| **Modelo de índice** | **0,717 → zona masculina** |
| Lectura femenino vs. masculino | 30 % / **70 %** |
| Lift (comparado con lo habitual) | femenino ×0,1 · masculino ×0,5 · unisex ×1,8 |

**Cómo leerlo:** el clasificador dice "unisex 90 %" porque es su respuesta "segura" (lift 1,8: "casi el doble de lo habitual"), pero eso **no significa que el perfume sea unisex**. El índice lo ubica del lado masculino. La lectura femenino vs. masculino confirma: entre los dos extremos, 70 % masculino.

## 9.5 La respuesta de la API, campo por campo

Para `woody 100, leather 75, smoky 60`:
```json
{
  "index": 0.6836,
  "zone": "male",
  "male_vs_female": {"female": 0.1416, "male": 0.8584},
  "class_probabilities": {"female": 0.0295, "male": 0.1786, "unisex": 0.7919},
  "lift": {"female": 0.089, "male": 1.152, "unisex": 1.546},
  "accords_used": {"woody": 100.0, "leather": 75.0, "smoky": 60.0},
  "influences": [
    {"accord": "woody",   "index_effect": 0.0663, "pushes_toward": "male"},
    {"accord": "leather", "index_effect": 0.0385, "pushes_toward": "male"},
    {"accord": "smoky",   "index_effect": 0.0067, "pushes_toward": "male"}
  ]
}
```
| Campo | Significado en este ejemplo |
|---|---|
| `index` | **0,6836**: está del lado masculino, justo arriba del límite de 0,67. |
| `zone` | `"male"`: como 0,6836 > 0,67, la zona es masculina. |
| `male_vs_female` | Si ignoramos "unisex": 85,8 % masculino, 14,2 % femenino. |
| `class_probabilities` | El clasificador: 3 % fem., 18 % masc., 79 % unisex. |
| `lift` | Masculino ×1,15 (un poco **más** de lo habitual: 17,9 % vs. 15,5 % de base); unisex ×1,55; femenino ×0,09 (muy improbable). |
| `accords_used` | Los acordes tal como se usaron, **ya reescalados** (el más fuerte vale 100). |
| `influences` | Quitar `woody` baja el índice 0,066 (= **6,6 puntos**); `leather`, 3,9; `smoky`, 0,7. Los tres empujan hacia masculino. |

> **Sobre el límite de zonas:** 0,6836 está muy cerca de 0,67. Un cambio pequeño en las intensidades podría pasarlo a "unisex". **Los límites son una convención**; por eso la interfaz muestra el número y la barra, no solo la zona.

## 9.6 El estudio de los votos (por qué ponderar)

### ¿Es alta la media de votos?
| Votos | Media | Mediana | Percentil 75 | Percentil 90 |
|---|---|---|---|---|
| Rating (`vote_count`) | 172,5 | 13 | 69 | 283 |
| Percepción de género | 64,5 | **5** | 24 | 98 |

La media **engaña** por unos pocos perfumes con miles de votos; el perfume típico tiene 5 votos de percepción.

### ¿Filtrar por votos mínimos?
| Mínimo para entrenar | Filas | Error | Spearman |
|---|---|---|---|
| 1 (todo) | 64.372 | 0,1237 | 0,824 |
| 5 | 41.686 | 0,1221 | 0,827 |
| 10 | 31.363 | 0,1226 | 0,827 |
| 30 | 17.699 | 0,1217 | 0,827 |
| 100 | 7.804 | 0,1247 | 0,817 |

(Esas "filas" son el 80 % interno de la partición de validación, no el train completo.) **Lectura:** filtrar **no mejora**; con 100 votos mínimos empeora porque se pierden demasiados datos.

### ¿Ponderar? (promedio de 3 particiones)
| Esquema | Error | Spearman |
|---|---|---|
| Sin filtro ni pesos | 0,1233 | 0,825 |
| Filtro mínimo 5 | 0,1223 | 0,827 |
| Pesos `min(votos, 30)` | 0,1215 | 0,828 |
| **Pesos `√votos`, tope 100 (elegido)** | **0,1215** | **0,829** |

**Lectura:** ponderar mejora el error en ≈ 1,5 %. Es una mejora **chica**, pero usa todas las filas con índice y no obliga a elegir un umbral arbitrario.

## 9.7 La pestaña "El modelo" de la página

Cada tabla de esa pestaña sale de un reporte:

| Bloque de la pestaña | Reporte de donde sale |
|---|---|
| Los 4 indicadores de arriba (error, Spearman, F1 por zonas, "−20,1 %") | `index_metrics.json` |
| "Índice vs. clasificador por etiqueta" | `index_metrics.json` |
| "Cómo se entrenó con los votos" | `vote_weights.json` |
| "Etiqueta de marca vs. percepción" + tabla de notas | `eda.json` + `experiments.json` |
| "Clasificador de la etiqueta" (validación cruzada, matriz, clases) | `metrics.json` |

---

# Parte 10: Preguntas frecuentes y guía práctica

## 10.1 Cómo hacer las cosas más comunes

| Quiero… | Comando |
|---|---|
| **Usar** la app (Windows) | Doble clic en `run.bat`, y abrir <http://localhost:8000> |
| **Usar** la app (Linux/Mac) | `./run.sh` |
| **Usar** la app con Docker | `docker build -t scentai .` y después `docker run --rm -p 8000:8000 scentai` |
| Detener la app | `Ctrl+C` en la terminal |
| Correr los tests | `python -m pytest tests -q` |
| Reentrenar todo | `python pipeline/run_all.py` (requiere `data/raw/perfumes.csv` y `pip install -r requirements.txt`) |
| Correr solo un paso | Por ejemplo `python pipeline/05_train_index.py` |
| Ver la documentación de la API | Abrir <http://localhost:8000/docs> con la app andando |
| Comprobar que el servidor está vivo | `curl http://localhost:8000/api/health` |

## 10.2 "Si quiero cambiar X, ¿qué toco?"

| Quiero cambiar… | Dónde | Qué hay que tener en cuenta |
|---|---|---|
| Los **límites de las zonas** (0,33 / 0,67) | `ZONE_LIMITS` en `perfume_gender/perception.py` **y** sus dos copias en la interfaz: `ZONE_LIMITS` en `app/frontend/app.js` y los separadores del espectro (`left: 33%` / `67%`) en `styles.css` | Hay que **reentrenar** (`python pipeline/run_all.py`), actualizar el test de zonas y el README. Los tres lugares tienen que coincidir. |
| El **máximo de acordes** | `MAX_ACCORDS` en `perfume_gender/config.py` | El modelo se entrenó con perfiles de hasta 8 acordes; subirlo a 12 no tiene respaldo en los datos. |
| El **peso de los votos** | `vote_weight` en `perception.py` | Reentrenar y volver a evaluar. |
| Los **hiperparámetros** del índice | `nuevo_regresor` en `pipeline/05_train_index.py` | Reentrenar; **no** ajustar mirando el test. |
| Los **colores** de la página | Variables al principio de `styles.css` (`--female`, `--male`, `--bg`…) | Hay **dos bloques**: el tema oscuro (`:root`) y el claro (`:root[data-theme="light"]`). Los colores de **texto** (`--female-t`…) deben mantener buen contraste con el fondo. |
| El **logo** | Archivos de `app/frontend/assets/` (`logo.svg`, `logo-mark.svg`) | El README también usa `logo.svg`. |
| Los **ejemplos rápidos** | `PRESETS` en `app/frontend/app.js` | Los acordes deben existir en el vocabulario (los que no, se ignoran). |
| El **puerto** | Los comandos `--port 8000` en `run.bat`/`run.sh`, o `-p 8080:8000` en Docker | |
| La **semilla** | `SEED` en `config.py` | Cambian ligeramente todos los resultados; el README quedaría desactualizado (el test de concordancia avisaría). |
| Usar un **dataset nuevo** | Reemplazar `data/raw/perfumes.csv` y correr `run_all.py` | Cambian todas las cifras; hay que actualizar el README (ver el test de concordancia). |
| **Agregar un acorde** | No se puede "a mano": el vocabulario sale de los datos (`02_etl.py`). | Si el acorde no aparece en al menos 50 perfumes, no entra. |

## 10.3 Errores comunes y qué significan

| Mensaje | Qué significa | Solución |
|---|---|---|
| **"No se pudo predecir: Failed to fetch"** (en la página) | El navegador no pudo conectarse al servidor: **no está corriendo** (se cerró la terminal, o se detuvo). | Volver a levantarlo (`run.bat`) y recargar la página con `Ctrl+F5`. |
| `ModuleNotFoundError: No module named 'perfume_gender'` | Python no encuentra el paquete: se ejecutó desde otra carpeta. | Correr siempre **desde la raíz del proyecto**. Los scripts de `pipeline/` ya traen su ayudante (`_bootstrap`). |
| `FileNotFoundError: ... perfumes.csv` | No está el dataset. | Descargarlo de Kaggle y guardarlo en `data/raw/perfumes.csv` (ver `data/raw/README.md`). |
| `FileNotFoundError: ... clean.csv.gz` | Falta el paso de limpieza. | Correr `python pipeline/02_etl.py`. |
| `address already in use` / `port is already allocated` | El puerto 8000 ya está ocupado (por ejemplo, otra copia del servidor). | Cerrar el otro servidor, o usar otro puerto. |
| `failed to connect to the docker API` / `Cannot connect to the Docker daemon` | Docker Desktop no está abierto. | Abrir Docker Desktop, esperar y reintentar. |
| Aviso de versiones de scikit-learn al cargar un modelo | El modelo se guardó con **otra versión** de scikit-learn. | Instalar la versión de `requirements-app.txt` (`pip install -r requirements-app.txt`). |
| `warning: CRLF will be replaced by LF` (al hacer `git add`) | Aviso de saltos de línea de Windows vs. Linux. | Es solo un aviso; el `.gitattributes` lo maneja. No afecta. |
| Test de concordancia del README falla | Los reportes cambiaron y el README tiene cifras viejas. | Actualizar las cifras del README con las de `reports/*.json`. |

## 10.4 Cómo leer un error de Python (traceback)
Cuando Python falla, muestra una pila de líneas ("traceback"). **Se lee de abajo hacia arriba**: la **última línea** dice el **tipo de error y el motivo** (por ejemplo `FileNotFoundError: Falta data/processed/clean.csv.gz`); las líneas de arriba muestran **en qué archivo y línea** ocurrió. En este proyecto, los mensajes de error están escritos para decir **qué hacer** ("ejecutá pipeline/02_etl.py").

## 10.5 Preguntas conceptuales frecuentes

**¿Por qué el test se usa una sola vez?**
Porque funciona como un examen final con preguntas que el modelo nunca vio. Si lo usaras para decidir (qué modelo, qué perillas) irías "afinando" para ese examen y el resultado sería **optimista**: ya no mediría cuánto sirve el modelo con datos realmente nuevos.

**¿Por qué usar F1 macro y no solo la exactitud?**
Porque la exactitud puede engañar con categorías desbalanceadas. Un modelo que siempre dice "unisex" acierta 51,2 % sin saber nada. El F1 macro le da el mismo peso a cada categoría y **castiga** que le vaya mal en las chicas (masculino).

**¿64,7 % de exactitud es mucho o poco?**
Es **moderado**: supera al baseline (51,2 %) por ~13 puntos. Lo valioso es el **tipo** de errores: casi nunca invierte femenino con masculino; se equivoca hacia "unisex". Por eso el proyecto se presenta como una **orientación**, no como un veredicto.

**¿Por qué dos modelos y no uno solo?**
El clasificador entiende la **etiqueta de la marca** (útil para probabilidades y para la lectura femenino vs. masculino). El de índice entiende la **percepción de la gente** (útil para ubicar en la escala). Responden preguntas distintas y se complementan.

**¿Qué es exactamente el "índice"?**
Un promedio ponderado de los votos de la gente: cada voto vale 0 (femenino), 0,25, 0,5 (unisex), 0,75 o 1 (masculino). Ejemplo: 10 votos "masculino" + 10 "unisex" = `(10×1 + 10×0,5)/20 = 0,75`.

**¿Por qué no se usan las notas?**
Porque se supone que el perfumista, al pedir la primera muestra, define **acordes**, no ingredientes exactos. Es una hipótesis de dominio a validar con un perfumista real. Las notas **sí** mejorarían el modelo (~7 puntos de F1), y quedó como mejora futura.

**¿Si corro todo de nuevo, dan los mismos resultados?**
Sí, gracias a la **semilla fija**. Se comprobó corriendo el pipeline completo dos veces: idéntico salvo los tiempos de ejecución.

**¿Los modelos son "sesgados"?**
Aprenden lo que hay en los datos: **cómo la gente percibe y las marcas etiquetan perfumes existentes**, incluyendo estereotipos de género del mercado. Además, quienes votan ven la etiqueta de la marca antes de votar. El modelo **no juzga** esas convenciones; las reproduce. Está dicho en el README y en `MODEL_CARD.md`.

**¿Sirve para decidir el género de mi perfume?**
No como único criterio. Es una **orientación estadística** previa a la muestra. El olfato y el criterio del perfumista siguen siendo lo que decide.

**¿Qué mejoraría el proyecto?**
Ideas anotadas: (1) un modelo alternativo que además use **notas** (+7 puntos de F1); (2) una función **"sugerir qué acorde agregar o quitar"** para mover el perfil hacia un extremo; (3) **traducir** los nombres de acordes al español; (4) evaluar el **dataset más reciente** de Kaggle; (5) **validar con perfumistas reales**.

---

# Glosario rápido (A–Z)

| Término | Definición corta |
|---|---|
| **Acorde** | Familia de olor que resume el carácter de un perfume (woody, sweet…). |
| **API** | El "menú" de pedidos que atiende un servidor. |
| **argmax** | "El que tiene el valor más alto": la clase con mayor probabilidad. |
| **Baseline** | Resultado mínimo de referencia (siempre responder la categoría más frecuente). |
| **Calibración** | Que las probabilidades del modelo "digan la verdad". |
| **Clasificación** | Predecir una categoría. |
| **Contenedor / imagen (Docker)** | La app funcionando / la "caja" con todo lo necesario para correrla. |
| **CORS** | Regla de seguridad de navegadores sobre quién puede llamar al servidor. |
| **CSV** | Archivo de texto con valores separados por coma. |
| **CV (validación cruzada)** | Evaluar rotando qué pedazo del train se usa de examen. |
| **DataFrame** | Tabla de pandas. |
| **Deduplicar** | Eliminar filas repetidas. |
| **ECE** | Error de calibración esperado (cerca de 0 = excelente). |
| **EDA** | Análisis exploratorio: mirar y graficar los datos. |
| **Endpoint** | Una "dirección" de la API (`/api/predict`). |
| **ETL** | Extraer, transformar y cargar: limpiar y preparar datos. |
| **Exactitud (accuracy)** | % de aciertos sobre el total. |
| **F1 / F1 macro** | Combinación de precisión y recall / promedio de F1 de las categorías. |
| **Feature** | Variable de entrada del modelo (acá, la intensidad de un acorde). |
| **Fixture** | Preparativo reutilizable de un test. |
| **Fuga de datos (leakage)** | Que el modelo vea información que no debería tener. |
| **Gradient Boosting** | Muchos árboles en serie, cada uno corrigiendo al anterior. |
| **Hiperparámetro** | "Perilla" que se ajusta antes de entrenar. |
| **Índice (de masculinidad percibida)** | Posición 0–1 entre femenino y masculino calculada con los votos. |
| **JSON** | Formato de texto para datos estructurados. |
| **Lift** | Probabilidad del modelo ÷ frecuencia base de la clase. |
| **MAE** | Error medio absoluto. |
| **Matriz de confusión** | Tabla de "qué era" vs. "qué dijo el modelo". |
| **Mediana** | Valor del medio al ordenar los datos. |
| **Modelo** | Fórmula aprendida de los datos que hace predicciones. |
| **Normalizar** | Llevar a un formato estándar (minúsculas, sin espacios sobrantes…). |
| **Outlier** | Dato atípico, muy alejado de lo normal. |
| **Overfitting** | Memorizar el entrenamiento y fallar con datos nuevos. |
| **Pipeline** | Serie de pasos que se ejecutan en orden. |
| **Precisión** | De lo que el modelo marcó como X, cuánto realmente era X. |
| **Probabilidad** | Número entre 0 y 1 que expresa la confianza del modelo. |
| **Recall** | De todo lo que realmente era X, cuánto encontró el modelo. |
| **Regresión** | Predecir un número. |
| **Semilla (seed)** | Número que fija el azar para repetir resultados. |
| **Spearman** | Mide si el modelo **ordena** bien (1 = mismo orden). |
| **Stratified (estratificado)** | Mantener las proporciones de cada categoría al dividir. |
| **Target** | La respuesta que se quiere predecir. |
| **Test / Train** | Datos de examen final / datos de entrenamiento. |
| **Venv** | Entorno virtual de Python propio de un proyecto. |
| **Vector / matriz** | Lista / tabla de números. |

---

## Cierre

Si llegaste hasta acá, ahora podés explicar con tus palabras:

1. **Qué problema resuelve** el proyecto y para quién.
2. **Por qué hay dos modelos** y qué descubrimiento llevó a agregar el de índice.
3. **Cómo se pasa de un archivo de 131.930 perfumes a un modelo entrenado**, paso por paso y por qué cada decisión (descartar duplicados, no equilibrar, ponderar por votos, no usar el test para decidir).
4. **Cómo se interpreta cada número** (F1 macro, error medio, Spearman, calibración, *lift*).
5. **Cómo la página habla con el servidor** y qué hace cada archivo.
6. **Qué límites tiene** y por qué se presenta como una orientación estadística y no como un veredicto.

Que sea fácil de explicar es, en sí mismo, una señal de que el proyecto está bien hecho: cada decisión tiene una razón medida y escrita.
