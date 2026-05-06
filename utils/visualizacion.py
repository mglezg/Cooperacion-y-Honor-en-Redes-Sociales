import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generar_figura_simulacion(G, pos, info_agentes, decisiones_ronda):
    fig, ax = plt.subplots(figsize=(10, 10))
    fig.patch.set_facecolor(ESTILO['fondo']) # Mantén el fondo oscuro consistente
    
    # Usamos las etiquetas cortas ('A', 'E', etc.) que vienen de tu lógica core
    for node in G.nodes():
        x, y = pos[node]
        agente = info_agentes[node]
        # Asegúrate de que 'fenotipo' sea la letra (A, E, O, P, R)
        cod_fenotipo = agente['fenotipo'] 
        rep = agente.get('reputacion', 0.5)
        dec = decisiones_ronda.get(node, 'cooperar')
        
        # --- CANAL 1 y 3: Fondo y Brillo ---
        # Brillo: Agentes con reputación < 0.5 se ven más opacos (marginados)
        alfa = 1.0 if rep >= 0.5 else 0.3 
        color_fondo = COLORES_FENOTIPOS.get(cod_fenotipo, '#A9A9A9')
        
        rect_fondo = patches.Rectangle((x-0.4, y-0.4), 0.8, 0.8, 
                                      facecolor=color_fondo,
                                      alpha=alfa, zorder=1)
        ax.add_patch(rect_fondo)

        # --- CANAL 2: Borde (Honradez) ---
        color_borde = 'none'
        if rep >= 0.7: color_borde = ESTILO['verde'] # Honrado
        elif rep <= 0.3: color_borde = ESTILO['rojo'] # Deshonrado
        
        if color_borde != 'none':
            rect_borde = patches.Rectangle((x-0.45, y-0.45), 0.9, 0.9, 
                                          linewidth=2.5, edgecolor=color_borde, 
                                          fill=False, zorder=2)
            ax.add_patch(rect_borde)

        # --- CANAL 4: Marcador central (Decisión) ---
        # Blanco si cooperó, Gris oscuro si defectó
        color_punto = 'white' if dec == 'cooperar' else '#333333'
        ax.scatter(x, y, c=color_punto, s=120, edgecolors='none', zorder=3)

    ax.set_aspect('equal')
    ax.axis('off')
    return fig

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
