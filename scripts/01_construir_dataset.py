"""Construye el conjunto supervisado PM2.5(t+1) y lo guarda por partición.

Uso (desde la raíz del repositorio):
    python scripts/01_construir_dataset.py

Salidas en data/processed/:
    supervisado_train.csv, supervisado_val.csv, supervisado_test.csv
    resumen_perdida_filas.csv   (cuántas filas se pierden y por qué)
    resumen_particiones.csv     (tamaño y estadísticos por bloque)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd  # noqa: E402

from pm25.features import (COLS_CALENDARIO, COLS_HISTORIAL, OBJETIVO,  # noqa: E402
                           PARTICIONES, preparar_dataset)

CSV = ROOT / "data/raw/santa_anita_2015_2024.csv"
OUT = ROOT / "data/processed"
OUT.mkdir(parents=True, exist_ok=True)

D, resumen = preparar_dataset(CSV)
resumen.round(3).to_csv(OUT / "resumen_perdida_filas.csv", index_label="concepto")
print(resumen.round(2).to_string(), "\n")

cols = COLS_HISTORIAL + COLS_CALENDARIO + ["instante_objetivo", OBJETIVO]
filas = []
for nombre, (a, b) in PARTICIONES.items():
    parte = D.loc[D["particion"] == nombre, cols]
    parte.to_csv(OUT / f"supervisado_{nombre}.csv", index_label="fecha_hora")
    y = parte[OBJETIVO]
    filas.append({"particion": nombre, "desde_respuesta": a, "hasta_respuesta": b,
                  "filas": len(parte), "media": y.mean(), "mediana": y.median(),
                  "p95": y.quantile(0.95), "maximo": y.max()})
tabla = pd.DataFrame(filas).set_index("particion")
num = ["filas", "media", "mediana", "p95", "maximo"]
tabla[num] = tabla[num].round(3)
tabla.to_csv(OUT / "resumen_particiones.csv")
print(tabla.to_string())
