# Predicción de PM2.5 en Santa Anita

Proyecto del curso de Machine Learning para predecir la concentración de PM2.5 de la siguiente hora en la estación Santa Anita de SENAMHI.

Repositorio del proyecto: https://github.com/AIexander-lx/prediccion-pm25-santa-anita-

## Estado

EDA de la primera entrega desarrollado en la notebook, con tablas y gráficos exportados. El modelado corresponde a la segunda entrega. La unidad de concentración debe confirmarse con el proveedor antes de cerrar el informe.

## Organización

- `data/raw/`: CSV de Santa Anita, conservado sin modificaciones.
- `data/processed/`: tablas de cobertura, calidad, estadísticas y patrones temporales.
- `notebooks/01_eda.ipynb`: EDA ejecutado con resultados e interpretaciones.
- `figures/`: gráficos exportados para el informe.
- `report/`: archivos LaTeX, referencias y PDF del informe.
- `slides/`: presentación del proyecto.
- `requirements.txt`: dependencias de Python.

## Datos

Fuente: SENAMHI, conjunto [Monitoreo de los contaminantes del aire en Lima Metropolitana](https://www.datosabiertos.gob.pe/dataset/monitoreo-de-los-contaminantes-del-aire-en-lima-metropolitana-servicio-nacional-de), publicado en la Plataforma Nacional de Datos Abiertos.

Licencia indicada por el proveedor: Open Data Commons Attribution License. Esta atribución corresponde a los datos; no establece una licencia para el código del proyecto.

El archivo `data/raw/santa_anita_2015_2024.csv` es una copia sin cambios del CSV filtrado por estación proporcionado por el equipo. Contiene registros desde enero de 2015 hasta mayo de 2024. La notebook selecciona del 1 de enero de 2022 al 30 de abril de 2024, conservando el archivo de entrada y las horas sin medición.

## Preparación del entorno

Desde la carpeta del repositorio:

```sh
python -m venv .venv
```

En PowerShell, activar el entorno e instalar las dependencias:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
jupyter lab
```

Abrir `notebooks/01_eda.ipynb` y ejecutar todas las celdas en orden. Las rutas funcionan desde la raíz del repositorio o desde `notebooks/`. La ejecución actualiza las tablas en `data/processed/` y diez figuras en `figures/`, cada una en PNG de 300 dpi y PDF vectorial. La primera celda registra las versiones utilizadas.

Las tres figuras complementarias describen la disponibilidad, los promedios mensuales y la correlación simultánea de PM10, PM2.5 y NO2. El objetivo predictivo sigue siendo PM2.5 una hora después. La correlación entre contaminantes no se interpreta como evidencia de desempeño predictivo.

El EDA no imputa faltantes, no elimina valores extremos y no entrena modelos. Se exploró todo el periodo seleccionado; esta exposición debe documentarse al definir la evaluación temporal de P2.

Consultar `figures/README.md` para elegir las figuras y sus pies de imagen.

## Informe y presentación

El informe se edita en Prism usando la plantilla IEEE del curso. Las versiones del LaTeX y del PDF se guardan en `report/`, y la presentación en `slides/`.
