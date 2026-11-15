# Plan de trabajo de la Entrega 2 (P2)

Documento interno del equipo con la entrega, los roles y las tareas. El resumen del proyecto está en el [README](../README.md).


## La entrega

| | |
|---|---|
| **Etapa** | P2: modelado, evaluación y discusión |
| **Semana de entrega** | **Semana 15 del curso** (la guía actualizada la adelantó desde la semana 16) |
| **Fecha exacta** | _(completar con la fecha de Canvas)_ |
| **Exposición** | Máximo **10 minutos**, seguidos de preguntas, durante la clase de laboratorio de esa semana |
| **Rúbrica** | En Canvas |

### Artefactos (los tres)

1. **Paper en PDF**, con el template IEEE de conferencias, **máximo 12 páginas**, en español o en inglés. Incluye todo el contenido de P1 más lo nuevo de P2.
2. **Repositorio público** de código, organizado y reproducible. Su calidad y organización se evalúan.
3. **Presentación** en PDF. Participan todos los integrantes y solo uno comparte pantalla.

### Contenido nuevo de P2 (además de lo de P1)

- Preprocesamiento e ingeniería de características.
- Un **baseline** definido.
- Implementación y comparación de **al menos dos modelos** de ML.
- Diseño experimental, validación y ajuste de hiperparámetros.
- Evaluación con métricas apropiadas.
- Análisis e interpretación de resultados y errores.
- Discusión, limitaciones, consideraciones éticas y conclusiones.

### Estructura del paper

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

## División del trabajo por roles

Cuatro roles de carga similar. Cada rol tiene su código, sus secciones del paper y sus figuras o tablas, y todos aportan a la presentación.

> **Cada integrante se asigna un rol** escribiendo su nombre en la columna "Responsable".

| Rol | Responsable | Responsabilidades | Secciones del paper |
|---|---|---|---|
| **1. Datos y características** | Alexander | Construir el conjunto supervisado (rezagos, medias móviles solo con el pasado, hora y día); manejar faltantes y ventanas incompletas sin fuga; aplicar la partición cronológica; escalado dentro del pipeline; actualizar el EDA que pasa al paper. | 3 (actualizada) y 4 |
| **2. Baseline y modelos lineales** |Josue| Baseline de persistencia; Ridge y Lasso; validación temporal y búsqueda de hiperparámetros; definir y justificar las métricas (MAE, RMSE, R², MSE); protocolo experimental. | 5 (baseline y lineales) y 6 |
| **3. Modelos no lineales y análisis de errores** | Enrique | Random Forest y, si se decide, boosting; ajuste de hiperparámetros; comparación con el baseline y los lineales; importancia de variables; análisis de errores y del régimen de concentraciones altas; respuesta a las tres preguntas de investigación. | 5 (no lineales) y 7 |
| **4. Reporte, repositorio y presentación** | Requelmy | Armar el paper en IEEE (hasta 12 páginas); redactar resumen, introducción, discusión, limitaciones, ética, conclusiones y referencias; mantener el repo reproducible (README, dependencias, notebooks); armar la presentación de 10 minutos y coordinar el ensayo. | 1, 2, 8, 9 y 10 |

### Responsabilidades compartidas

- Revisar el trabajo de los demás antes de integrar a `main`.
- Todos participan en la presentación y responden preguntas sobre datos, modelos, evaluación y decisiones.
- Probar que el repositorio se ejecuta desde cero siguiendo el README.

## Tareas por rol

Marca cada tarea con `[x]` cuando esté lista y sube el cambio. Cada rol trabaja en su propia rama (por ejemplo `p2-rol1-datos`) y se integra a `main` con un pull request revisado por otro integrante.

### Rol 1: Datos y características
- [x] Definir el conjunto supervisado: entrada hasta `t`, etiqueta `PM2.5(t+1)`.
- [x] Construir los rezagos (1, 3, 6, 12 y 24 horas) y las medias móviles usando solo información pasada.
- [x] Construir las variables de calendario (hora del día y día de la semana) y decidir su codificación.
- [x] Decidir qué hacer con faltantes y ventanas incompletas, sin imputar con ceros ni usar información futura.
- [x] Aplicar la partición cronológica (entrenamiento, validación, prueba) y guardarla.
- [x] Implementar el preprocesamiento (escalado, etc.) ajustado solo con entrenamiento, dentro de un pipeline.
- [x] Verificar la ausencia de fuga de información con una comprobación explícita.
- [x] Actualizar el EDA para el paper (sección 3) y redactar la sección 4.

### Rol 2: Baseline y modelos lineales
- [x] Implementar el baseline de persistencia y calcular sus métricas en validación.
- [x] Definir y justificar las métricas (MAE, RMSE, MSE, R²) y fijar la forma de comparar con el baseline.
- [x] Implementar Ridge y Lasso con los rezagos y las variables de calendario.
- [x] Ajustar `alpha` con validación temporal (no aleatoria) y registrar la búsqueda.
- [x] Comparar con y sin variables de calendario para la pregunta de investigación 2.
- [x] Interpretar los coeficientes (cuáles quedan en cero en Lasso).
- [x] Redactar las secciones 5 (baseline y lineales) y 6.

### Rol 3: Modelos no lineales y análisis de errores
- [x] Implementar Random Forest sobre el mismo conjunto de características.
- [x] Ajustar hiperparámetros con validación temporal (por ejemplo `n_estimators`, `max_features`, `min_samples_leaf`).
- [x] Decidir si se prueba un segundo modelo no lineal (por ejemplo boosting) y comparar.
- [x] Calcular la importancia de variables e interpretarla (incluyendo sus limitaciones).
- [x] Analizar los errores: dónde falla el modelo, por hora, mes y nivel de concentración.
- [x] Evaluar el desempeño en el régimen de concentraciones altas (pregunta 3).
- [x] Redactar las secciones 5 (no lineales) y 7, con tablas y figuras comparativas.

### Rol 4: Reporte, repositorio y presentación
- [ ] Configurar el paper con el template IEEE (LaTeX o Word) y respetar el límite de 12 páginas.
- [ ] Actualizar las secciones 1 y 2 con los resultados de P2.
- [ ] Integrar las secciones 3 a 7 de los demás roles y unificar estilo, notación y referencias.
- [ ] Redactar la discusión, limitaciones, consideraciones éticas, conclusiones y referencias (secciones 8 a 10).
- [ ] Mantener el repositorio: README actualizado, dependencias, instrucciones de ejecución y notebooks ordenados.
- [ ] Verificar que los experimentos se reproducen desde cero.
- [ ] Armar la presentación (10 minutos) y exportarla a PDF.
- [ ] Organizar un ensayo en el que todos hablen y practiquen las preguntas posibles.
- [ ] Entregar el paper, el repositorio y la presentación en Canvas.

### Tareas de todos
- [ ] Asignarse un rol en la tabla de arriba.
- [ ] Confirmar la fecha exacta de entrega y la fecha de la exposición.
- [ ] Hacer una última revisión conjunta del paper antes de entregar.
- [ ] Preparar respuestas sobre datos, modelos, evaluación y decisiones para la ronda de preguntas.
