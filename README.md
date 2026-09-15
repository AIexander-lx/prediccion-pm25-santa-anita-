# Predicción de PM2.5 en Santa Anita

Proyecto del curso de Machine Learning para predecir la concentración de PM2.5 de la siguiente hora en la estación Santa Anita de SENAMHI.

## Estado

Estructura inicial del repositorio. El análisis exploratorio, el modelado y el informe están pendientes de desarrollo.

## Organización

- `data/raw/`: CSV de Santa Anita, conservado sin modificaciones.
- `data/processed/`: datos preparados que se generen durante el análisis.
- `notebooks/01_eda.ipynb`: notebook base para el EDA, todavía sin análisis.
- `figures/`: gráficos exportados para el informe.
- `report/`: archivos LaTeX, referencias y PDF del informe.
- `slides/`: presentación del proyecto.
- `requirements.txt`: dependencias de Python.

## Datos

Fuente: SENAMHI, conjunto [Monitoreo de los contaminantes del aire en Lima Metropolitana](https://www.datosabiertos.gob.pe/dataset/monitoreo-de-los-contaminantes-del-aire-en-lima-metropolitana-servicio-nacional-de), publicado en la Plataforma Nacional de Datos Abiertos.

Licencia indicada por el proveedor: Open Data Commons Attribution License. Esta atribución corresponde a los datos; no establece una licencia para el código del proyecto.

El archivo `data/raw/santa_anita_2015_2024.csv` es una copia sin cambios del CSV filtrado por estación proporcionado por el equipo. Contiene registros desde enero de 2015 hasta mayo de 2024. El periodo de estudio será del 1 de enero de 2022 al 30 de abril de 2024; el filtro se implementará en la notebook, conservando el archivo de entrada.

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

Abrir `notebooks/01_eda.ipynb`. Por ahora solo contiene la estructura de trabajo, sin resultados.

## Informe y presentación

El informe se editará en Prism usando la plantilla IEEE del curso. Guardar las versiones del LaTeX y del PDF en `report/`, y la presentación en `slides/`. El archivo `report/main.tex` es únicamente un marcador inicial, no la plantilla definitiva.
