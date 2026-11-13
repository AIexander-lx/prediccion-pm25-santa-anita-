"""Construcción del conjunto supervisado para predecir PM2.5(t+1).

Convenciones (fijadas en el EDA, secciones 8 y 9):

* La rejilla es horaria y completa entre INICIO y FIN; las horas sin medición
  quedan como NaN. No se imputa ni se interpola nada.
* Cada fila representa el instante ``t`` en que se hace el pronóstico. Solo usa
  mediciones de PM2.5 en ``t`` y antes. La respuesta es ``PM2.5(t+1)``.
* Una fila solo se conserva si tiene la respuesta y *todas* las entradas de
  historial completas (casos completos). El costo en filas se cuantifica en
  ``resumen_perdida_filas``.
* La partición cronológica se define por el instante de la **respuesta** (t+1),
  de modo que ninguna etiqueta de entrenamiento cae en el periodo de
  validación y ninguna de validación cae en el de prueba.
* La hora del día y el día de la semana se guardan como enteros del instante
  que se pronostica (t+1), que se conocen de antemano. Su codificación
  (seno/coseno y variables indicadoras) se hace dentro del pipeline.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

INICIO = pd.Timestamp("2022-01-01 00:00")
FIN = pd.Timestamp("2024-04-30 23:00")

REZAGOS = (1, 3, 6, 12, 24)          # PM2.5(t-k), en horas
VENTANAS = (3, 6, 24)                # medias móviles finales (incluyen t)

# Bloques por instante de la respuesta (t+1), inclusivos.
PARTICIONES = {
    "train": (pd.Timestamp("2022-01-01 00:00"), pd.Timestamp("2023-06-30 23:00")),
    "val": (pd.Timestamp("2023-07-01 00:00"), pd.Timestamp("2023-12-31 23:00")),
    "test": (pd.Timestamp("2024-01-01 00:00"), pd.Timestamp("2024-04-30 23:00")),
}

COLS_HISTORIAL = (
    ["pm25_t"]
    + [f"pm25_lag{k}" for k in REZAGOS]
    + [f"pm25_media{w}h" for w in VENTANAS]
)
COLS_CALENDARIO = ["hora_objetivo", "dia_semana_objetivo"]
OBJETIVO = "y_pm25_t1"


def cargar_serie(csv: Path) -> pd.Series:
    """Serie horaria de PM2.5 sobre la rejilla completa [INICIO, FIN]."""
    raw = pd.read_csv(csv, dtype={"FECHA": str, "HORA": str})
    raw["fecha_hora"] = pd.to_datetime(
        raw["FECHA"] + raw["HORA"].str.zfill(6), format="%Y%m%d%H%M%S"
    )
    periodo = raw.loc[raw["fecha_hora"].between(INICIO, FIN)]
    if periodo["fecha_hora"].duplicated().any():
        raise ValueError("Hay horas duplicadas en el periodo de estudio.")
    rejilla = pd.date_range(INICIO, FIN, freq="h", name="fecha_hora")
    return periodo.set_index("fecha_hora")["PM2_5"].reindex(rejilla).astype(float)


def construir_matriz(s: pd.Series) -> pd.DataFrame:
    """Matriz supervisada completa (incluye filas con NaN, aún sin filtrar).

    Todas las entradas se calculan con ``shift`` hacia atrás o ventanas finales,
    por lo que la fila ``t`` nunca contiene información posterior a ``t``.
    """
    X = pd.DataFrame(index=s.index)
    X["pm25_t"] = s
    for k in REZAGOS:
        X[f"pm25_lag{k}"] = s.shift(k)
    for w in VENTANAS:
        # min_periods=w: se exige la ventana completa; con un hueco queda NaN.
        X[f"pm25_media{w}h"] = s.rolling(w, min_periods=w).mean()
    objetivo = s.index + pd.Timedelta(hours=1)
    X["hora_objetivo"] = objetivo.hour
    X["dia_semana_objetivo"] = objetivo.dayofweek      # 0 = lunes
    X["instante_objetivo"] = objetivo
    X[OBJETIVO] = s.shift(-1)
    return X


def filtrar_casos_completos(X: pd.DataFrame) -> pd.DataFrame:
    """Conserva solo filas con respuesta y todas las entradas disponibles.

    La respuesta de la última hora del periodo (t = FIN) no existe y se descarta.
    """
    return X.dropna(subset=COLS_HISTORIAL + [OBJETIVO])


def asignar_particion(X: pd.DataFrame) -> pd.Series:
    """Etiqueta cada fila con su bloque según el instante de la respuesta."""
    part = pd.Series(pd.NA, index=X.index, dtype="object")
    for nombre, (a, b) in PARTICIONES.items():
        part[X["instante_objetivo"].between(a, b)] = nombre
    return part


def resumen_perdida_filas(X: pd.DataFrame) -> pd.DataFrame:
    """Cuántas filas se pierden y por qué, en orden de aplicación de los filtros."""
    total = len(X)
    sin_respuesta = X[OBJETIVO].isna()
    sin_actual = X["pm25_t"].isna()
    hueco_rezagos = X[[f"pm25_lag{k}" for k in REZAGOS]].isna().any(axis=1)
    hueco_medias = X[[f"pm25_media{w}h" for w in VENTANAS]].isna().any(axis=1)
    util = ~(sin_respuesta | X[COLS_HISTORIAL].isna().any(axis=1))
    filas = {
        "Instantes t en la rejilla": total,
        "Sin respuesta PM2.5(t+1)": int(sin_respuesta.sum()),
        "Sin medición actual PM2.5(t)": int(sin_actual.sum()),
        "Con algún rezago faltante (1,3,6,12,24)": int(hueco_rezagos.sum()),
        "Con alguna media móvil incompleta": int(hueco_medias.sum()),
        "Filas utilizables (casos completos)": int(util.sum()),
    }
    out = pd.DataFrame({"filas": filas})
    out["porcentaje_de_la_rejilla"] = 100 * out["filas"] / total
    return out


def preparar_dataset(csv: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Devuelve (dataset utilizable con columna ``particion``, resumen de pérdida)."""
    X = construir_matriz(cargar_serie(csv))
    resumen = resumen_perdida_filas(X)
    D = filtrar_casos_completos(X).copy()
    D["particion"] = asignar_particion(D)
    return D, resumen


# ---------------------------------------------------------------------------
# Preprocesamiento dentro de un pipeline (se ajusta solo con entrenamiento)
# ---------------------------------------------------------------------------

def _ciclico(periodo: int):
    """Transformador seno/coseno para una variable entera cíclica."""
    from sklearn.preprocessing import FunctionTransformer

    def f(x):
        ang = 2 * np.pi * np.asarray(x, dtype=float) / periodo
        return np.column_stack([np.sin(ang), np.cos(ang)])

    return FunctionTransformer(f, feature_names_out=lambda _t, cols: [
        f"{cols[0]}_sin", f"{cols[0]}_cos"])


def crear_preprocesador(con_calendario: bool = True):
    """ColumnTransformer: escala el historial y codifica el calendario.

    * Historial (9 variables de PM2.5): ``StandardScaler``.
    * Hora (24): seno y coseno, para que 23 h y 0 h queden vecinas.
    * Día de la semana: variables indicadoras (el efecto de fin de semana no es
      una senoide), con la primera categoría como referencia.

    Debe usarse como primer paso de un ``Pipeline`` y ajustarse únicamente con
    el conjunto de entrenamiento (``pipeline.fit(X_train, y_train)``).
    """
    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    bloques = [("historial", StandardScaler(), list(COLS_HISTORIAL))]
    if con_calendario:
        bloques += [
            ("hora", _ciclico(24), ["hora_objetivo"]),
            ("dia", OneHotEncoder(drop="first", categories=[list(range(7))],
                                  sparse_output=False), ["dia_semana_objetivo"]),
        ]
    return ColumnTransformer(bloques, verbose_feature_names_out=False)


def columnas_modelo(con_calendario: bool = True) -> list[str]:
    """Columnas de entrada que consume el preprocesador."""
    return list(COLS_HISTORIAL) + (list(COLS_CALENDARIO) if con_calendario else [])
