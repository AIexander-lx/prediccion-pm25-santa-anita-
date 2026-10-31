# Predicción de PM2.5 en Santa Anita

Proyecto final del curso de Machine Learning. El objetivo es predecir la concentración de PM2.5 de la siguiente hora en la estación Santa Anita de SENAMHI, a partir de su historial reciente, y evaluar si las variables de calendario aportan por encima de ese historial.

La estación pertenece a la zona este de la red de monitoreo de Lima Metropolitana. Sobre los días con cobertura suficiente del periodo analizado, el 93 % supera la guía diaria de calidad del aire de la OMS (15 µg/m³) y el 10,3 % el Estándar de Calidad Ambiental peruano (50 µg/m³), lo que da sentido a disponer de un pronóstico a corto plazo.

## Preguntas de investigación

1. ¿Cuánto mejora un modelo de aprendizaje automático sobre la persistencia al usar la medición actual como pronóstico de la siguiente hora en un horizonte de una hora?
2. ¿Aportan las variables de calendario (hora del día y día de la semana) por encima de lo que ya contiene el historial reciente de la propia serie?
3. ¿Se degrada el desempeño en el régimen de concentraciones altas, que es el de mayor relevancia sanitaria?

La primera entrega no las responde: reúne la evidencia descriptiva necesaria para plantearlas y para diseñar el experimento que las responderá.

## Integrantes

- Zheng Chan, Enrique
- Limaco Porras, Requelmy
- León Pantaleón, Jobeth Alexander
- Huamán Huamaní, Josué Yeremi

Repositorio del proyecto: https://github.com/AIexander-lx/prediccion-pm25-santa-anita-

## Estado

EDA de la primera entrega desarrollado en la notebook, con tablas y gráficos exportados. El modelado corresponde a la segunda entrega; el reparto de roles y tareas está en la sección "Entrega 2 (P2)". Las concentraciones están en µg/m³, unidad confirmada con el informe de vigilancia de la calidad del aire de SENAMHI para el Área Metropolitana de Lima y Callao (2021).

## Entrega 2 (P2): roles y tareas

Plan de trabajo del equipo para la segunda etapa del proyecto final (modelado, evaluación y discusión). La primera entrega quedó congelada en el tag `p1-entrega`.

### La entrega

| | |
|---|---|
| **Etapa** | P2: modelado, evaluación y discusión |
| **Semana de entrega** | **Semana 15 del curso** (la guía actualizada la adelantó desde la semana 16) |
| **Fecha exacta** | _(completar con la fecha de Canvas)_ |
| **Exposición** | Máximo **10 minutos**, seguidos de preguntas, durante la clase de laboratorio de esa semana |
| **Rúbrica** | En Canvas |

#### Artefactos (los tres)

1. **Paper en PDF**, con el template IEEE de conferencias, **máximo 12 páginas**, en español o en inglés. Incluye todo el contenido de P1 más lo nuevo de P2.
2. **Repositorio público** de código, organizado y reproducible. Su calidad y organización se evalúan.
3. **Presentación** en PDF. Participan todos los integrantes y solo uno comparte pantalla.

#### Contenido nuevo de P2 (además de lo de P1)

- Preprocesamiento e ingeniería de características.
- Un **baseline** definido.
- Implementación y comparación de **al menos dos modelos** de ML.
- Diseño experimental, validación y ajuste de hiperparámetros.
- Evaluación con métricas apropiadas.
- Análisis e interpretación de resultados y errores.
- Discusión, limitaciones, consideraciones éticas y conclusiones.

#### Estructura del paper

| # | Sección | Etapa |
|---|---|---|
| 1 | Resumen | P1 y P2 |
| 2 | Introducción y formulación del problema | P1 y P2 |
| 3 | Datos y análisis exploratorio (EDA) | P1 y P2 |
| 4 | Preprocesamiento e ingeniería de características | P2 |
| 5 | Metodología y modelos | P2 |
| 6 | Diseño experimental y evaluación | P2 |
| 7 | Resultados y análisis | P2 |
| 8 | Discusión y limitaciones | P2 |
| 9 | Conclusiones | P2 |
| 10 | Referencias | P1 y P2 |

Se valora especialmente la capacidad de **justificar las decisiones** y de demostrar comprensión de los conceptos, además del desempeño de los modelos. Todos deben poder explicar las decisiones metodológicas.

### División del trabajo por roles

Cuatro roles de carga similar. Cada rol tiene su código, sus secciones del paper y sus figuras o tablas, y todos aportan a la presentación.

> **Cada integrante se asigna un rol** escribiendo su nombre en la columna "Responsable".

| Rol | Responsable | Responsabilidades | Secciones del paper |
|---|---|---|---|
| **1. Datos y características** | _(asignar)_ | Construir el conjunto supervisado (rezagos, medias móviles solo con el pasado, hora y día); manejar faltantes y ventanas incompletas sin fuga; aplicar la partición cronológica; escalado dentro del pipeline; actualizar el EDA que pasa al paper. | 3 (actualizada) y 4 |
| **2. Baseline y modelos lineales** | _(asignar)_ | Baseline de persistencia; Ridge y Lasso; validación temporal y búsqueda de hiperparámetros; definir y justificar las métricas (MAE, RMSE, R², MSE); protocolo experimental. | 5 (baseline y lineales) y 6 |
| **3. Modelos no lineales y análisis de errores** | _(asignar)_ | Random Forest y, si se decide, boosting; ajuste de hiperparámetros; comparación con el baseline y los lineales; importancia de variables; análisis de errores y del régimen de concentraciones altas; respuesta a las tres preguntas de investigación. | 5 (no lineales) y 7 |
| **4. Reporte, repositorio y presentación** | _(asignar)_ | Armar el paper en IEEE (hasta 12 páginas); redactar resumen, introducción, discusión, limitaciones, ética, conclusiones y referencias; mantener el repo reproducible (README, dependencias, notebooks); armar la presentación de 10 minutos y coordinar el ensayo. | 1, 2, 8, 9 y 10 |

#### Responsabilidades compartidas

- Revisar el trabajo de los demás antes de integrar a `main`.
- Todos participan en la presentación y responden preguntas sobre datos, modelos, evaluación y decisiones.
- Probar que el repositorio se ejecuta desde cero siguiendo el README.

### Tareas por rol

Marca cada tarea con `[x]` cuando esté lista y sube el cambio. Cada rol trabaja en su propia rama (por ejemplo `p2-rol1-datos`) y se integra a `main` con un pull request revisado por otro integrante.

#### Rol 1: Datos y características
- [ ] Definir el conjunto supervisado: entrada hasta `t`, etiqueta `PM2.5(t+1)`.
- [ ] Construir los rezagos (1, 3, 6, 12 y 24 horas) y las medias móviles usando solo información pasada.
- [ ] Construir las variables de calendario (hora del día y día de la semana) y decidir su codificación.
- [ ] Decidir qué hacer con faltantes y ventanas incompletas, sin imputar con ceros ni usar información futura.
- [ ] Aplicar la partición cronológica (entrenamiento, validación, prueba) y guardarla.
- [ ] Implementar el preprocesamiento (escalado, etc.) ajustado solo con entrenamiento, dentro de un pipeline.
- [ ] Verificar la ausencia de fuga de información con una comprobación explícita.
- [ ] Actualizar el EDA para el paper (sección 3) y redactar la sección 4.

#### Rol 2: Baseline y modelos lineales
- [ ] Implementar el baseline de persistencia y calcular sus métricas en validación.
- [ ] Definir y justificar las métricas (MAE, RMSE, MSE, R²) y fijar la forma de comparar con el baseline.
- [ ] Implementar Ridge y Lasso con los rezagos y las variables de calendario.
- [ ] Ajustar `alpha` con validación temporal (no aleatoria) y registrar la búsqueda.
- [ ] Comparar con y sin variables de calendario para la pregunta de investigación 2.
- [ ] Interpretar los coeficientes (cuáles quedan en cero en Lasso).
- [ ] Redactar las secciones 5 (baseline y lineales) y 6.

#### Rol 3: Modelos no lineales y análisis de errores
- [ ] Implementar Random Forest sobre el mismo conjunto de características.
- [ ] Ajustar hiperparámetros con validación temporal (por ejemplo `n_estimators`, `max_features`, `min_samples_leaf`).
- [ ] Decidir si se prueba un segundo modelo no lineal (por ejemplo boosting) y comparar.
- [ ] Calcular la importancia de variables e interpretarla (incluyendo sus limitaciones).
- [ ] Analizar los errores: dónde falla el modelo, por hora, mes y nivel de concentración.
- [ ] Evaluar el desempeño en el régimen de concentraciones altas (pregunta 3).
- [ ] Redactar las secciones 5 (no lineales) y 7, con tablas y figuras comparativas.

#### Rol 4: Reporte, repositorio y presentación
- [ ] Configurar el paper con el template IEEE (LaTeX o Word) y respetar el límite de 12 páginas.
- [ ] Actualizar las secciones 1 y 2 con los resultados de P2.
- [ ] Integrar las secciones 3 a 7 de los demás roles y unificar estilo, notación y referencias.
- [ ] Redactar la discusión, limitaciones, consideraciones éticas, conclusiones y referencias (secciones 8 a 10).
- [ ] Mantener el repositorio: README actualizado, dependencias, instrucciones de ejecución y notebooks ordenados.
- [ ] Verificar que los experimentos se reproducen desde cero.
- [ ] Armar la presentación (10 minutos) y exportarla a PDF.
- [ ] Organizar un ensayo en el que todos hablen y practiquen las preguntas posibles.
- [ ] Entregar el paper, el repositorio y la presentación en Canvas.

#### Tareas de todos
- [ ] Asignarse un rol en la tabla de arriba.
- [ ] Confirmar la fecha exacta de entrega y la fecha de la exposición.
- [ ] Hacer una última revisión conjunta del paper antes de entregar.
- [ ] Preparar respuestas sobre datos, modelos, evaluación y decisiones para la ronda de preguntas.

## Organización

- `data/raw/`: CSV de Santa Anita, conservado sin modificaciones.
- `data/processed/`: tablas de cobertura, calidad, estadísticas, patrones temporales y decisiones de diseño experimental.
- `notebooks/01_eda.ipynb`: EDA ejecutado con resultados e interpretaciones.
- `figures/`: gráficos exportados para el informe.
- `pyproject.toml`: dependencias declaradas del proyecto.
- `uv.lock`: versiones exactas de todas las dependencias.
- `requirements.txt`: exportación del bloqueo de versiones, para quien use pip.

## Datos

Fuente: SENAMHI, conjunto [Monitoreo de los contaminantes del aire en Lima Metropolitana](https://www.datosabiertos.gob.pe/dataset/monitoreo-de-los-contaminantes-del-aire-en-lima-metropolitana-servicio-nacional-de), publicado en la Plataforma Nacional de Datos Abiertos.

Licencia indicada por el proveedor: Open Data Commons Attribution License. Esta atribución corresponde a los datos; no establece una licencia para el código del proyecto.

El archivo `data/raw/santa_anita_2015_2024.csv` es una copia sin cambios del CSV filtrado por estación proporcionado por el equipo. Contiene registros desde enero de 2015 hasta mayo de 2024. La notebook selecciona del 1 de enero de 2022 al 30 de abril de 2024, conservando el archivo de entrada y las horas sin medición.

## Preparación del entorno

El proyecto fija sus dependencias con [uv](https://docs.astral.sh/uv/). El archivo `uv.lock` registra la versión exacta de cada paquete, resuelta para Windows, macOS y Linux, de modo que cualquier persona obtiene el mismo entorno con el que se produjeron las tablas y figuras de este repositorio.

Instalar uv una sola vez, desde PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Después, desde la carpeta del repositorio:

```powershell
uv sync --frozen
uv run jupyter lab
```

`uv sync --frozen` crea el entorno virtual en `.venv/` e instala exactamente lo que indica `uv.lock`, sin resolver versiones nuevas. No hace falta crear ni activar el entorno a mano. Para incorporar una dependencia se usa `uv add <paquete>`, que actualiza `pyproject.toml` y `uv.lock`; ambos archivos deben quedar registrados en el control de versiones.

Quien prefiera no instalar uv puede reproducir el entorno con pip. Este camino instala las mismas versiones de los paquetes, pero no fija la versión de Python:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
jupyter lab
```

El archivo `requirements.txt` se genera a partir de `uv.lock` y no debe editarse a mano:

```powershell
uv export --no-hashes --no-dev --no-emit-project -o requirements.txt
```

## Reproducir el análisis

Con el entorno listo, abrir `notebooks/01_eda.ipynb` y ejecutar todas las celdas en orden. Las rutas funcionan desde la raíz del repositorio o desde `notebooks/`. La ejecución tarda menos de un minuto y actualiza treinta tablas en `data/processed/` y trece figuras en `figures/`, cada una en PNG de 300 dpi y PDF vectorial. La primera celda registra las versiones utilizadas y fija la semilla global; la última verifica por hash que el CSV de entrada no fue modificado.

El EDA no imputa faltantes, no elimina valores extremos y no entrena modelos. Se exploró todo el periodo seleccionado; esa exposición se declara en la sección 9 de la notebook, que además fija los cortes de las particiones y el protocolo de evaluación de la segunda etapa en `data/processed/particiones_propuestas.csv`.

Las figuras complementarias describen la disponibilidad, los promedios mensuales y la correlación simultánea de PM10, PM2.5 y NO2. El objetivo predictivo sigue siendo PM2.5 una hora después: la correlación entre contaminantes no se interpreta como evidencia de desempeño predictivo. Consultar `figures/README.md` para elegir las figuras y sus pies de imagen.

