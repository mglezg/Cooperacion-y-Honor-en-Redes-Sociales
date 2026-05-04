# ============================================================
#  visor.py
#  Interfaz interactiva Streamlit para explorar simulaciones
#  Ejecutar con: streamlit run visor.py
#  Instalar:     pip install streamlit
# ============================================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
import glob

# ── Configuracion de pagina ──────────────────────────────────
st.set_page_config(
    page_title="Cooperacion y Honor - Visor",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Estilos ──────────────────────────────────────────────────
COLORES = {
    'E': '#E15759', 'P': '#4E79A7',
    'O': '#F28E2B', 'A': '#59A14F', 'R': '#B07AA1',
}
ETIQUETAS = {
    'E': 'Envidioso', 'P': 'Pesimista',
    'O': 'Optimista', 'A': 'Altruista', 'R': 'Aleatorio',
}
FONDO = '#1a1a2e'
PANEL = '#16213e'

st.markdown("""
<style>
    .stApp { background-color: #1a1a2e; color: #e0e0e0; }
    .metric-card {
        background: #16213e; border-radius: 10px;
        padding: 14px 18px; margin: 4px 0;
        border: 1px solid #2a2a4e;
    }
    .metric-label { font-size: 12px; color: #888; margin: 0; }
    .metric-value { font-size: 22px; font-weight: 600; margin: 0; color: #e0e0e0; }
</style>
""", unsafe_allow_html=True)

# ── Carga de datos ────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    log_global  = "resultados/logs/log.csv"
    log_jugadores = "resultados/logs/log_jugadores.csv"
    df_global   = pd.read_csv(log_global)    if os.path.exists(log_global)    else None
    df_jugadores = pd.read_csv(log_jugadores) if os.path.exists(log_jugadores) else None
    return df_global, df_jugadores

df_global, df_jugadores = cargar_datos()

if df_global is None:
    st.error("No se encontraron logs. Ejecuta primero main.py para generar una simulacion.")
    st.stop()

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.title("🧬 Cooperacion y Honor")
    st.caption("Simulacion de Fenotipos con LLM")
    st.divider()

    vista = st.radio("Vista", [
        "Resumen global",
        "Evolucion de fenotipos",
        "Sistema de honor",
        "Agente individual",
        "Visor de justificaciones",
        "Frames de la reticula",
    ])

    st.divider()
    pasos_total = df_global["paso"].max()
    st.metric("Pasos simulados", pasos_total + 1)
    if df_jugadores is not None:
        st.metric("Agentes", df_jugadores["id"].nunique())

# ── Paleta matplotlib oscura ─────────────────────────────────
def fig_oscuro(w=10, h=5):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(FONDO)
    ax.set_facecolor(PANEL)
    ax.tick_params(colors='#e0e0e0')
    for spine in ax.spines.values():
        spine.set_edgecolor('#333355')
    ax.xaxis.label.set_color('#e0e0e0')
    ax.yaxis.label.set_color('#e0e0e0')
    ax.title.set_color('#e0e0e0')
    ax.grid(True, color='#2a2a4e', linewidth=0.6, alpha=0.8)
    return fig, ax

def fig_oscuro_multi(nrows, ncols, w=14, h=5):
    fig, axes = plt.subplots(nrows, ncols, figsize=(w, h))
    fig.patch.set_facecolor(FONDO)
    for ax in (axes.flat if hasattr(axes, 'flat') else [axes]):
        ax.set_facecolor(PANEL)
        ax.tick_params(colors='#e0e0e0')
        for spine in ax.spines.values():
            spine.set_edgecolor('#333355')
        ax.xaxis.label.set_color('#e0e0e0')
        ax.yaxis.label.set_color('#e0e0e0')
        ax.title.set_color('#e0e0e0')
        ax.grid(True, color='#2a2a4e', linewidth=0.6, alpha=0.8)
    return fig, axes

# ─────────────────────────────────────────────────────────────
# VISTA: Resumen global
# ─────────────────────────────────────────────────────────────
if vista == "Resumen global":
    st.header("Resumen de la simulacion")

    coop_final  = df_global['cooperacion_global'].iloc[-1]
    coop_max    = df_global['cooperacion_global'].max()
    coop_media  = df_global['cooperacion_global'].mean()

    c1, c2, c3 = st.columns(3)
    c1.metric("Cooperacion final",  f"{coop_final:.1%}")
    c2.metric("Cooperacion maxima", f"{coop_max:.1%}")
    c3.metric("Cooperacion media",  f"{coop_media:.1%}")

    st.divider()
    fig, ax = fig_oscuro(10, 4)
    ax.plot(df_global['paso'], df_global['cooperacion_global'],
            color='#27AE60', linewidth=2)
    ax.fill_between(df_global['paso'], df_global['cooperacion_global'],
                    alpha=0.15, color='#27AE60')
    ax.set_ylim(0, 1)
    ax.set_title('Evolucion de la cooperacion global')
    ax.set_xlabel('Paso')
    ax.set_ylabel('phi(t)')
    st.pyplot(fig)

    if df_jugadores is not None and 'rep_pos' in df_jugadores.columns:
        st.divider()
        st.subheader("Reputacion media por fenotipo")
        fig, (ax1, ax2) = fig_oscuro_multi(1, 2, 14, 4)
        for f, c in COLORES.items():
            sub = df_jugadores[df_jugadores['fenotipo'] == f]
            if sub.empty: continue
            ax1.plot(sub.groupby('paso')['rep_pos'].mean(),
                     color=c, label=ETIQUETAS[f], linewidth=1.8)
            ax2.plot(sub.groupby('paso')['rep_neg'].mean(),
                     color=c, label=ETIQUETAS[f], linewidth=1.8)
        for ax, t in [(ax1, 'Reputacion positiva'), (ax2, 'Reputacion negativa')]:
            ax.set_ylim(0, 1)
            ax.set_title(t)
            ax.set_xlabel('Paso')
            leg = ax.legend(fontsize=8, facecolor='#2a2a3e',
                            labelcolor='white', edgecolor='#444')
        st.pyplot(fig)

# ─────────────────────────────────────────────────────────────
# VISTA: Evolucion de fenotipos
# ─────────────────────────────────────────────────────────────
elif vista == "Evolucion de fenotipos":
    st.header("Evolucion de la proporcion de fenotipos")
    fig, ax = fig_oscuro(11, 5)
    for f, c in COLORES.items():
        if f in df_global.columns:
            ax.plot(df_global['paso'], df_global[f],
                    label=ETIQUETAS[f], color=c, linewidth=2)
    ax.set_ylim(0, 1)
    ax.set_title('Proporcion de cada fenotipo por ronda')
    ax.set_xlabel('Paso')
    ax.set_ylabel('Proporcion')
    leg = ax.legend(title='Fenotipos', fontsize=9,
                    facecolor='#2a2a3e', labelcolor='white',
                    title_fontsize=10, edgecolor='#444')
    leg.get_title().set_color('white')
    st.pyplot(fig)

    if df_jugadores is not None:
        st.divider()
        st.subheader("Cambios de fenotipo por ronda")
        cambios = df_jugadores.groupby('paso')['cambio_fenotipo'].sum()
        fig2, ax2 = fig_oscuro(10, 3)
        ax2.bar(cambios.index, cambios.values, color='#F28E2B', alpha=0.7)
        ax2.set_title('Numero de cambios de fenotipo por ronda')
        ax2.set_xlabel('Paso')
        ax2.set_ylabel('Cambios')
        st.pyplot(fig2)

# ─────────────────────────────────────────────────────────────
# VISTA: Sistema de honor
# ─────────────────────────────────────────────────────────────
elif vista == "Sistema de honor":
    st.header("Sistema de honor bidireccional")

    if df_jugadores is None or 'rep_pos' not in df_jugadores.columns:
        st.warning("No hay datos de reputacion. Asegurate de usar el logger_jugadores actualizado.")
        st.stop()

    paso_sel = st.slider("Selecciona ronda", 0, int(df_global['paso'].max()), 0)

    df_paso = df_jugadores[df_jugadores['paso'] == paso_sel]

    st.subheader(f"Distribucion de reputacion en ronda {paso_sel}")
    c1, c2 = st.columns(2)

    with c1:
        fig, ax = fig_oscuro(6, 4)
        for f, c in COLORES.items():
            sub = df_paso[df_paso['fenotipo'] == f]
            if not sub.empty:
                ax.hist(sub['rep_pos'], bins=10, alpha=0.6,
                        color=c, label=ETIQUETAS[f], range=(0, 1))
        ax.set_title('Rep+ en esta ronda')
        ax.set_xlabel('Reputacion positiva')
        leg = ax.legend(fontsize=7, facecolor='#2a2a3e',
                        labelcolor='white', edgecolor='#444')
        st.pyplot(fig)

    with c2:
        fig, ax = fig_oscuro(6, 4)
        for f, c in COLORES.items():
            sub = df_paso[df_paso['fenotipo'] == f]
            if not sub.empty:
                ax.hist(sub['rep_neg'], bins=10, alpha=0.6,
                        color=c, label=ETIQUETAS[f], range=(0, 1))
        ax.set_title('Rep- en esta ronda')
        ax.set_xlabel('Reputacion negativa')
        leg = ax.legend(fontsize=7, facecolor='#2a2a3e',
                        labelcolor='white', edgecolor='#444')
        st.pyplot(fig)

    st.divider()
    st.subheader("Top 5 agentes mas honrados y mas deshonrados")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Mas honrados (rep+ alta)**")
        st.dataframe(
            df_paso.nlargest(5, 'rep_pos')[['id', 'fenotipo', 'rep_pos', 'rep_neg', 'estrategia']],
            hide_index=True
        )
    with c2:
        st.markdown("**Mas deshonrados (rep- alta)**")
        st.dataframe(
            df_paso.nlargest(5, 'rep_neg')[['id', 'fenotipo', 'rep_pos', 'rep_neg', 'estrategia']],
            hide_index=True
        )

# ─────────────────────────────────────────────────────────────
# VISTA: Agente individual
# ─────────────────────────────────────────────────────────────
elif vista == "Agente individual":
    st.header("Trayectoria de un agente")

    if df_jugadores is None:
        st.warning("No hay datos de jugadores.")
        st.stop()

    ids = sorted(df_jugadores['id'].unique())
    jugador_id = st.selectbox("Selecciona agente", ids)
    jugador_df = df_jugadores[df_jugadores['id'] == jugador_id]

    # Metricas rapidas
    fenotipo_final = jugador_df['fenotipo'].iloc[-1]
    pago_medio     = jugador_df['pago'].mean()
    cambios        = jugador_df['cambio_fenotipo'].sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Fenotipo final", ETIQUETAS.get(fenotipo_final, fenotipo_final))
    c2.metric("Pago medio",     f"{pago_medio:.2f}")
    c3.metric("Cambios fenotipo", int(cambios))
    if 'rep_pos' in jugador_df.columns:
        c4.metric("Rep+ final", f"{jugador_df['rep_pos'].iloc[-1]:.2f}")

    # Grafica pago
    fig, ax = fig_oscuro(10, 3)
    for f, grupo in jugador_df.groupby('fenotipo'):
        ax.plot(grupo['paso'], grupo['pago'],
                marker='o', markersize=3, linestyle='-',
                color=COLORES.get(f, 'gray'), label=ETIQUETAS.get(f, f))
    ax.set_title(f'Pago acumulado — Agente {jugador_id}')
    ax.set_xlabel('Paso')
    ax.set_ylabel('Pago')
    leg = ax.legend(fontsize=8, facecolor='#2a2a3e', labelcolor='white', edgecolor='#444')
    st.pyplot(fig)

    # Grafica honor
    if 'rep_pos' in jugador_df.columns:
        fig, ax = fig_oscuro(10, 3)
        ax.plot(jugador_df['paso'], jugador_df['rep_pos'],
                color='#27AE60', linewidth=2, label='Rep+')
        ax.plot(jugador_df['paso'], jugador_df['rep_neg'],
                color='#E74C3C', linewidth=2, label='Rep-')
        ax.fill_between(jugador_df['paso'],
                        jugador_df['rep_pos'], jugador_df['rep_neg'],
                        where=jugador_df['rep_pos'] >= jugador_df['rep_neg'],
                        alpha=0.12, color='#27AE60')
        ax.fill_between(jugador_df['paso'],
                        jugador_df['rep_pos'], jugador_df['rep_neg'],
                        where=jugador_df['rep_pos'] < jugador_df['rep_neg'],
                        alpha=0.12, color='#E74C3C')
        ax.set_ylim(0, 1)
        ax.set_title(f'Honor — Agente {jugador_id}')
        ax.set_xlabel('Paso')
        ax.set_ylabel('Reputacion')
        leg = ax.legend(fontsize=9, facecolor='#2a2a3e', labelcolor='white', edgecolor='#444')
        st.pyplot(fig)

# ─────────────────────────────────────────────────────────────
# VISTA: Justificaciones del LLM
# ─────────────────────────────────────────────────────────────
elif vista == "Visor de justificaciones":
    st.header("Justificaciones del LLM")
    st.caption("Razonamientos textuales generados por cada agente en cada ronda")

    if df_jugadores is None or 'justif_llm' not in df_jugadores.columns:
        st.warning("No hay justificaciones en el log.")
        st.stop()

    df_justif = df_jugadores[
        df_jugadores['justif_llm'].notna() &
        ~df_jugadores['justif_llm'].str.startswith('[fallback')
    ]

    c1, c2, c3 = st.columns(3)
    fenotipo_filtro  = c1.selectbox("Fenotipo", ['Todos'] + list(ETIQUETAS.keys()),
                                     format_func=lambda x: ETIQUETAS.get(x, x))
    decision_filtro  = c2.selectbox("Decision", ['Todas', 'C', 'D'])
    paso_filtro      = c3.slider("Ronda", 0, int(df_global['paso'].max()),
                                  (0, int(df_global['paso'].max())))

    df_f = df_justif.copy()
    df_f = df_f[(df_f['paso'] >= paso_filtro[0]) & (df_f['paso'] <= paso_filtro[1])]
    if fenotipo_filtro != 'Todos':
        df_f = df_f[df_f['fenotipo'] == fenotipo_filtro]
    if decision_filtro != 'Todas':
        df_f = df_f[df_f['estrategia'] == decision_filtro]

    st.metric("Justificaciones mostradas", len(df_f))
    st.divider()

    for _, row in df_f.head(30).iterrows():
        color = COLORES.get(row['fenotipo'], '#888')
        decision_emoji = "🤝" if row['estrategia'] == 'C' else "🗡️"
        with st.expander(
            f"{decision_emoji} Ronda {row['paso']} | Agente {row['id']} | "
            f"{ETIQUETAS.get(row['fenotipo'], row['fenotipo'])} | "
            f"{'COOPERAR' if row['estrategia'] == 'C' else 'DEFECTAR'}"
        ):
            st.markdown(f"> {row['justif_llm']}")
            if 'rep_pos' in row:
                st.caption(f"Rep+: {row['rep_pos']:.2f}  |  Rep-: {row['rep_neg']:.2f}  |  Pago: {row['pago']:.2f}")

# ─────────────────────────────────────────────────────────────
# VISTA: Frames de la reticula
# ─────────────────────────────────────────────────────────────
elif vista == "Frames de la reticula":
    st.header("Visor de frames")

    frames = sorted(glob.glob("img/frames/frame_*.png"))
    if not frames:
        st.warning("No hay frames generados. Ejecuta main.py primero.")
        st.stop()

    paso_frame = st.slider("Ronda", 0, len(frames) - 1, 0)
    st.image(frames[paso_frame], use_column_width=True)
    st.caption(f"Frame {paso_frame + 1} de {len(frames)}")

    gif_path = "img/simulacion.gif"
    if os.path.exists(gif_path):
        st.divider()
        st.subheader("GIF completo de la simulacion")
        st.image(gif_path)
