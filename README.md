# Predicción de PM2.5 en Santa Anita

Proyecto final del curso de Machine Learning. El objetivo es predecir la concentración de PM2.5 de la siguiente hora en la estación Santa Anita de SENAMHI, a partir de su historial reciente, y evaluar si las variables de calendario aportan por encima de ese historial.

La estación pertenece a la zona este de la red de monitoreo de Lima Metropolitana. Sobre los días con cobertura suficiente del periodo analizado, el 93 % supera la guía diaria de calidad del aire de la OMS (15 µg/m³) y el 10,3 % el Estándar de Calidad Ambiental peruano (50 µg/m³), lo que da sentido a disponer de un pronóstico a corto plazo.

## Preguntas de investigación

1. ¿Cuánto mejora un modelo de aprendizaje automático sobre la persistencia —usar la medición actual como pronóstico de la siguiente hora— en un horizonte de una hora?
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

EDA de la primera entrega desarrollado en la notebook, con tablas y gráficos exportados. El modelado corresponde a la segunda entrega. Las concentraciones están en µg/m³, unidad confirmada con el informe de vigilancia de la calidad del aire de SENAMHI para el Área Metropolitana de Lima y Callao (2021).

## Organización

- `data/raw/`: CSV de Santa Anita, conservado sin modificaciones.
- `data/processed/`: tablas de cobertura, calidad, estadísticas, patrones temporales y decisiones de diseño experimental.
- `notebooks/01_eda.ipynb`: EDA ejecutado con resultados e interpretaciones.
- `figures/`: gráficos exportados para el informe.
- `report/`: archivos LaTeX, referencias y PDF del informe.
- `slides/`: presentación del proyecto.
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

## Informe y presentación

El informe se edita en Prism usando la plantilla IEEE del curso. Las versiones del LaTeX y del PDF se guardan en `report/`, y la presentación en `slides/`.
