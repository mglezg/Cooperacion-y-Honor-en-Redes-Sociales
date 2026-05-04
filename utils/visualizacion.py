import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

# Paleta consistente con reticula_nx.py
COLORES_FENOTIPOS = {
    'E': '#E15759',
    'P': '#4E79A7',
    'O': '#F28E2B',
    'A': '#59A14F',
    'R': '#B07AA1',
}

ETIQUETAS = {
    'E': 'Envidioso',
    'P': 'Pesimista',
    'O': 'Optimista',
    'A': 'Altruista',
    'R': 'Aleatorio',
}

ESTILO = {
    'fondo':     '#1a1a2e',
    'panel':     '#16213e',
    'texto':     '#e0e0e0',
    'grid':      '#2a2a4e',
    'verde':     '#27AE60',
    'rojo':      '#E74C3C',
}

def _aplicar_estilo_oscuro(ax, titulo, xlabel, ylabel):
    ax.set_facecolor(ESTILO['panel'])
    ax.tick_params(colors=ESTILO['texto'])
    ax.xaxis.label.set_color(ESTILO['texto'])
    ax.yaxis.label.set_color(ESTILO['texto'])
    ax.title.set_color(ESTILO['texto'])
    ax.set_title(titulo, fontsize=11, pad=8)
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.grid(True, color=ESTILO['grid'], linewidth=0.6, alpha=0.8)
    for spine in ax.spines.values():
        spine.set_edgecolor('#333355')


def graficar_resultados_globales(
        log_path="resultados/logs/log.csv",
        log_jugadores_path="resultados/logs/log_jugadores.csv",
        out_dir="resultados/plots"):

    os.makedirs(out_dir, exist_ok=True)
    df = pd.read_csv(log_path)

    # ── Grafico 1: Cooperacion global ────────────────────────
    fig, ax = plt.subplots(figsize=(9, 4))
    fig.patch.set_facecolor(ESTILO['fondo'])
    ax.plot(df['paso'], df['cooperacion_global'],
            color=ESTILO['verde'], linewidth=2.0, label='phi(t)')
    ax.fill_between(df['paso'], df['cooperacion_global'],
                    alpha=0.15, color=ESTILO['verde'])
    ax.set_ylim(0, 1)
    _aplicar_estilo_oscuro(ax, 'Evolucion de la cooperacion global', 'Paso', 'phi(t)')
    leg = ax.legend(fontsize=8, facecolor='#2a2a3e', labelcolor='white', edgecolor='#444')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'cooperacion_global.png'),
                dpi=130, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()

    # ── Grafico 2: Proporcion de fenotipos ───────────────────
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor(ESTILO['fondo'])
    for fenotipo, color in COLORES_FENOTIPOS.items():
        if fenotipo in df.columns:
            ax.plot(df['paso'], df[fenotipo],
                    label=ETIQUETAS[fenotipo], color=color, linewidth=1.8)
    _aplicar_estilo_oscuro(ax, 'Evolucion de la proporcion de fenotipos', 'Paso', 'Proporcion')
    ax.set_ylim(0, 1)
    leg = ax.legend(title='Fenotipos', fontsize=8,
                    facecolor='#2a2a3e', labelcolor='white',
                    title_fontsize=9, edgecolor='#444')
    leg.get_title().set_color('white')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'fenotipos_evolucion.png'),
                dpi=130, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()

    # ── Grafico 3: Reputacion por fenotipo (si existe) ───────
    if os.path.exists(log_jugadores_path):
        dfj = pd.read_csv(log_jugadores_path)
        if 'rep_pos' in dfj.columns:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
            fig.patch.set_facecolor(ESTILO['fondo'])
            for fenotipo, color in COLORES_FENOTIPOS.items():
                sub = dfj[dfj['fenotipo'] == fenotipo]
                if sub.empty:
                    continue
                media_pos = sub.groupby('paso')['rep_pos'].mean()
                media_neg = sub.groupby('paso')['rep_neg'].mean()
                ax1.plot(media_pos.index, media_pos.values,
                         color=color, label=ETIQUETAS[fenotipo], linewidth=1.8)
                ax2.plot(media_neg.index, media_neg.values,
                         color=color, label=ETIQUETAS[fenotipo], linewidth=1.8)
            for ax, titulo in [(ax1, 'Reputacion positiva media por fenotipo'),
                                (ax2, 'Reputacion negativa media por fenotipo')]:
                _aplicar_estilo_oscuro(ax, titulo, 'Paso', 'Reputacion')
                ax.set_ylim(0, 1)
                leg = ax.legend(fontsize=8, facecolor='#2a2a3e',
                                labelcolor='white', edgecolor='#444')
            plt.tight_layout()
            plt.savefig(os.path.join(out_dir, 'reputacion_evolucion.png'),
                        dpi=130, bbox_inches='tight', facecolor=fig.get_facecolor())
            plt.close()

    print("Graficas guardadas en:", out_dir)


def graficar_rendimiento_jugador(
        log_path="resultados/logs/log_jugadores.csv",
        jugador_id="0-0",
        out_dir="resultados/plots"):

    df = pd.read_csv(log_path)
    jugador_df = df[df['id'] == jugador_id]

    if jugador_df.empty:
        print(f"No se encontraron datos para el jugador {jugador_id}")
        return

    tiene_honor = 'rep_pos' in jugador_df.columns
    ncols = 2 if tiene_honor else 1
    fig, axes = plt.subplots(1, ncols, figsize=(11 * ncols, 5))
    fig.patch.set_facecolor(ESTILO['fondo'])
    ax_pago = axes[0] if tiene_honor else axes

    # Panel izquierdo: pago acumulado
    for fenotipo, grupo in jugador_df.groupby('fenotipo'):
        ax_pago.plot(grupo['paso'], grupo['pago'],
                     marker='o', markersize=3, linestyle='-',
                     color=COLORES_FENOTIPOS.get(fenotipo, 'gray'),
                     label=ETIQUETAS.get(fenotipo, fenotipo))
    _aplicar_estilo_oscuro(ax_pago,
                           f'Rendimiento del agente {jugador_id}',
                           'Paso', 'Pago acumulado')
    leg = ax_pago.legend(title='Fenotipo', fontsize=8,
                         facecolor='#2a2a3e', labelcolor='white',
                         title_fontsize=9, edgecolor='#444')
    leg.get_title().set_color('white')

    # Panel derecho: honor (si tiene datos)
    if tiene_honor:
        ax_h = axes[1]
        ax_h.plot(jugador_df['paso'], jugador_df['rep_pos'],
                  color=ESTILO['verde'], linewidth=2.0, label='Rep+')
        ax_h.plot(jugador_df['paso'], jugador_df['rep_neg'],
                  color=ESTILO['rojo'],  linewidth=2.0, label='Rep-')
        ax_h.fill_between(jugador_df['paso'],
                          jugador_df['rep_pos'], jugador_df['rep_neg'],
                          where=jugador_df['rep_pos'] >= jugador_df['rep_neg'],
                          alpha=0.12, color=ESTILO['verde'], label='zona honrada')
        ax_h.fill_between(jugador_df['paso'],
                          jugador_df['rep_pos'], jugador_df['rep_neg'],
                          where=jugador_df['rep_pos'] < jugador_df['rep_neg'],
                          alpha=0.12, color=ESTILO['rojo'], label='zona deshonrada')
        ax_h.set_ylim(0, 1)
        _aplicar_estilo_oscuro(ax_h,
                               f'Honor del agente {jugador_id}',
                               'Paso', 'Reputacion')
        leg = ax_h.legend(fontsize=8, facecolor='#2a2a3e',
                          labelcolor='white', edgecolor='#444')

    plt.tight_layout()
    subdir = os.path.join(out_dir, 'rendimiento')
    os.makedirs(subdir, exist_ok=True)
    filename = os.path.join(subdir, f"{jugador_id.replace('-', '_')}.png")
    plt.savefig(filename, dpi=130, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print(f"Grafico guardado: {filename}")
