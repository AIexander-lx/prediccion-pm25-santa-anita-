"""Experimento reproducible del rol 2. Ejecutar desde la raíz: python scripts/04_modelos_lineales.py.

La búsqueda usa exclusivamente entrenamiento y tres cortes por fecha de origen
expansivo. Validación compara variantes; prueba se reserva para el modelo
elegido por MAE de validación y la persistencia, sin reajustar con validación.
"""
from pathlib import Path
import sys
import warnings
import platform

import numpy as np
import pandas as pd
import sklearn
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import Lasso, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pm25.features import OBJETIVO, columnas_modelo, crear_preprocesador  # noqa: E402

OUT = ROOT / "data/processed"
ALPHAS = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]


def metricas(y, pred):
    mse = mean_squared_error(y, pred)
    return {"MAE": mean_absolute_error(y, pred), "RMSE": np.sqrt(mse),
            "MSE": mse, "R2": r2_score(y, pred)}


def main():
    bloques = {n: pd.read_csv(OUT / f"supervisado_{n}.csv", parse_dates=["fecha_hora", "instante_objetivo"]).sort_values("instante_objetivo").reset_index(drop=True)
               for n in ("train", "val", "test")}
    tr, val, test = (bloques[n] for n in ("train", "val", "test"))
    for nombre, datos in bloques.items():
        if datos.empty or datos.instante_objetivo.duplicated().any() or datos[OBJETIVO].isna().any():
            raise ValueError(f"Partición {nombre} vacía, con fechas duplicadas o respuestas faltantes")
    if not (tr.instante_objetivo.max() < val.instante_objetivo.min()
            and val.instante_objetivo.max() < test.instante_objetivo.min()):
        raise ValueError("Las particiones no están ordenadas cronológicamente")
    # Fechas de respuesta, no número de filas: los huecos no cambian los cortes.
    fechas = tr.instante_objetivo
    cortes = [("2022-07-01", "2022-10-01"), ("2022-10-01", "2023-01-01"),
              ("2023-01-01", "2023-04-01")]
    cv = [(np.flatnonzero(fechas < inicio), np.flatnonzero((fechas >= inicio) & (fechas < fin)))
          for inicio, fin in cortes]
    assert all(len(a) and len(b) and fechas.iloc[a].max() < fechas.iloc[b].min() for a, b in cv)
    pd.DataFrame([{"fold": i + 1, "train_desde": fechas.iloc[a].min(), "train_hasta": fechas.iloc[a].max(),
                   "val_desde": fechas.iloc[b].min(), "val_hasta": fechas.iloc[b].max(),
                   "n_train": len(a), "n_val": len(b)} for i, (a, b) in enumerate(cv)]).to_csv(OUT / "lineales_folds.csv", index=False)
    resultados, busquedas, coeficientes, predicciones, modelos = [], [], [], [], {}

    def evaluar(nombre, bloque, datos, pred, alpha=None):
        resultados.append({"modelo": nombre, "bloque": bloque, "alpha": alpha, "n": len(datos), **metricas(datos[OBJETIVO], pred)})
        predicciones.extend({"modelo": nombre, "bloque": bloque, "instante_objetivo": t, "real": y, "prediccion": p}
                            for t, y, p in zip(datos.instante_objetivo, datos[OBJETIVO], pred))

    evaluar("Persistencia", "validacion", val, val.pm25_t)
    for nombre, clase in (("Ridge", Ridge), ("Lasso", Lasso)):
        for calendario in (False, True):
            etiqueta = f"{nombre}_{'con' if calendario else 'sin'}_calendario"
            cols = columnas_modelo(calendario)
            modelo = clase(max_iter=100000, tol=1e-5) if nombre == "Lasso" else clase()
            pipe = Pipeline([("prep", crear_preprocesador(calendario)), ("modelo", modelo)])
            grid = GridSearchCV(pipe, {"modelo__alpha": ALPHAS}, cv=cv, scoring="neg_mean_absolute_error", refit=True, n_jobs=1, error_score="raise", return_train_score=False)
            with warnings.catch_warnings():
                warnings.simplefilter("error", ConvergenceWarning)
                grid.fit(tr[cols], tr[OBJETIVO])
            for i, alpha in enumerate(ALPHAS):
                fila = {"modelo": etiqueta, "alpha": alpha, "mae_cv_medio": -grid.cv_results_["mean_test_score"][i], "mae_cv_desv": grid.cv_results_["std_test_score"][i]}
                fila.update({f"mae_fold_{j+1}": -grid.cv_results_[f"split{j}_test_score"][i] for j in range(len(cv))})
                busquedas.append(fila)
            best = grid.best_estimator_
            modelos[etiqueta] = (best, cols, grid.best_params_["modelo__alpha"])
            evaluar(etiqueta, "validacion", val, best.predict(val[cols]), grid.best_params_["modelo__alpha"])
            nombres = best.named_steps["prep"].get_feature_names_out()
            for variable, valor in zip(nombres, best.named_steps["modelo"].coef_):
                coeficientes.append({"modelo": etiqueta, "variable": variable, "coeficiente": valor, "cero": bool(abs(valor) < 1e-10)})
    # Elegir entre los cuatro modelos lineales por MAE de validación; también
    # comparar persistencia, sin usar prueba para escoger ni reajustar.
    candidatos = [r for r in resultados if r["modelo"] != "Persistencia"]
    elegido = min(candidatos, key=lambda r: r["MAE"])["modelo"]
    modelo, cols, alpha = modelos[elegido]
    evaluar("Persistencia", "prueba", test, test.pm25_t)
    evaluar(elegido, "prueba", test, modelo.predict(test[cols]), alpha)
    for nombre, filas in (("lineales_metricas.csv", resultados), ("lineales_busqueda.csv", busquedas),
                          ("lineales_coeficientes.csv", coeficientes), ("lineales_predicciones.csv", predicciones)):
        pd.DataFrame(filas).to_csv(OUT / nombre, index=False, float_format="%.8f")
    pd.DataFrame([{"python": platform.python_version(), "numpy": np.__version__,
                   "pandas": pd.__version__, "scikit_learn": sklearn.__version__,
                   "seleccion_validacion": elegido}]).to_csv(OUT / "lineales_entorno.csv", index=False)
    print(pd.DataFrame(resultados).to_string(index=False))
    print(f"Modelo lineal elegido por MAE de validación: {elegido}")


if __name__ == "__main__":
    main()
