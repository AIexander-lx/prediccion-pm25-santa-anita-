# Figuras para la primera entrega

Generadas por `notebooks/01_eda.ipynb`. Cada figura está disponible en PNG (300 dpi) y PDF vectorial. Para LaTeX se recomienda PDF. Las concentraciones están en µg/m³, unidad confirmada con el informe de vigilancia de la calidad del aire de SENAMHI para el Área Metropolitana de Lima y Callao (2021).

## Figuras centrales

1. **01_cobertura_anual — Selección del periodo.** Porcentaje de horas con al menos una medición de PM2.5 disponible en Santa Anita. Los años 2015–2023 usan el calendario completo; 2024 comprende enero–mayo. Los duplicados solo se colapsan como indicador de disponibilidad, sin promediar sus concentraciones.
2. **02_cobertura_mensual — Calidad de datos.** Cobertura mensual de PM2.5 entre enero de 2022 y abril de 2024, calculada respecto al total de horas de cada mes.
3. **03_distribucion_pm25 — Distribución y valores atípicos.** Histograma y diagrama de caja de las mediciones horarias disponibles. La línea discontinua indica la mediana. Los valores extremos se conservan.
4. **04_serie_temporal — Comportamiento temporal.** Concentraciones horarias de PM2.5 y mediana diaria calculada en días con al menos 18 mediciones. Las líneas horizontales marcan el ECA peruano (50 µg/m³) y la guía de la OMS (15 µg/m³), ambos definidos sobre promedios de 24 horas, por lo que solo aplican al panel inferior. Se mantienen los huecos de la serie.
5. **05_patrones_calendario — Patrones horarios y semanales.** Mediana de PM2.5 por hora y día de la semana. La banda representa los percentiles 25 y 75 de las observaciones, no un intervalo de confianza. Las diferencias no demuestran una mejora predictiva.
6. **11_atipicos_calendario — Atípicos.** Distribución de las mediciones señaladas por la regla IQR según año, mes y hora del día. Es el respaldo de la decisión de conservarlas: su concentración en 2022, en invierno y al mediodía es incompatible con un ruido instrumental.
7. **12_distribucion_anual — Cambio de régimen.** Diagrama de caja de las concentraciones horarias por año y medianas mensuales superpuestas año a año. Documenta el descenso del nivel medio a lo largo del periodo y su consecuencia sobre la partición cronológica. El tramo de 2024 abarca solo enero–abril.
8. **13_autocorrelacion — Dependencia temporal.** Correlación de Pearson entre la serie y sus rezagos hasta 72 horas, y correlación parcial de los primeros 24. Cada rezago se calcula con las horas en que ambos valores están disponibles; la correlación parcial se deriva por Durbin–Levinson. Justifica la elección de la ventana de rezagos.

## Figuras complementarias

9. **06_resumen_mensual.** Media y mediana mensual de las concentraciones disponibles. Interpretar junto con la cobertura de cada mes.
10. **07_horas_consecutivas.** Distribución conjunta de PM2.5 en horas consecutivas con ambas mediciones disponibles. El color representa el número de pares en escala logarítmica y la diagonal indica igualdad de concentraciones.
11. **08_faltantes_contaminantes.** Porcentaje mensual de horas sin medición para PM10, PM2.5 y NO2. El eje horizontal muestra meses reales y la escala de color representa faltantes, no concentraciones.
12. **09_promedios_mensuales_contaminantes.** Media mensual de cada contaminante calculada sobre sus mediciones disponibles. Los paneles tienen escalas verticales propias y se interpretan junto con la cobertura mensual. El tramo final de NO2 debe leerse junto con la reserva sobre instrumentación de la sección 4 de la notebook.
13. **10_correlacion_contaminantes.** Correlación de Pearson entre contaminantes medidos en la misma hora. Cada par utiliza las horas compartidas con medición; no describe la relación con el valor de la hora siguiente.

Las ocho primeras cubren los puntos centrales del EDA. Las cinco restantes aportan contexto y pueden omitirse si el espacio del informe es limitado.

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

En IEEE, para las figuras anchas con varios paneles puede usarse `figure*` y `width=\textwidth`. La plantilla debe cargar `graphicx`.
