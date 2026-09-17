# Figuras para la primera entrega

Generadas por `notebooks/01_eda.ipynb`. Cada figura está disponible en PNG (300 dpi) y PDF vectorial. Para LaTeX se recomienda PDF. La unidad de concentración está pendiente de confirmación con SENAMHI; los gráficos la identifican como «unidad del archivo».

## Ubicación y pies de figura sugeridos

1. **01_cobertura_anual — Selección del periodo.** Porcentaje de horas con al menos una medición de PM2.5 disponible en Santa Anita. Los años 2015–2023 usan el calendario completo; 2024 comprende enero–mayo. Los duplicados solo se colapsan como indicador de disponibilidad, sin promediar sus concentraciones.
2. **02_cobertura_mensual — Calidad de datos.** Cobertura mensual de PM2.5 entre enero de 2022 y abril de 2024, calculada respecto al total de horas de cada mes.
3. **03_distribucion_pm25 — Distribución y valores atípicos.** Histograma y diagrama de caja de las mediciones horarias disponibles. La línea discontinua indica la mediana. Los valores extremos se conservan.
4. **04_serie_temporal — Comportamiento temporal.** Concentraciones horarias de PM2.5 y mediana diaria calculada en días con al menos 18 mediciones. Se mantienen los huecos de la serie.
5. **05_patrones_calendario — Patrones horarios y semanales.** Mediana de PM2.5 por hora y día de la semana. La banda representa los percentiles 25 y 75 de las observaciones, no un intervalo de confianza. Las diferencias no demuestran una mejora predictiva.
6. **06_resumen_mensual — Complementaria.** Media y mediana mensual de las concentraciones disponibles. Interpretar junto con la cobertura de cada mes.
7. **07_horas_consecutivas — Complementaria.** Distribución conjunta de PM2.5 en horas consecutivas con ambas mediciones disponibles. El color representa el número de pares en escala logarítmica y la diagonal indica igualdad de concentraciones.

Las primeras cinco figuras cubren los puntos centrales del EDA. No es necesario incluir todas si el espacio del informe es limitado.

## Ejemplo en LaTeX

Subir a Prism el PDF de la figura, conservando la carpeta `figures/`, y colocar lo siguiente en el apartado correspondiente:

```latex
\begin{figure}[htbp]
    \centering
    \includegraphics[width=\columnwidth]{figures/01_cobertura_anual.pdf}
    \caption{Cobertura anual de PM2.5 en Santa Anita. En 2024 se consideran únicamente enero a mayo.}
    \label{fig:cobertura-anual}
\end{figure}
```

En IEEE, para las figuras anchas con dos paneles puede usarse `figure*` y `width=\textwidth`. La plantilla debe cargar `graphicx`. Las figuras con concentración requieren confirmar la unidad antes de cerrar la entrega.
