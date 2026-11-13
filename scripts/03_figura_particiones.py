"""Figura de la partición cronológica sobre la serie (para la sección 4 del paper).

Uso: python scripts/03_figura_particiones.py
Salida: figures/14_particiones_cronologicas.{png,pdf}
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

from pm25.features import OBJETIVO, PARTICIONES, cargar_serie, preparar_dataset  # noqa: E402

plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "savefig.facecolor": "white"})
CSV = ROOT / "data/raw/santa_anita_2015_2024.csv"
s = cargar_serie(CSV)
D, _ = preparar_dataset(CSV)
dia = s.resample("D").agg(["mean", "count"])
dia = dia[dia["count"] >= 18]["mean"]          # mismo criterio de 18 de 24 horas del EDA
colores = {"train": "#9ecae1", "val": "#fdd0a2", "test": "#c7e9c0"}
nombres = {"train": "Entrenamiento", "val": "Validación", "test": "Prueba"}

fig, ax = plt.subplots(figsize=(7.2, 2.6))
for n, (a, b) in PARTICIONES.items():
    ax.axvspan(a, b, color=colores[n], alpha=0.6, lw=0)
    media = D.loc[D["particion"] == n, OBJETIVO].mean()      # media de la respuesta del bloque
    ax.text(a + (b - a) / 2, 0.97, f"{nombres[n]}\nmedia {media:.1f}".replace(".", ","),
            ha="center", va="top",
            transform=ax.get_xaxis_transform(), fontsize=8)
ax.plot(dia.index, dia.values, color="#08306b", lw=0.7)
ax.set_ylabel("PM2.5 media diaria (µg/m³)")
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1, 4, 7, 10)))
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: (lambda d: f"{MESES[d.month - 1]} {d.year}")(mdates.num2date(x))))
ax.set_xlim(s.index.min(), s.index.max())
fig.tight_layout()
(ROOT / "figures").mkdir(exist_ok=True)
fig.savefig(ROOT / "figures/14_particiones_cronologicas.png", dpi=300)
fig.savefig(ROOT / "figures/14_particiones_cronologicas.pdf")
print("listo")
