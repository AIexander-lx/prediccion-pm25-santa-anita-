# Predicción horaria de PM2.5 en Santa Anita

Proyecto final del curso de Machine Learning (UTEC). Predice la concentración de PM2.5 de la **siguiente hora** en la estación Santa Anita de SENAMHI (Lima Metropolitana) a partir de su historial reciente, y evalúa si las variables de calendario (hora del día y día de la semana) aportan por encima de ese historial.

- **Tarea:** regresión supervisada, `PM2.5(t+1)` a partir de información hasta `t`.
- **Datos:** 19.391 mediciones horarias disponibles de 20.424 horas esperadas (enero de 2022 a abril de 2024).
- **Evaluación:** partición cronológica (entrenamiento, validación, prueba), validación de origen expansivo, comprobaciones explícitas de fuga de información.
- **Modelos:** persistencia (baseline), Ridge, Lasso, Random Forest y HistGradientBoosting.

Paper: [`paper/`](paper/) (plantilla IEEE, en español). Plan interno del equipo: [`docs/plan_p2.md`](docs/plan_p2.md).

## Integrantes

| Integrante | Rol en P2 |
|---|---|
| León Pantaleón, Jobeth Alexander | Datos y características |
| Huamán Huamaní, Josué Yeremi | Baseline y modelos lineales |
| Zheng Chan, Enrique | Modelos no lineales y análisis de errores |
| Limaco Porras, Requelmy | Reporte, repositorio y presentación |

## Preguntas de investigación y respuesta resumida

1. **PI1. ¿Cuánto mejora un modelo de ML sobre la persistencia?** En prueba, Random Forest y HistGB reducen el MAE entre 14 y 15 %; Ridge, 7 %.
2. **PI2. ¿Aporta el calendario?** Solo a los modelos de árboles (2 a 3 % en validación), por medio de la hora; el día de la semana no aporta.
3. **PI3. ¿Se degrada el desempeño con concentraciones altas?** Sí: en el decil superior el MAE es de 2 a 4 veces el del resto y todos los modelos subestiman por encima de 50 µg/m³.

## Resultados principales

MAE en µg/m³ (menor es mejor). Mejora: reducción respecto a la persistencia del mismo bloque.

| Modelo | MAE validación | MAE prueba | Mejora en prueba |
|---|---|---|---|
| Persistencia (baseline) | 3,378 | 2,829 | n/a |
| Ridge (sin calendario) | 3,141 | 2,626 | 7,2 % |
| Random Forest (con calendario) | 2,985 | 2,413 | 14,7 % |
| HistGB (con calendario) | 3,057 | 2,428 | 14,2 % |

Tablas completas, intervalos de confianza y análisis de errores: sección de resultados del paper y `data/processed/*.csv`. Las concentraciones bajan entre bloques (media de la respuesta de 32,9 en entrenamiento a 17,8 en prueba), por lo que los errores absolutos no son comparables entre bloques.

## Estructura del repositorio


```
.
├── data/
│   ├── raw/            CSV de Santa Anita, sin modificar
│   └── processed/      tablas del EDA, conjunto supervisado y resultados (CSV)
├── notebooks/
│   └── 01_eda.ipynb    análisis exploratorio (P1)
├── scripts/            pipeline de P2, se ejecuta en orden (01 a 06)
├── src/pm25/           funciones de construcción de características
├── figures/            figuras en PNG (300 dpi) y PDF vectorial
├── paper/              fuentes LaTeX del artículo (main.tex, secciones, refs.bib)
├── docs/               plan de trabajo de P2
├── pyproject.toml      dependencias declaradas
├── uv.lock             versiones exactas
└── requirements.txt    exportación del bloqueo, para quien use pip
```


## Datos

Fuente: SENAMHI, conjunto [Monitoreo de los contaminantes del aire en Lima Metropolitana](https://www.datosabiertos.gob.pe/dataset/monitoreo-de-los-contaminantes-del-aire-en-lima-metropolitana-servicio-nacional-de), Plataforma Nacional de Datos Abiertos. Licencia del proveedor: Open Data Commons Attribution License (aplica a los datos, no al código).

`data/raw/santa_anita_2015_2024.csv` es el CSV filtrado por estación (82.542 registros, 15 columnas, enero de 2015 a mayo de 2024). El análisis usa del 1 de enero de 2022 al 30 de abril de 2024. Las concentraciones están en µg/m³, unidad confirmada con el informe de vigilancia de SENAMHI para Lima y Callao (2021). Para obtener el archivo de nuevo, descargar el conjunto desde el enlace anterior y filtrar por la estación Santa Anita.

## Instalación

El proyecto fija sus dependencias con [uv](https://docs.astral.sh/uv/). La versión de Python está en `.python-version`.

```bash
# instalar uv una vez (Windows, PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# desde la raíz del repositorio
uv sync --frozen
```

`uv sync --frozen` crea `.venv/` con las versiones exactas de `uv.lock`. Alternativa con pip (mismas versiones de paquetes, sin fijar la de Python):

```bash
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1   |   Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Cómo reproducir los resultados

Desde la raíz, en este orden:

```bash
uv run jupyter lab                                  # abrir notebooks/01_eda.ipynb y ejecutar todo (EDA, < 1 min)
uv run python scripts/01_construir_dataset.py       # conjunto supervisado y particiones
uv run python scripts/02_verificar_fuga.py          # 12 comprobaciones de fuga de información
uv run python scripts/03_figura_particiones.py      # figura 14
uv run python scripts/04_modelos_lineales.py        # persistencia, Ridge y Lasso
uv run python scripts/05_modelos_no_lineales.py     # Random Forest y HistGB (~15 min con 2 núcleos)
uv run python scripts/06_analisis_errores.py        # errores por hora, mes y nivel; figuras 15 a 18
```

| Script | Qué hace | Salida |
|---|---|---|
| `01_construir_dataset.py` | Rezagos, medias móviles y calendario solo con el pasado; descarta filas con huecos; asigna bloques cronológicos | `data/processed/supervisado_*.csv` |
| `02_verificar_fuga.py` | Pruebas explícitas de ausencia de fuga, con un control negativo | `verificacion_fuga.csv` |
| `03_figura_particiones.py` | Figura de la partición cronológica | `figures/14_*` |
| `04_modelos_lineales.py` | Baseline y modelos lineales; búsqueda de `alpha` con validación temporal | `lineales_*.csv` |
| `05_modelos_no_lineales.py` | Árboles con y sin calendario, importancia por permutación | `no_lineales_*.csv` |
| `06_analisis_errores.py` | No reentrena; desagrega errores y calcula intervalos por bootstrap de bloques | `errores_*.csv`, `figures/15_*` a `18_*` |

El resultado esperado son los mismos CSV que ya están en `data/processed/` y las figuras de `figures/`. Los modelos usan semilla fija.

## Compilar el paper

Con una distribución de LaTeX que incluya `IEEEtran` (por ejemplo TeX Live) o subiendo `paper/` y `figures/` a Overleaf:

```bash
cd paper
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

## Limitaciones

Una sola estación y 28 meses; concentraciones que bajan entre entrenamiento y prueba; EDA que examinó todo el periodo, incluida la prueba (los cortes se fijaron antes de entrenar y la selección usó solo validación); sin variables meteorológicas. Detalle en la sección de discusión del paper.

## Licencia y atribución

Datos: SENAMHI, Open Data Commons Attribution License. El código no tiene licencia declarada; si se desea reutilizar, agregar un archivo `LICENSE`.
