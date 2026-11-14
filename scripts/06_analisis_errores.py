"""Análisis de errores y régimen de concentraciones altas (rol 3).

Uso (desde la raíz, después de 04_modelos_lineales.py y 05_modelos_no_lineales.py):
    python scripts/06_analisis_errores.py

Compara, sobre las mismas filas de validación y prueba, la persistencia, el modelo
lineal elegido por el rol 2 y el mejor Random Forest y HistGradientBoosting
elegidos en validación. No reentrena nada: solo lee las predicciones guardadas.

Salidas en data/processed/ (prefijo ``errores_``) y figuras 15 a 18 en figures/.
"""
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pm25.features import OBJETIVO  # noqa: E402

OUT = ROOT / "data/processed"
FIG = ROOT / "figures"
SEMILLA = 42
B = 2000                 # réplicas bootstrap
BLOQUE = 24              # longitud del bloque móvil (filas consecutivas, ≈ un día)
# Cortes de referencia en µg/m³: guía OMS 24 h (15) y metas intermedias (25, 37,5, 50, 75);
# 50 coincide con el ECA peruano diario. Se usan solo para agrupar horas, no como superación.
NIVELES = [0, 15, 25, 37.5, 50, 75, np.inf]
ETIQ_NIVELES = ["<15", "15–25", "25–37,5", "37,5–50", "50–75", "≥75"]
BLOQUES = {"validacion": "Validación (jul–dic 2023)", "prueba": "Prueba (ene–abr 2024)"}

plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False,
                     "savefig.facecolor": "white", "axes.grid": True, "grid.color": "#e6e6e6",
                     "grid.linewidth": 0.5, "axes.axisbelow": True, "legend.frameon": False})
# Paleta categórica validada (orden fijo); la persistencia, como referencia, va en gris.
COLOR = {"Persistencia": "#8c8c8c", "Ridge": "#2a78d6", "Random Forest": "#eb6834", "HistGB": "#1baf7a"}
MARCA = {"Persistencia": "s", "Ridge": "o", "Random Forest": "^", "HistGB": "D"}
NOMBRE_VAR = {"pm25_t": "PM2.5(t)", "hora_objetivo": "hora (t+1)", "dia_semana_objetivo": "día semana (t+1)",
              **{f"pm25_lag{k}": f"rezago {k} h" for k in (1, 3, 6, 12, 24)},
              **{f"pm25_media{w}h": f"media {w} h" for w in (3, 6, 24)}}
LINEA = {"Persistencia": ":", "Ridge": "-", "Random Forest": "-", "HistGB": "--"}


def coma(x, dec=2):
    return f"{x:.{dec}f}".replace(".", ",")


def cargar_predicciones():
    """Tabla ancha por bloque: una fila por instante, una columna por modelo."""
    lin = pd.read_csv(OUT / "lineales_predicciones.csv", parse_dates=["instante_objetivo"])
    nl = pd.read_csv(OUT / "no_lineales_predicciones.csv", parse_dates=["instante_objetivo"])
    ent_lin = pd.read_csv(OUT / "lineales_entorno.csv").iloc[0]
    ent_nl = pd.read_csv(OUT / "no_lineales_entorno.csv").iloc[0]
    origen = {"Persistencia": (lin, "Persistencia"), "Ridge": (lin, ent_lin.seleccion_validacion),
              "Random Forest": (nl, ent_nl.seleccion_RandomForest), "HistGB": (nl, ent_nl.seleccion_HistGB)}
    if not str(ent_lin.seleccion_validacion).startswith("Ridge"):
        raise ValueError("El script asume que el lineal elegido es Ridge; renombrar la etiqueta si cambia")
    anchas = {}
    for bloque in BLOQUES:
        partes, real = [], None
        for nombre, (tabla, etiqueta) in origen.items():
            sub = tabla[(tabla.modelo == etiqueta) & (tabla.bloque == bloque)].set_index("instante_objetivo").sort_index()
            if sub.empty:
                raise ValueError(f"Faltan predicciones de {etiqueta} en {bloque}")
            if real is None:
                real = sub["real"]
            elif not (sub.index.equals(real.index) and np.allclose(sub["real"], real)):
                raise ValueError(f"{etiqueta} no usa las mismas filas que la persistencia en {bloque}")
            partes.append(sub["prediccion"].rename(nombre))
        anchas[bloque] = pd.concat([real.rename("real")] + partes, axis=1)
    return anchas, origen


def resumen(real, pred):
    e = pred - real
    return {"n": len(real), "MAE": e.abs().mean(), "RMSE": np.sqrt((e ** 2).mean()), "sesgo": e.mean()}


def bootstrap_diferencia(ae_a, ae_b, mascara, rng):
    """IC 95 % por bootstrap de bloques móviles de MAE(a) − MAE(b) en las filas de ``mascara``.

    Se remuestrean bloques de filas consecutivas de todo el bloque temporal y la diferencia
    se calcula en las filas remuestreadas que cumplen la máscara, para respetar la
    autocorrelación de los errores.
    """
    n = len(ae_a)
    inicios = rng.integers(0, n - BLOQUE + 1, size=(B, int(np.ceil(n / BLOQUE))))
    idx = (inicios[:, :, None] + np.arange(BLOQUE)).reshape(B, -1)[:, :n]
    m = mascara[idx]
    with np.errstate(invalid="ignore"):
        dif = (np.where(m, ae_a[idx], 0).sum(1) - np.where(m, ae_b[idx], 0).sum(1)) / m.sum(1)
    dif = dif[np.isfinite(dif)]
    return np.percentile(dif, 2.5), np.percentile(dif, 97.5)


def comparar_calendario(rng):
    """Pregunta 2: MAE(con calendario) − MAE(sin calendario) en validación, con IC bootstrap.

    Solo validación: en prueba se evaluó únicamente la variante elegida de cada familia.
    """
    filas = []
    for archivo, familias in (("lineales_predicciones.csv", ("Ridge", "Lasso")),
                              ("no_lineales_predicciones.csv", ("RandomForest", "HistGB"))):
        P = pd.read_csv(OUT / archivo)
        P = P[P.bloque == "validacion"]
        for f in familias:
            con = P[P.modelo == f"{f}_con_calendario"].set_index("instante_objetivo").sort_index()
            sin = P[P.modelo == f"{f}_sin_calendario"].set_index("instante_objetivo").sort_index()
            if not con.index.equals(sin.index):
                raise ValueError(f"{f}: variantes con y sin calendario en filas distintas")
            ae_con = (con.prediccion - con.real).abs().to_numpy()
            ae_sin = (sin.prediccion - sin.real).abs().to_numpy()
            lo, hi = bootstrap_diferencia(ae_con, ae_sin, np.ones(len(con), bool), rng)
            filas.append({"familia": f, "bloque": "validacion", "n": len(con), "mae_sin": ae_sin.mean(),
                          "mae_con": ae_con.mean(), "dif_con_menos_sin": ae_con.mean() - ae_sin.mean(),
                          "cambio_pct": 100 * (ae_con.mean() / ae_sin.mean() - 1), "ic95_inf": lo, "ic95_sup": hi})
    print(pd.DataFrame(filas).round(4).to_string(index=False))
    return filas


def main():
    anchas, origen = cargar_predicciones()
    modelos = list(origen)
    umbral = pd.read_csv(OUT / "supervisado_train.csv")[OBJETIVO].quantile(0.90)
    rng = np.random.default_rng(SEMILLA)
    por_hora, por_mes, por_nivel, regimen, comparacion = [], [], [], [], []

    for bloque, W in anchas.items():
        y = W["real"]
        ae = {m: (W[m] - y).abs().to_numpy() for m in modelos}
        hora = W.index.hour
        mes = W.index.to_period("M").astype(str)
        nivel = pd.cut(y, NIVELES, right=False, labels=ETIQ_NIVELES)
        for m in modelos:
            for clave, grupo, destino in (("hora", hora, por_hora), ("mes", mes, por_mes), ("nivel", nivel, por_nivel)):
                for g, idx in W.groupby(grupo, observed=True).indices.items():
                    destino.append({"bloque": bloque, "modelo": m, clave: g, "media_real": y.iloc[idx].mean(),
                                    **resumen(y.iloc[idx], W[m].iloc[idx])})

        # Comparación global con IC (pregunta 1) y régimen alto (pregunta 3).
        p90_bloque = y.quantile(0.90)
        definiciones = {
            "todas": (np.ones(len(y), bool), np.nan),
            "umbral_p90_entrenamiento": ((y >= umbral).to_numpy(), umbral),
            "decil_superior_bloque": ((y >= p90_bloque).to_numpy(), p90_bloque),
            "resto_bajo_decil_superior": ((y < p90_bloque).to_numpy(), p90_bloque),
        }
        for definicion, (mascara, corte) in definiciones.items():
            base = ae["Persistencia"][mascara].mean()
            for m in modelos:
                fila = {"bloque": bloque, "definicion": definicion, "corte_ugm3": corte, "modelo": m,
                        **resumen(y[mascara], W[m][mascara]),
                        "mejora_mae_vs_persistencia_pct": 100 * (1 - ae[m][mascara].mean() / base)}
                if m != "Persistencia":
                    lo, hi = bootstrap_diferencia(ae[m], ae["Persistencia"], mascara, rng)
                    fila.update({"dif_mae_vs_persistencia": ae[m][mascara].mean() - base,
                                 "ic95_inf": lo, "ic95_sup": hi})
                (comparacion if definicion == "todas" else regimen).append(fila)
        # Diferencias entre familias (¿el no lineal supera al lineal?).
        for m in ("Random Forest", "HistGB"):
            lo, hi = bootstrap_diferencia(ae[m], ae["Ridge"], np.ones(len(y), bool), rng)
            comparacion.append({"bloque": bloque, "definicion": "todas", "modelo": f"{m} − Ridge",
                                "dif_mae_vs_ridge": ae[m].mean() - ae["Ridge"].mean(), "ic95_inf": lo, "ic95_sup": hi})

    calendario = comparar_calendario(rng)
    tablas = {"errores_calendario.csv": calendario, "errores_por_hora.csv": por_hora, "errores_por_mes.csv": por_mes, "errores_por_nivel.csv": por_nivel,
              "errores_regimen_alto.csv": regimen, "errores_comparacion_global.csv": comparacion}
    for nombre, filas in tablas.items():
        pd.DataFrame(filas).to_csv(OUT / nombre, index=False, float_format="%.6f")
    print(f"Umbral del régimen alto (p90 de la respuesta en entrenamiento): {umbral:.2f} µg/m³")
    print(pd.DataFrame(regimen)[["bloque", "definicion", "modelo", "n", "MAE", "sesgo",
                                 "mejora_mae_vs_persistencia_pct", "ic95_inf", "ic95_sup"]].round(3).to_string(index=False))
    print(pd.DataFrame(comparacion).round(3).to_string(index=False))
    figuras(anchas, modelos, pd.DataFrame(por_hora), pd.DataFrame(por_mes), pd.DataFrame(por_nivel))


def guardar(fig, nombre):
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / f"{nombre}.png", dpi=300)
    fig.savefig(FIG / f"{nombre}.pdf")
    plt.close(fig)


def figuras(anchas, modelos, por_hora, por_mes, por_nivel):
    # 15: MAE global por modelo y bloque, con la mejora frente a persistencia.
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.4), sharey=True)
    for ax, (bloque, W) in zip(axes, anchas.items()):
        maes = [(W[m] - W["real"]).abs().mean() for m in modelos]
        barras = ax.bar(range(len(modelos)), maes, color=[COLOR[m] for m in modelos], width=0.62,
                        edgecolor="white", linewidth=1)
        for b, v in zip(barras, maes):
            mejora = 100 * (1 - v / maes[0])
            texto = coma(v) if b is barras[0] else f"{coma(v)}\n(−{coma(mejora, 1)} %)"
            ax.text(b.get_x() + b.get_width() / 2, v + 0.05, texto, ha="center", va="bottom", fontsize=7)
        ax.set_xticks(range(len(modelos)), modelos)
        ax.set_title(BLOQUES[bloque], fontsize=8)
        ax.grid(axis="x", visible=False)
    axes[0].set_ylabel("MAE (µg/m³)")
    axes[0].set_ylim(0, max(axes[0].get_ylim()[1], axes[1].get_ylim()[1]) * 1.18)
    fig.tight_layout()
    guardar(fig, "15_comparacion_modelos")

    # 16: importancia por permutación en validación de los no lineales elegidos.
    imp = pd.read_csv(OUT / "no_lineales_importancia.csv")
    ent = pd.read_csv(OUT / "no_lineales_entorno.csv").iloc[0]
    sel = {"Random Forest": ent.seleccion_RandomForest, "HistGB": ent.seleccion_HistGB}
    var = imp[imp.tipo == "permutacion_variable"]
    orden = (var[var.modelo == sel["Random Forest"]].sort_values("aumento_mae").variable.tolist())
    resto = [v for v in var.variable.unique() if v not in orden]
    orden = resto + orden
    fig, ax = plt.subplots(figsize=(3.5, 2.9))
    alto = 0.38
    for k, (nombre, etiqueta) in enumerate(sel.items()):
        d = var[var.modelo == etiqueta].set_index("variable").reindex(orden)
        pos = np.arange(len(orden)) - (k - 0.5) * alto     # Random Forest arriba, como en la leyenda
        ax.barh(pos, d.aumento_mae, height=alto, xerr=d.desv, color=COLOR[nombre], label=nombre,
                edgecolor="white", linewidth=0.8, error_kw={"elinewidth": 0.6, "ecolor": "#52514e"})
    ax.set_yticks(np.arange(len(orden)), [NOMBRE_VAR.get(v, v) for v in orden])
    ax.set_xlabel("Aumento del MAE al permutar (µg/m³)")
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower right", fontsize=7)
    fig.tight_layout()
    guardar(fig, "16_importancia_variables")

    # 17: MAE por hora (validación) y por mes (validación y prueba).
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 2.5), gridspec_kw={"width_ratios": [1, 1.25]})
    h = por_hora[por_hora.bloque == "validacion"]
    pm = por_mes.copy()
    meses = sorted(pm.mes.unique())
    for m in modelos:
        d = h[h.modelo == m].sort_values("hora")
        a1.plot(d.hora, d.MAE, color=COLOR[m], ls=LINEA[m], lw=1.6, marker=MARCA[m], ms=3, label=m)
        d = pm[pm.modelo == m].set_index("mes").reindex(meses)
        a2.plot(range(len(meses)), d.MAE, color=COLOR[m], ls=LINEA[m], lw=1.6, marker=MARCA[m], ms=3.5, label=m)
    a1.set_xlabel("Hora pronosticada (validación)")
    a1.set_xticks(range(0, 24, 3))
    a1.set_ylabel("MAE (µg/m³)")
    a2.axvline(meses.index("2024-01") - 0.5, color="#52514e", lw=0.7, ls="--")
    a2.text(meses.index("2024-01") - 0.4, a2.get_ylim()[1] * 0.97, "prueba", fontsize=7, va="top", color="#52514e")
    nombres_mes = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    a2.set_xticks(range(len(meses)), [f"{nombres_mes[int(x[5:]) - 1]}\n{x[2:4]}" for x in meses], fontsize=7)
    manejadores, etiquetas = a2.get_legend_handles_labels()
    fig.legend(manejadores, etiquetas, loc="upper center", ncol=4, fontsize=7, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    guardar(fig, "17_errores_hora_mes")

    # 18: MAE y sesgo por nivel de concentración observado.
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 3.9), sharex=True, sharey="row")
    ancho = 0.2
    for j, bloque in enumerate(BLOQUES):
        d = por_nivel[por_nivel.bloque == bloque]
        presentes = [e for e in ETIQ_NIVELES if e in set(d.nivel)]
        for k, m in enumerate(modelos):
            dm = d[d.modelo == m].set_index("nivel").reindex(presentes)
            x = np.array([ETIQ_NIVELES.index(e) for e in presentes]) + (k - 1.5) * ancho
            axes[0, j].bar(x, dm.MAE, width=ancho, color=COLOR[m], label=m, edgecolor="white", linewidth=0.6)
            axes[1, j].bar(x, dm.sesgo, width=ancho, color=COLOR[m], edgecolor="white", linewidth=0.6)
        n = d[d.modelo == "Persistencia"].set_index("nivel").reindex(presentes)["n"]
        for e, v in n.items():
            axes[0, j].text(ETIQ_NIVELES.index(e), 0.98, f"n={v}", transform=axes[0, j].get_xaxis_transform(),
                            ha="center", va="top", fontsize=6.5, color="#52514e")
        axes[0, j].set_title(BLOQUES[bloque], fontsize=8)
        axes[1, j].axhline(0, color="#52514e", lw=0.7)
        axes[1, j].set_xticks(range(len(ETIQ_NIVELES)), ETIQ_NIVELES, fontsize=7)
        axes[1, j].set_xlabel("PM2.5 observado en t+1 (µg/m³)")
        for ax in axes[:, j]:
            ax.grid(axis="x", visible=False)
    axes[0, 0].set_ylabel("MAE (µg/m³)")
    axes[1, 0].set_ylabel("Sesgo medio (µg/m³)\npredicho − observado")
    axes[0, 0].set_ylim(0, axes[0, 0].get_ylim()[1] * 1.12)
    axes[0, 1].legend(fontsize=7, loc="center left")
    fig.tight_layout()
    guardar(fig, "18_errores_por_nivel")
    print("Figuras 15 a 18 guardadas en figures/")


if __name__ == "__main__":
    main()
