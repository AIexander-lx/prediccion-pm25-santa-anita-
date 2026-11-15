"""Experimento reproducible del rol 3. Ejecutar desde la raíz: python scripts/05_modelos_no_lineales.py.

Requiere haber ejecutado antes 01_construir_dataset.py y 04_modelos_lineales.py.

Mismo protocolo que el rol 2 (sección 6 del paper):

* Búsqueda de hiperparámetros solo con entrenamiento y los mismos tres cortes
  de origen expansivo por fecha de la respuesta (se comprueba contra
  ``lineales_folds.csv``). Criterio: MAE medio de las tres ventanas.
* Cada variante (con y sin calendario) se reajusta con todo el entrenamiento y
  se evalúa en validación. En cada familia (Random Forest, HistGradientBoosting)
  se elige la variante con menor MAE de validación.
* El elegido de cada familia se evalúa en prueba sin reajustar con validación.
  Prueba no se usa para elegir hiperparámetros, variantes ni familia.
* Importancia por permutación sobre validación, por variable y por grupo.
"""
from pathlib import Path
import sys
import platform
import time
import warnings

import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pm25.features import (COLS_CALENDARIO, COLS_HISTORIAL, OBJETIVO,  # noqa: E402
                           columnas_modelo, crear_preprocesador)

OUT = ROOT / "data/processed"
SEMILLA = 42
# Mismos cortes que scripts/04_modelos_lineales.py (validación interna por fecha de respuesta).
CORTES = [("2022-07-01", "2022-10-01"), ("2022-10-01", "2023-01-01"), ("2023-01-01", "2023-04-01")]

FAMILIAS = {
    "RandomForest": (
        lambda: RandomForestRegressor(random_state=SEMILLA, n_jobs=-1),
        {"modelo__n_estimators": [200, 500],
         "modelo__max_features": [0.33, 0.6, 1.0],
         "modelo__min_samples_leaf": [1, 5, 20, 50, 100]},
    ),
    "HistGB": (
        # Sin parada temprana: su partición interna sería aleatoria, no temporal.
        lambda: HistGradientBoostingRegressor(random_state=SEMILLA, early_stopping=False),
        {"modelo__learning_rate": [0.02, 0.05, 0.1],
         "modelo__max_iter": [50, 100, 300, 600],
         "modelo__max_leaf_nodes": [7, 15, 31],
         "modelo__min_samples_leaf": [20, 100, 300],
         "modelo__l2_regularization": [0.0, 1.0]},
    ),
}
GRUPOS = {"historial": list(COLS_HISTORIAL), "calendario": list(COLS_CALENDARIO)}
N_REPETICIONES = 20


def metricas(y, pred):
    mse = mean_squared_error(y, pred)
    return {"MAE": mean_absolute_error(y, pred), "RMSE": np.sqrt(mse),
            "MSE": mse, "R2": r2_score(y, pred)}


def cargar_bloques():
    bloques = {n: pd.read_csv(OUT / f"supervisado_{n}.csv", parse_dates=["fecha_hora", "instante_objetivo"])
               .sort_values("instante_objetivo").reset_index(drop=True) for n in ("train", "val", "test")}
    for nombre, datos in bloques.items():
        if datos.empty or datos.instante_objetivo.duplicated().any() or datos[OBJETIVO].isna().any():
            raise ValueError(f"Partición {nombre} vacía, con fechas duplicadas o respuestas faltantes")
    tr, val, test = (bloques[n] for n in ("train", "val", "test"))
    if not (tr.instante_objetivo.max() < val.instante_objetivo.min()
            and val.instante_objetivo.max() < test.instante_objetivo.min()):
        raise ValueError("Las particiones no están ordenadas cronológicamente")
    return tr, val, test


def folds_temporales(fechas):
    cv = [(np.flatnonzero(fechas < a), np.flatnonzero((fechas >= a) & (fechas < b))) for a, b in CORTES]
    assert all(len(i) and len(j) and fechas.iloc[i].max() < fechas.iloc[j].min() for i, j in cv)
    # Deben coincidir con los del rol 2 para que la búsqueda sea comparable.
    ref = pd.read_csv(OUT / "lineales_folds.csv")
    if [(len(i), len(j)) for i, j in cv] != list(zip(ref.n_train, ref.n_val)):
        raise ValueError("Los folds no coinciden con lineales_folds.csv")
    return cv


def permutacion(modelo, datos, cols, columnas_a_permutar, rng):
    """Aumento del MAE al permutar conjuntamente ``columnas_a_permutar`` (misma permutación de filas)."""
    base = mean_absolute_error(datos[OBJETIVO], modelo.predict(datos[cols]))
    aumentos = []
    for _ in range(N_REPETICIONES):
        X = datos[cols].copy()
        orden = rng.permutation(len(X))
        X[columnas_a_permutar] = X[columnas_a_permutar].to_numpy()[orden]
        aumentos.append(mean_absolute_error(datos[OBJETIVO], modelo.predict(X)) - base)
    return np.mean(aumentos), np.std(aumentos)


def main():
    # Aviso interno de joblib al anidar el paralelismo del bosque dentro de GridSearchCV; no afecta resultados.
    warnings.filterwarnings("ignore", message=".*sklearn.utils.parallel.delayed.*")
    tr, val, test = cargar_bloques()
    cv = folds_temporales(tr.instante_objetivo)
    resultados, busquedas, predicciones, importancias, modelos = [], [], [], [], {}

    def evaluar(nombre, bloque, datos, pred, params=None):
        resultados.append({"modelo": nombre, "bloque": bloque, "hiperparametros": params,
                           "n": len(datos), **metricas(datos[OBJETIVO], pred)})
        predicciones.extend({"modelo": nombre, "bloque": bloque, "instante_objetivo": t, "real": y, "prediccion": p}
                            for t, y, p in zip(datos.instante_objetivo, datos[OBJETIVO], pred))

    for familia, (fabrica, malla) in FAMILIAS.items():
        for calendario in (False, True):
            etiqueta = f"{familia}_{'con' if calendario else 'sin'}_calendario"
            cols = columnas_modelo(calendario)
            # El escalado del historial no altera los cortes de un árbol; se conserva el mismo
            # preprocesador que en los lineales para que las entradas sean idénticas.
            pipe = Pipeline([("prep", crear_preprocesador(calendario)), ("modelo", fabrica())])
            grid = GridSearchCV(pipe, malla, cv=cv, scoring="neg_mean_absolute_error", refit=True,
                                n_jobs=1, error_score="raise", return_train_score=False)
            t0 = time.time()
            grid.fit(tr[cols], tr[OBJETIVO])
            print(f"{etiqueta}: {len(grid.cv_results_['params'])} combinaciones en {time.time() - t0:.0f} s")
            for i, params in enumerate(grid.cv_results_["params"]):
                fila = {"modelo": etiqueta, **{k.replace("modelo__", ""): v for k, v in params.items()},
                        "mae_cv_medio": -grid.cv_results_["mean_test_score"][i],
                        "mae_cv_desv": grid.cv_results_["std_test_score"][i],
                        "rango": grid.cv_results_["rank_test_score"][i]}
                fila.update({f"mae_fold_{j+1}": -grid.cv_results_[f"split{j}_test_score"][i] for j in range(len(cv))})
                busquedas.append(fila)
            mejores = {k.replace("modelo__", ""): v for k, v in grid.best_params_.items()}
            modelos[etiqueta] = (grid.best_estimator_, cols, mejores)
            evaluar(etiqueta, "validacion", val, grid.best_estimator_.predict(val[cols]), str(mejores))

    # Elección dentro de cada familia por MAE de validación; prueba solo evalúa.
    elegidos = {}
    for familia in FAMILIAS:
        candidatos = [r for r in resultados if r["modelo"].startswith(familia) and r["bloque"] == "validacion"]
        elegidos[familia] = min(candidatos, key=lambda r: r["MAE"])["modelo"]
    for familia, etiqueta in elegidos.items():
        modelo, cols, params = modelos[etiqueta]
        evaluar(etiqueta, "prueba", test, modelo.predict(test[cols]), str(params))

    # Importancia por permutación en validación (no en prueba) para los elegidos.
    rng = np.random.default_rng(SEMILLA)
    for etiqueta in elegidos.values():
        modelo, cols, _ = modelos[etiqueta]
        for variable in cols:
            media, desv = permutacion(modelo, val, cols, [variable], rng)
            importancias.append({"modelo": etiqueta, "tipo": "permutacion_variable", "variable": variable,
                                 "aumento_mae": media, "desv": desv})
        for grupo, columnas in GRUPOS.items():
            if set(columnas) <= set(cols):
                media, desv = permutacion(modelo, val, cols, columnas, rng)
                importancias.append({"modelo": etiqueta, "tipo": "permutacion_grupo", "variable": grupo,
                                     "aumento_mae": media, "desv": desv})
        if etiqueta.startswith("RandomForest"):
            # Importancia por impureza (MDI), calculada en entrenamiento: sesgada hacia variables
            # continuas y repartida entre variables correlacionadas; se reporta solo como contraste.
            nombres = modelo.named_steps["prep"].get_feature_names_out()
            for variable, valor in zip(nombres, modelo.named_steps["modelo"].feature_importances_):
                importancias.append({"modelo": etiqueta, "tipo": "impureza_entrenamiento", "variable": variable,
                                     "aumento_mae": valor, "desv": np.nan})

    for nombre, filas in (("no_lineales_metricas.csv", resultados), ("no_lineales_busqueda.csv", busquedas),
                          ("no_lineales_predicciones.csv", predicciones),
                          ("no_lineales_importancia.csv", importancias)):
        pd.DataFrame(filas).to_csv(OUT / nombre, index=False, float_format="%.8f")
    pd.DataFrame([{"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__,
                   "scikit_learn": sklearn.__version__, "semilla": SEMILLA,
                   **{f"seleccion_{f}": e for f, e in elegidos.items()}}]).to_csv(OUT / "no_lineales_entorno.csv", index=False)
    print(pd.DataFrame(resultados).drop(columns="hiperparametros").to_string(index=False))
    print("Elegidos por MAE de validación:", elegidos)


if __name__ == "__main__":
    main()
