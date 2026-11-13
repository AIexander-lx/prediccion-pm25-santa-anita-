"""Comprobaciones explícitas de ausencia de fuga de información (data leakage).

Uso (desde la raíz del repositorio):
    python scripts/02_verificar_fuga.py

Escribe data/processed/verificacion_fuga.csv y termina con código distinto de
cero si alguna comprobación falla.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.pipeline import Pipeline  # noqa: E402
from sklearn.linear_model import Ridge  # noqa: E402

from pm25.features import (COLS_CALENDARIO, COLS_HISTORIAL, OBJETIVO,  # noqa: E402
                           PARTICIONES, REZAGOS, VENTANAS, cargar_serie,
                           columnas_modelo, construir_matriz, crear_preprocesador,
                           filtrar_casos_completos, preparar_dataset)

CSV = ROOT / "data/raw/santa_anita_2015_2024.csv"
OUT = ROOT / "data/processed"
rng = np.random.default_rng(42)
resultados = []


def registrar(nombre, ok, detalle):
    resultados.append({"comprobacion": nombre, "resultado": "OK" if ok else "FALLA",
                       "detalle": detalle})
    print(f"[{'OK' if ok else 'FALLA'}] {nombre}: {detalle}")


s = cargar_serie(CSV)
X_full = construir_matriz(s)
D, _ = preparar_dataset(CSV)
cols_ent = COLS_HISTORIAL

# 1. Recalculo independiente, fila a fila, usando solo valores en t o antes -----
muestra = rng.choice(D.index, size=500, replace=False)
errores = 0
for t in muestra:
    i = s.index.get_loc(t)
    pasado = s.iloc[: i + 1].to_numpy()                 # nada posterior a t
    esperado = {"pm25_t": pasado[-1]}
    for k in REZAGOS:
        esperado[f"pm25_lag{k}"] = pasado[-1 - k]
    for w in VENTANAS:
        esperado[f"pm25_media{w}h"] = pasado[-w:].mean()
    for c, v in esperado.items():
        if not np.isclose(D.loc[t, c], v, rtol=0, atol=1e-9):
            errores += 1
registrar("Recálculo independiente con solo el pasado (500 filas al azar)",
          errores == 0, f"{errores} discrepancias en {500 * len(cols_ent)} valores")

# 2. Invariancia ante el futuro: alterar todo lo posterior a T no cambia nada ------
fallas = 0
cortes = rng.choice(s.index[200:-200], size=8, replace=False)
for T in cortes:
    s_alt = s.copy()
    s_alt.loc[s_alt.index > T] = s_alt.loc[s_alt.index > T] * 1000 + 777   # futuro absurdo
    A = construir_matriz(s_alt).loc[:T, cols_ent + COLS_CALENDARIO]
    B = X_full.loc[:T, cols_ent + COLS_CALENDARIO]
    if not A.equals(B):
        fallas += 1
registrar("Las entradas en t no cambian si se altera el futuro (8 cortes)",
          fallas == 0, f"{fallas} cortes con diferencias")

# 3. La respuesta es exactamente la medición una hora después ----------------------
ok_y = np.allclose(D[OBJETIVO].to_numpy(), s.shift(-1).loc[D.index].to_numpy())
ok_dt = (D["instante_objetivo"] - D.index == pd.Timedelta(hours=1)).all()
registrar("Respuesta = PM2.5(t+1) con separación exacta de 1 hora", bool(ok_y and ok_dt),
          "valores y fechas coinciden en todas las filas")

# 4. Entradas del calendario corresponden a t+1, no a t ---------------------------
ok_cal = ((D["hora_objetivo"] == D["instante_objetivo"].dt.hour).all()
          and (D["dia_semana_objetivo"] == D["instante_objetivo"].dt.dayofweek).all())
registrar("Hora y día de la semana corresponden al instante pronosticado (t+1)",
          bool(ok_cal), "coinciden en todas las filas")

# 5. Particiones: completas, disjuntas, cronológicas, por instante de la respuesta --
sin_part = int(D["particion"].isna().sum())
bloques = {n: D[D["particion"] == n] for n in PARTICIONES}
orden_ok = (bloques["train"]["instante_objetivo"].max() < bloques["val"]["instante_objetivo"].min()
            and bloques["val"]["instante_objetivo"].max() < bloques["test"]["instante_objetivo"].min())
solapes = len(set(bloques["train"].index) & set(bloques["val"].index)) \
    + len(set(bloques["val"].index) & set(bloques["test"].index)) \
    + len(set(bloques["train"].index) & set(bloques["test"].index))
dentro = all(b["instante_objetivo"].between(*PARTICIONES[n]).all() for n, b in bloques.items())
registrar("Partición cronológica sin filas sin asignar, sin solapes y en orden",
          sin_part == 0 and orden_ok and solapes == 0 and dentro,
          f"sin asignar={sin_part}, solapes={solapes}, orden={orden_ok}")

# 6. Ninguna entrada o respuesta con tiempo posterior al bloque de la fila ---------
ok_sup = all((b.index.max() < pd.Timestamp(PARTICIONES[n][1])) for n, b in bloques.items())
registrar("Ninguna fila usa información posterior al final de su bloque",
          bool(ok_sup), "el último t de cada bloque es anterior a su corte")

# 7. Sin imputación: sin NaN/inf, y los ceros coinciden con los del archivo --------
sin_nan = not D[cols_ent + [OBJETIVO]].isna().any().any()
finito = bool(np.isfinite(D[cols_ent + [OBJETIVO]].to_numpy()).all())
ceros_raw = int((s == 0).sum())
ceros_ds = int((D["pm25_t"] == 0).sum())
registrar("Sin NaN ni infinitos, y sin ceros inventados", sin_nan and finito and ceros_raw == ceros_ds,
          f"ceros en la serie={ceros_raw}, ceros en pm25_t={ceros_ds}")

# 8. Un hueco en la ventana excluye la fila (no se rellena) ------------------------
hay_hueco = X_full[cols_ent].isna().any(axis=1) | X_full[OBJETIVO].isna()
excluidas = X_full.index.difference(D.index)
ok_huecos = set(X_full.index[hay_hueco]) == set(excluidas)
registrar("Toda fila con hueco en entradas o respuesta queda excluida, y solo esas",
          ok_huecos, f"{len(excluidas)} filas excluidas = {int(hay_hueco.sum())} con hueco")

# 9. El preprocesamiento se ajusta solo con entrenamiento --------------------------
for con_cal in (False, True):
    cols = columnas_modelo(con_cal)
    tr, va, te = (bloques[n] for n in ("train", "val", "test"))
    pipe = Pipeline([("prep", crear_preprocesador(con_cal)), ("modelo", Ridge(alpha=1.0))])
    pipe.fit(tr[cols], tr[OBJETIVO])
    esc = pipe.named_steps["prep"].named_transformers_["historial"]
    media_tr = tr[COLS_HISTORIAL].mean().to_numpy()
    media_todo = D[COLS_HISTORIAL].mean().to_numpy()
    ok_tr = np.allclose(esc.mean_, media_tr)
    difiere = not np.allclose(esc.mean_, media_todo)
    antes = esc.mean_.copy()
    pipe.predict(va[cols]); pipe.predict(te[cols])             # predecir no reajusta
    ok_fijo = np.allclose(antes, esc.mean_)
    X_va = pipe.named_steps["prep"].transform(va[cols])
    registrar(f"Escalador ajustado solo con entrenamiento (calendario={con_cal})",
              ok_tr and difiere and ok_fijo and np.isfinite(X_va).all(),
              f"media pm25_t entrenamiento={esc.mean_[0]:.3f}, con todo={media_todo[0]:.3f}")

# 10. Forma del calendario codificado -------------------------------------------------
prep = crear_preprocesador(True).fit(bloques["train"][columnas_modelo(True)])
nombres = list(prep.get_feature_names_out())
registrar("Codificación del calendario: 9 de historial + 2 (hora) + 6 (día) = 17 columnas",
          len(nombres) == 17, ", ".join(nombres))

# 11. Control negativo: la prueba 2 debe detectar una fuga deliberada ---------------------
def matriz_con_fuga(serie):
    M = construir_matriz(serie)
    M["fuga_pm25_t_mas1"] = serie.shift(-1)       # información del futuro a propósito
    return M

T = cortes[0]
s_alt = s.copy()
s_alt.loc[s_alt.index > T] = s_alt.loc[s_alt.index > T] * 1000 + 777
col = ["fuga_pm25_t_mas1"]
detecta = not matriz_con_fuga(s_alt).loc[:T, col].equals(matriz_con_fuga(s).loc[:T, col])
registrar("Control negativo: una entrada con fuga deliberada sí es detectada por la prueba 2",
          detecta, "la columna con shift(-1) cambia al alterar el futuro")

res = pd.DataFrame(resultados)
res.to_csv(OUT / "verificacion_fuga.csv", index=False)
fallos = int((res["resultado"] == "FALLA").sum())
print(f"\n{len(res) - fallos} de {len(res)} comprobaciones OK")
sys.exit(1 if fallos else 0)
