import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta
import math
import sys

# Script de python per dibuxar un Horizon Graph, amb les dades d'una setmana concreta
# del dataset a "AEP_hourly.csv". Horitzó definit com la mitjana del consum de tot el dataset,
# Que conté dades de consum des de Octubre de 2004 fins al Agost de 2018.

# Accepta el numero de la setmana que es vol visualitzar com a paràmetre. Per defecte mostra la primera setmana. 

def plot_horizon_week_number(
    csv_path="AEP_hourly.csv",
    week_number=1,
    bands=3,
    save=False
):
    # Preparar dades
    df = pd.read_csv(csv_path)
    df["Datetime"] = pd.to_datetime(df["Datetime"])
    df = df.sort_values("Datetime")
    df["date"] = df["Datetime"].dt.date
    df["hour"] = df["Datetime"].dt.hour

    if df.empty:
        raise ValueError("No s'han trobat dades al dataset.")

    # Calcul de mitja global per definir l'horitzó
    global_mean = df["AEP_MW"].mean()

    # Selecció de la setmana demanada dins del dataset
    unique_dates = sorted(df["date"].unique().tolist())
    if len(unique_dates) == 0:
        raise ValueError("No hi ha dates vàlides al dataset.")

    total_weeks = math.ceil(len(unique_dates) / 7)
    if week_number < 1 or week_number > total_weeks:
        raise ValueError(f"El número de setmana ha d'estar entre 1 i {total_weeks}. Valor rebut: {week_number}")

    start_idx = (week_number - 1) * 7
    week_dates = unique_dates[start_idx:start_idx + 7]

    if not week_dates:
        raise ValueError("No hi ha dades per a la setmana indicada.")

    week_df = df[df["date"].isin(week_dates)].copy()
    week_df["deviation"] = week_df["AEP_MW"] - global_mean

    # Definir les bandes per als gradients de colors
    max_dev = np.nanmax(np.abs(week_df["deviation"].values))
    if not np.isfinite(max_dev) or max_dev == 0:
        max_dev = 1.0
    band_size = max_dev / bands

    # Paleta de colors
    positius = ["#cfe8ff", "#7fb6ff", "#2b7bff"]  
    negatius  = ["#ffcfcf", "#ff7f7f", "#ff2b2b"]  

    # Funció per pintar el grafic amb l'eix X a l'altura del horizó definit.
    def draw_horizon(ax, day_df):
        day_df = day_df.sort_values("hour")
        x = day_df["hour"].values

        dev = day_df["deviation"].values

        # Coloreig per areas de valors positius
        pos = np.clip(dev, 0, None)
        for i in range(1, bands + 1):
            lower = (i - 1) * band_size
            upper = i * band_size
            band = np.clip(pos, lower, upper) - lower
            ax.fill_between(x, 0, band, alpha=1.0, linewidth=0, color=positius[i-1])

        # Coloreig d'areas de valors negatius i inversió de valors
        neg = np.clip(-dev, 0, None)
        for i in range(1, bands + 1):
            lower = (i - 1) * band_size
            upper = i * band_size
            band = np.clip(neg, lower, upper) - lower
            ax.fill_between(x, 0, band, alpha=1.0, linewidth=0, color=negatius[i-1])

        # Definició de l'horitzó i compactació de les franges
        ax.axhline(0, color="#777777", linewidth=0.8, linestyle="--")
        ax.set_ylim(0, band_size)
        ax.set_yticks([])
        ax.set_xlim(0, 23)
        ax.set_xticks(range(0, 24, 2))

    # Creacio dels subplots, labels ...
    n_rows = len(week_dates)
    fig, axes = plt.subplots(n_rows, 1, figsize=(12, 1.8 * n_rows), sharex=True)
    if n_rows == 1:
        axes = [axes] 

    for ax, d in zip(axes, week_dates):
        day = week_df[week_df["date"] == d]
        draw_horizon(ax, day)
        ax.text(-0.02, 0.5, f"{d}",
                transform=ax.transAxes, va="center", ha="right", fontsize=10)

    axes[-1].set_xlabel("Hora del dia")
    fig.suptitle(
        f"Horizon Graph – Setmana {week_number} – Consum en MW: \n"
        f"Horitzó (mitja de consum)= {global_mean:,.0f} MW",
        fontsize=12, y=1.0
    )
    plt.tight_layout()

    # Opció per guardar automaticament el grafic
    if save:
        out = f"horizon_week_{week_number:02d}_AEP_{week_dates[0]}_to_{week_dates[-1]}.png"
        plt.savefig(out, dpi=150, bbox_inches="tight")
        print(f"Gráfico guardado en: {out}")

    plt.show()


# Comprovació dels paràmetres
if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            week_num = int(sys.argv[1])
        except ValueError:
            print("Error: Número de setmana no valid.")
            sys.exit(1)
    else:
        week_num = 1

    plot_horizon_week_number("AEP_hourly.csv", week_number=week_num, bands=3, save=False)
