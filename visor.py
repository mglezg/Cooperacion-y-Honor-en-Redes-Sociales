# ============================================================
#  visor.py  —  Interfaz Streamlit mejorada
#  Ejecutar con: streamlit run visor.py
# ============================================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import os
import glob

# ── Configuracion de pagina ──────────────────────────────────
st.set_page_config(
    page_title="Cooperacion y Honor — Visor",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Paleta y constantes ──────────────────────────────────────
COLORES = {
    'E': '#E15759', 'P': '#4E79A7',
    'O': '#F28E2B', 'A': '#59A14F', 'R': '#B07AA1',
}
ETIQUETAS = {
    'E': 'Envidioso', 'P': 'Pesimista',
    'O': 'Optimista', 'A': 'Altruista', 'R': 'Aleatorio',
}
FONDO  = '#1a1a2e'
PANEL  = '#16213e'
TEXTO  = '#e0e0e0'
GRID   = '#2a2a4e'
VERDE  = '#27AE60'
ROJO   = '#E74C3C'
ACCENT = '#7B68EE'

# ── Estilos globales ─────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #1a1a2e; color: #e0e0e0; }
    [data-testid="stSidebar"] { background-color: #12122a !important; }
    [data-testid="stSidebar"] * { color: #c8c8e8 !important; }
    [data-testid="stMetric"] {
        background: #16213e;
        border: 1px solid #2a2a4e;
        border-radius: 10px;
        padding: 14px 18px;
    }
    [data-testid="stMetricLabel"]  { color: #888 !important; font-size: 11px !important; }
    [data-testid="stMetricValue"]  { color: #e0e0e0 !important; }
    [data-testid="stMetricDelta"]  { color: #27AE60 !important; }
    .agent-card {
        background: #16213e;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 12px;
        border: 1px solid #2a2a4e;
    }
    .agent-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        margin-right: 6px;
    }
    .round-badge {
        background: #2a2a4e;
        color: #888;
        font-size: 11px;
        padding: 2px 8px;
        border-radius: 4px;
    }
    .reasoning-box {
        background: #0e1428;
        border-left: 3px solid #7B68EE;
        padding: 10px 14px;
        border-radius: 0 6px 6px 0;
        margin-top: 8px;
        font-size: 13px;
        line-height: 1.6;
        color: #d0d0f0;
    }
    .stat-pill {
        display: inline-block;
        background: #2a2a4e;
        border-radius: 12px;
        padding: 2px 10px;
        font-size: 11px;
        color: #aaa;
        margin: 4px 3px 0 0;
    }
    hr { border-color: #2a2a4e !important; }
    label { color: #aaa !important; font-size: 12px !important; }
</style>
""", unsafe_allow_html=True)

# ── Carga de datos ─────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    log_global    = "resultados/logs/log.csv"
    log_jugadores = "resultados/logs/log_jugadores.csv"
    df_global     = pd.read_csv(log_global)    if os.path.exists(log_global)    else None
    df_jugadores  = pd.read_csv(log_jugadores) if os.path.exists(log_jugadores) else None
    return df_global, df_jugadores

df_global, df_jugadores = cargar_datos()

if df_global is None:
    st.error("No se encontraron logs. Ejecuta primero `main.py` para generar una simulacion.")
    st.stop()

# ── SIDEBAR ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧬 Cooperacion y Honor")
    st.caption("Simulacion de Fenotipos con LLM")
    st.divider()

    vista = st.radio("", [
        "📊  Resumen global",
        "🔬  Evolucion de fenotipos",
        "🏅  Sistema de honor",
        "🤖  Agente individual",
        "🧠  Visor de razonamientos",
        "🎞️  Frames de la reticula",
    ], label_visibility="collapsed")

    st.divider()
    pasos_total = df_global["paso"].max()
    st.metric("Pasos simulados", pasos_total + 1)
    if df_jugadores is not None:
        st.metric("Agentes", df_jugadores["id"].nunique())
        if "fenotipo" in df_jugadores.columns:
            ultimo_paso = df_jugadores[df_jugadores["paso"] == pasos_total]
            for f, label in ETIQUETAS.items():
                n = (ultimo_paso["fenotipo"] == f).sum()
                if n > 0:
                    color = COLORES[f]
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:8px;margin:3px 0;">'
                        f'<div style="width:10px;height:10px;border-radius:2px;'
                        f'background:{color};flex-shrink:0;"></div>'
                        f'<span style="font-size:12px;color:#aaa;">{label}: '
                        f'<b style="color:#e0e0e0;">{n}</b></span></div>',
                        unsafe_allow_html=True
                    )


# ── Helpers matplotlib ─────────────────────────────────────────
def _base_fig(w=10, h=4.5):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(FONDO)
    _estilizar_ax(ax)
    return fig, ax

def _base_fig_multi(nrows, ncols, w=14, h=5):
    fig, axes = plt.subplots(nrows, ncols, figsize=(w, h))
    fig.patch.set_facecolor(FONDO)
    for ax in (axes.flat if hasattr(axes, "flat") else [axes]):
        _estilizar_ax(ax)
    return fig, axes

def _estilizar_ax(ax):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=TEXTO, labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor('#2a2a4e')
    ax.xaxis.label.set_color(TEXTO)
    ax.yaxis.label.set_color(TEXTO)
    ax.title.set_color(TEXTO)
    ax.grid(True, color=GRID, linewidth=0.5, alpha=0.7, linestyle='--')

def _etiqueta_final(ax, x_series, y_series, label, color, x_max_factor=1.20):
    """Etiqueta inline al final de la linea."""
    if len(x_series) == 0:
        return
    x_last = x_series.iloc[-1] if hasattr(x_series, 'iloc') else x_series[-1]
    y_last = y_series.iloc[-1] if hasattr(y_series, 'iloc') else y_series[-1]
    ax.annotate(
        f"  {label}",
        xy=(x_last, y_last),
        color=color,
        fontsize=8.5,
        va='center',
        fontweight='bold',
    )


# ─────────────────────────────────────────────────────────────
# VISTA: Resumen global
# ─────────────────────────────────────────────────────────────
if vista.endswith("Resumen global"):
    st.markdown("## Resumen de la simulacion")

    coop_final = df_global['cooperacion_global'].iloc[-1]
    coop_max   = df_global['cooperacion_global'].max()
    coop_media = df_global['cooperacion_global'].mean()
    delta_str  = f"{coop_final - df_global['cooperacion_global'].iloc[0]:+.1%}"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cooperacion final",  f"{coop_final:.1%}", delta_str)
    c2.metric("Cooperacion maxima", f"{coop_max:.1%}")
    c3.metric("Cooperacion media",  f"{coop_media:.1%}")
    if df_jugadores is not None and "fenotipo" in df_jugadores.columns:
        ultimo = df_jugadores[df_jugadores['paso'] == df_global['paso'].max()]
        dominante = ultimo['fenotipo'].value_counts().idxmax() if not ultimo.empty else "—"
        c4.metric("Fenotipo dominante", ETIQUETAS.get(dominante, dominante))

    st.divider()

    # Cooperacion global
    fig, ax = _base_fig(10, 3.8)
    pasos = df_global['paso']
    coop  = df_global['cooperacion_global']
    ax.plot(pasos, coop, color=VERDE, linewidth=2.2, zorder=3)
    ax.fill_between(pasos, coop, alpha=0.12, color=VERDE)
    idx_max = coop.idxmax()
    ax.annotate(
        f"max {coop[idx_max]:.0%}",
        xy=(pasos[idx_max], coop[idx_max]),
        xytext=(0, 10), textcoords='offset points',
        color=VERDE, fontsize=8, ha='center',
        arrowprops=dict(arrowstyle='->', color=VERDE, lw=0.8)
    )
    ax.annotate(f"  {coop.iloc[-1]:.0%}", xy=(pasos.iloc[-1], coop.iloc[-1]),
                color=VERDE, fontsize=9, va='center', fontweight='bold')
    ax.set_xlim(right=pasos.max() * 1.12)
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0, decimals=0))
    ax.set_title('Evolucion de la cooperacion global', fontsize=11, pad=10)
    ax.set_xlabel('Paso', fontsize=9)
    ax.set_ylabel('phi(t)', fontsize=9)
    plt.tight_layout(pad=1.5)
    st.pyplot(fig)

    if df_jugadores is not None and 'rep_pos' in df_jugadores.columns:
        st.divider()
        st.markdown("#### Reputacion media por fenotipo")
        fig, (ax1, ax2) = _base_fig_multi(1, 2, 14, 4)
        x_max = df_jugadores['paso'].max()

        for f, c in COLORES.items():
            sub = df_jugadores[df_jugadores['fenotipo'] == f]
            if sub.empty:
                continue
            mp = sub.groupby('paso')['rep_pos'].mean()
            mn = sub.groupby('paso')['rep_neg'].mean()
            ax1.plot(mp.index, mp.values, color=c, linewidth=1.8)
            ax2.plot(mn.index, mn.values, color=c, linewidth=1.8)
            if len(mp):
                _etiqueta_final(ax1, mp.index, mp.values, ETIQUETAS[f], c)
            if len(mn):
                _etiqueta_final(ax2, mn.index, mn.values, ETIQUETAS[f], c)

        for ax, titulo in [(ax1, 'Reputacion positiva media'), (ax2, 'Reputacion negativa media')]:
            ax.set_ylim(0, 1)
            ax.set_xlim(right=x_max * 1.25)
            ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0, decimals=0))
            ax.set_title(titulo, fontsize=10, pad=8)
            ax.set_xlabel('Paso', fontsize=9)

        plt.tight_layout(pad=1.5)
        st.pyplot(fig)


# ─────────────────────────────────────────────────────────────
# VISTA: Evolucion de fenotipos
# ─────────────────────────────────────────────────────────────
elif vista.endswith("Evolucion de fenotipos"):
    st.markdown("## Evolucion de la proporcion de fenotipos")

    fig, ax = _base_fig(11, 5)
    x_max = df_global['paso'].max()

    for f, c in COLORES.items():
        if f not in df_global.columns:
            continue
        y = df_global[f]
        ax.plot(df_global['paso'], y, color=c, linewidth=2.2, zorder=3)
        ax.fill_between(df_global['paso'], y, alpha=0.07, color=c)
        _etiqueta_final(ax, df_global['paso'], y, ETIQUETAS[f], c)

    ax.set_xlim(right=x_max * 1.22)
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0, decimals=0))
    ax.set_title('Proporcion de cada fenotipo por ronda', fontsize=11, pad=10)
    ax.set_xlabel('Paso', fontsize=9)
    ax.set_ylabel('Proporcion', fontsize=9)
    plt.tight_layout(pad=1.5)
    st.pyplot(fig)

    if df_jugadores is not None and 'cambio_fenotipo' in df_jugadores.columns:
        st.divider()
        st.markdown("#### Cambios de fenotipo por ronda")
        cambios = df_jugadores.groupby('paso')['cambio_fenotipo'].sum()
        fig2, ax2 = _base_fig(10, 3)
        bars = ax2.bar(cambios.index, cambios.values, color=ACCENT, alpha=0.75, width=0.8, zorder=3)
        umbral = cambios.mean() + cambios.std()
        for bar, val in zip(bars, cambios.values):
            if val >= umbral:
                bar.set_color('#F28E2B')
                bar.set_alpha(0.9)
        ax2.axhline(cambios.mean(), color='#888', linewidth=1, linestyle='--', alpha=0.6)
        ax2.annotate(f"  media {cambios.mean():.1f}", xy=(cambios.index[-1], cambios.mean()),
                     color='#888', fontsize=8, va='center')
        ax2.set_title('Cambios de fenotipo por ronda', fontsize=11, pad=10)
        ax2.set_xlabel('Paso', fontsize=9)
        ax2.set_ylabel('N cambios', fontsize=9)
        ax2.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        plt.tight_layout(pad=1.5)
        st.pyplot(fig2)


# ─────────────────────────────────────────────────────────────
# VISTA: Sistema de honor
# ─────────────────────────────────────────────────────────────
elif vista.endswith("Sistema de honor"):
    st.markdown("## Sistema de honor bidireccional")

    if df_jugadores is None or 'rep_pos' not in df_jugadores.columns:
        st.warning("No hay datos de reputacion. Asegurate de usar el logger_jugadores actualizado.")
        st.stop()

    paso_sel = st.slider("Selecciona ronda", 0, int(df_global['paso'].max()), 0)
    df_paso = df_jugadores[df_jugadores['paso'] == paso_sel]

    st.markdown(f"#### Distribucion de reputacion — Ronda {paso_sel}")
    c1, c2 = st.columns(2)

    for col, campo, titulo in [
        (c1, 'rep_pos', 'Reputacion positiva (Rep+)'),
        (c2, 'rep_neg', 'Reputacion negativa (Rep-)'),
    ]:
        with col:
            fig, ax = _base_fig(6, 3.8)
            for f, c in COLORES.items():
                sub = df_paso[df_paso['fenotipo'] == f]
                if not sub.empty:
                    ax.hist(sub[campo], bins=10, alpha=0.55,
                            color=c, label=ETIQUETAS[f], range=(0, 1), zorder=3)
            ax.set_title(titulo, fontsize=10, pad=8)
            ax.set_xlabel('Valor', fontsize=9)
            ax.set_ylabel('N agentes', fontsize=9)
            ax.set_xlim(0, 1)
            leg = ax.legend(fontsize=7, facecolor='#2a2a3e', labelcolor='white',
                            edgecolor='#444', loc='upper center',
                            ncol=3, framealpha=0.85)
            plt.tight_layout(pad=1.5)
            st.pyplot(fig)

    st.divider()
    st.markdown("#### Mapa de reputacion — todos los agentes")
    fig, ax = _base_fig(8, 5)
    for f, c in COLORES.items():
        sub = df_paso[df_paso['fenotipo'] == f]
        if not sub.empty:
            ax.scatter(sub['rep_pos'], sub['rep_neg'], color=c, alpha=0.75,
                       s=50, label=ETIQUETAS[f], zorder=3, edgecolors='none')
    ax.plot([0, 1], [0, 1], color='#444', linewidth=1, linestyle='--', alpha=0.5)
    ax.fill_between([0, 1], [0, 0], [0, 1], alpha=0.04, color=ROJO)
    ax.fill_between([0, 1], [0, 1], [1, 1], alpha=0.04, color=VERDE)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xlabel('Rep+  (cooperacion)', fontsize=9)
    ax.set_ylabel('Rep-  (defeccion)', fontsize=9)
    ax.set_title('Posicion de cada agente en el espacio de honor', fontsize=10, pad=8)
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(1.0, decimals=0))
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0, decimals=0))
    ax.text(0.03, 0.93, 'zona deshonrada', color=ROJO, fontsize=8, alpha=0.8, transform=ax.transAxes)
    ax.text(0.60, 0.05, 'zona honrada', color=VERDE, fontsize=8, alpha=0.8, transform=ax.transAxes)
    leg = ax.legend(fontsize=8, facecolor='#2a2a3e', labelcolor='white',
                    edgecolor='#444', loc='upper right', framealpha=0.85)
    plt.tight_layout(pad=1.5)
    st.pyplot(fig)

    st.divider()
    st.markdown("#### Top agentes mas honrados y mas deshonrados")
    t1, t2 = st.columns(2)
    cols_tabla = [c for c in ['id', 'fenotipo', 'rep_pos', 'rep_neg', 'estrategia'] if c in df_paso.columns]
    with t1:
        st.markdown("**Mas honrados — rep+ alta**")
        st.dataframe(df_paso.nlargest(5, 'rep_pos')[cols_tabla], hide_index=True)
    with t2:
        st.markdown("**Mas deshonrados — rep- alta**")
        st.dataframe(df_paso.nlargest(5, 'rep_neg')[cols_tabla], hide_index=True)


# ─────────────────────────────────────────────────────────────
# VISTA: Agente individual
# ─────────────────────────────────────────────────────────────
elif vista.endswith("Agente individual"):
    st.markdown("## Trayectoria de un agente")

    if df_jugadores is None:
        st.warning("No hay datos de jugadores.")
        st.stop()

    ids = sorted(df_jugadores['id'].unique())
    jugador_id = st.selectbox("Selecciona agente", ids)
    jugador_df = df_jugadores[df_jugadores['id'] == jugador_id]

    fenotipo_final = jugador_df['fenotipo'].iloc[-1]
    pago_medio     = jugador_df['pago'].mean()     if 'pago' in jugador_df.columns else 0
    cambios        = jugador_df['cambio_fenotipo'].sum() if 'cambio_fenotipo' in jugador_df.columns else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Fenotipo final",    ETIQUETAS.get(fenotipo_final, fenotipo_final))
    c2.metric("Pago medio",        f"{pago_medio:.2f}")
    c3.metric("Cambios fenotipo",  int(cambios))
    if 'rep_pos' in jugador_df.columns:
        c4.metric("Rep+ final", f"{jugador_df['rep_pos'].iloc[-1]:.2f}")

    # Pago
    fig, ax = _base_fig(10, 3.5)
    x_max = jugador_df['paso'].max()
    for f, grupo in jugador_df.groupby('fenotipo'):
        ax.plot(grupo['paso'], grupo['pago'], marker='o', markersize=3,
                linestyle='-', linewidth=1.8, color=COLORES.get(f, 'gray'), zorder=3)
        _etiqueta_final(ax, grupo['paso'], grupo['pago'], ETIQUETAS.get(f, f), COLORES.get(f, 'gray'))
    ax.set_xlim(right=x_max * 1.22)
    ax.set_title(f'Pago acumulado — Agente {jugador_id}', fontsize=11, pad=8)
    ax.set_xlabel('Paso', fontsize=9)
    ax.set_ylabel('Pago', fontsize=9)
    plt.tight_layout(pad=1.5)
    st.pyplot(fig)

    # Honor
    if 'rep_pos' in jugador_df.columns:
        fig, ax = _base_fig(10, 3.5)
        ax.plot(jugador_df['paso'], jugador_df['rep_pos'], color=VERDE, linewidth=2.2, zorder=3)
        ax.plot(jugador_df['paso'], jugador_df['rep_neg'], color=ROJO,  linewidth=2.2, zorder=3)
        ax.fill_between(jugador_df['paso'], jugador_df['rep_pos'], jugador_df['rep_neg'],
                        where=jugador_df['rep_pos'] >= jugador_df['rep_neg'], alpha=0.10, color=VERDE)
        ax.fill_between(jugador_df['paso'], jugador_df['rep_pos'], jugador_df['rep_neg'],
                        where=jugador_df['rep_pos'] < jugador_df['rep_neg'], alpha=0.10, color=ROJO)
        _etiqueta_final(ax, jugador_df['paso'], jugador_df['rep_pos'], 'Rep+', VERDE)
        _etiqueta_final(ax, jugador_df['paso'], jugador_df['rep_neg'], 'Rep-', ROJO)
        ax.set_xlim(right=jugador_df['paso'].max() * 1.15)
        ax.set_ylim(0, 1)
        ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0, decimals=0))
        ax.set_title(f'Honor — Agente {jugador_id}', fontsize=11, pad=8)
        ax.set_xlabel('Paso', fontsize=9)
        ax.set_ylabel('Reputacion', fontsize=9)
        plt.tight_layout(pad=1.5)
        st.pyplot(fig)

    # Historial decisiones
    if 'estrategia' in jugador_df.columns:
        st.divider()
        st.markdown("#### Historial de decisiones")
        dec_counts = jugador_df['estrategia'].value_counts()
        total = len(jugador_df)
        n_c = dec_counts.get('C', 0)
        n_d = dec_counts.get('D', 0)
        col_c, col_d = st.columns(2)
        col_c.metric("Cooperaciones", n_c, f"{n_c/total:.0%} del total")
        col_d.metric("Defecciones",   n_d, f"{n_d/total:.0%} del total")


# ─────────────────────────────────────────────────────────────
# VISTA: Visor de razonamientos  (con filtro por jugador)
# ─────────────────────────────────────────────────────────────
elif vista.endswith("Visor de razonamientos"):
    st.markdown("## El Pensamiento del Agente")
    st.caption("Explora el razonamiento detras de cada movimiento — filtra por jugador, fenotipo o decision")

    if df_jugadores is None or 'justif_llm' not in df_jugadores.columns:
        st.warning("No hay justificaciones en el log. Asegurate de que el LLM este guardando 'justif_llm'.")
        st.stop()

    df_justif = df_jugadores[
        df_jugadores['justif_llm'].notna() &
        ~df_jugadores['justif_llm'].str.startswith('[fallback', na=False)
    ].copy()

    # ── FILTROS ─────────────────────────────────────────────────
    with st.expander("Filtros", expanded=True):
        fc1, fc2, fc3, fc4 = st.columns(4)

        ids_disponibles = sorted(df_justif['id'].unique().tolist())
        jugador_filtro = fc1.selectbox(
            "Jugador",
            ['Todos'] + ids_disponibles,
            help="Filtra por ID para seguir la trayectoria completa de un agente"
        )

        fenotipos_disponibles = sorted(df_justif['fenotipo'].unique().tolist())
        fenotipo_filtro = fc2.selectbox(
            "Fenotipo",
            ['Todos'] + fenotipos_disponibles,
            format_func=lambda x: ETIQUETAS.get(x, x) if x != 'Todos' else 'Todos'
        )

        decision_filtro = fc3.selectbox(
            "Decision",
            ['Todas', 'C', 'D'],
            format_func=lambda x: {'Todas': 'Todas', 'C': 'Cooperar', 'D': 'Defectar'}[x]
        )

        paso_max = int(df_global['paso'].max())
        paso_filtro = fc4.slider("Rondas", 0, paso_max, (0, paso_max))

    # ── APLICAR FILTROS ─────────────────────────────────────────
    df_f = df_justif[
        (df_justif['paso'] >= paso_filtro[0]) &
        (df_justif['paso'] <= paso_filtro[1])
    ].copy()

    if jugador_filtro != 'Todos':
        df_f = df_f[df_f['id'] == jugador_filtro]
    if fenotipo_filtro != 'Todos':
        df_f = df_f[df_f['fenotipo'] == fenotipo_filtro]
    if decision_filtro != 'Todas':
        df_f = df_f[df_f['estrategia'] == decision_filtro]

    n_total = len(df_f)

    # ── STATS ────────────────────────────────────────────────────
    sc1, sc2, sc3, sc4 = st.columns(4)
    sc1.metric("Razonamientos", n_total)
    if n_total > 0 and 'estrategia' in df_f.columns:
        n_c = (df_f['estrategia'] == 'C').sum()
        sc2.metric("Cooperaciones", n_c, f"{n_c/n_total:.0%}")
        sc3.metric("Defecciones", n_total - n_c, f"{(n_total-n_c)/n_total:.0%}")
    if n_total > 0 and 'rep_pos' in df_f.columns:
        sc4.metric("Rep+ media", f"{df_f['rep_pos'].mean():.2f}")

    # ── MINI TRAYECTORIA si hay jugador seleccionado ─────────────
    if jugador_filtro != 'Todos' and n_total > 0:
        traj = df_justif[df_justif['id'] == jugador_filtro].sort_values('paso')
        with st.expander(f"Trayectoria del agente {jugador_filtro}", expanded=False):
            c_graf, c_info = st.columns([2, 1])
            with c_graf:
                if 'rep_pos' in traj.columns:
                    fig, ax = _base_fig(7, 2.8)
                    ax.plot(traj['paso'], traj['rep_pos'], color=VERDE, linewidth=1.8)
                    ax.plot(traj['paso'], traj['rep_neg'], color=ROJO,  linewidth=1.8)
                    ax.fill_between(traj['paso'], traj['rep_pos'], traj['rep_neg'],
                                    where=traj['rep_pos'] >= traj['rep_neg'], alpha=0.10, color=VERDE)
                    ax.fill_between(traj['paso'], traj['rep_pos'], traj['rep_neg'],
                                    where=traj['rep_pos'] < traj['rep_neg'],  alpha=0.10, color=ROJO)
                    ax.set_ylim(0, 1)
                    ax.set_xlim(right=traj['paso'].max() * 1.18)
                    _etiqueta_final(ax, traj['paso'], traj['rep_pos'], 'Rep+', VERDE)
                    _etiqueta_final(ax, traj['paso'], traj['rep_neg'], 'Rep-', ROJO)
                    ax.set_title(f'Honor — {jugador_filtro}', fontsize=9, pad=6)
                    plt.tight_layout(pad=1.2)
                    st.pyplot(fig)
            with c_info:
                fnts_vistos = traj['fenotipo'].unique()
                st.markdown("**Fenotipos en la simulacion:**")
                for f in fnts_vistos:
                    color = COLORES.get(f, '#888')
                    n_rounds = (traj['fenotipo'] == f).sum()
                    st.markdown(
                        f'<span style="color:{color};font-weight:bold;">{ETIQUETAS.get(f,f)}</span>'
                        f' <span style="color:#888;font-size:12px;">— {n_rounds} rondas</span>',
                        unsafe_allow_html=True
                    )
                if 'pago' in traj.columns:
                    st.markdown(f"**Pago final:** `{traj['pago'].iloc[-1]:.2f}`")
                    st.markdown(f"**Pago medio:** `{traj['pago'].mean():.2f}`")
                if 'estrategia' in traj.columns:
                    n_c = (traj['estrategia'] == 'C').sum()
                    total = len(traj)
                    st.markdown(f"**Coopero:** `{n_c}/{total}` (`{n_c/total:.0%}`)")

    st.divider()

    if n_total == 0:
        st.info("No hay razonamientos con los filtros seleccionados.")
        st.stop()

    st.markdown(f"Mostrando **{min(50, n_total)}** de **{n_total}** razonamientos — mas recientes primero")

    # ── CARDS DE RAZONAMIENTO ────────────────────────────────────
    df_render = df_f.sort_values(by=['paso', 'id'], ascending=[False, True]).head(50)

    for _, row in df_render.iterrows():
        color   = COLORES.get(row['fenotipo'], '#888')
        es_coop = str(row.get('estrategia', 'C')) == 'C'
        emoji   = "🤝" if es_coop else "🗡️"
        dec_lbl = "COOPERO" if es_coop else "DEFECTO"
        dec_col = VERDE if es_coop else ROJO

        rep_pos = row.get('rep_pos', None)
        rep_neg = row.get('rep_neg', None)
        pago    = row.get('pago', None)

        pills = ""
        if rep_pos is not None:
            pills += f'<span class="stat-pill">Rep+ {float(rep_pos):.2f}</span>'
        if rep_neg is not None:
            pills += f'<span class="stat-pill">Rep- {float(rep_neg):.2f}</span>'
        if pago is not None:
            pills += f'<span class="stat-pill">Pago {float(pago):.2f}</span>'

        justif = str(row.get('justif_llm', '')).strip()

        st.markdown(f"""
<div class="agent-card">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;flex-wrap:wrap;">
    <span class="round-badge">Ronda {int(row['paso'])}</span>
    <span style="font-weight:700;color:#e0e0e0;">Agente {row['id']}</span>
    <span class="agent-badge" style="background:{color}22;color:{color};border:1px solid {color}55;">
      {ETIQUETAS.get(row['fenotipo'], row['fenotipo'])}
    </span>
    <span style="font-size:13px;color:{dec_col};font-weight:600;">{emoji} {dec_lbl}</span>
  </div>
  <div class="reasoning-box">{justif}</div>
  <div style="margin-top:8px;">{pills}</div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# VISTA: Frames de la reticula
# ─────────────────────────────────────────────────────────────
elif vista.endswith("Frames de la reticula"):
    st.markdown("## Visor de frames")

    frames = sorted(glob.glob("img/frames/frame_*.png"))
    if not frames:
        st.warning("No hay frames generados. Ejecuta `main.py` primero.")
        st.stop()

    paso_frame = st.slider("Ronda", 0, len(frames) - 1, 0)

    col_img, col_info = st.columns([3, 1])
    with col_img:
        st.image(frames[paso_frame], use_column_width=True)
        st.caption(f"Frame {paso_frame + 1} de {len(frames)}")

    with col_info:
        st.markdown("#### Leyenda de canales")
        st.markdown("""
<div style="font-size:12px;color:#aaa;line-height:2.0;">

<b>Canal 1 — Color de fondo</b><br>
<span style="color:#59A14F">■</span> Altruista &nbsp;
<span style="color:#E15759">■</span> Envidioso<br>
<span style="color:#F28E2B">■</span> Optimista &nbsp;
<span style="color:#4E79A7">■</span> Pesimista<br>
<span style="color:#B07AA1">■</span> Aleatorio

<br><b>Canal 2 — Borde exterior</b><br>
<span style="color:#27AE60">□</span> Rep+ alta (≥ 0.7) — honrado<br>
<span style="color:#E74C3C">□</span> Rep– alta (≥ 0.7) — deshonrado<br>
□ Rep neutral

<br><b>Canal 3 — Brillo / alfa</b><br>
Opacidad proporcional a Rep+<br>
Agentes deshonrados se "apagan"

<br><b>Canal 4 — Punto central</b><br>
⚪ Coopero esta ronda<br>
⚫ Defecto esta ronda

</div>
""", unsafe_allow_html=True)

    gif_path = "img/simulacion.gif"
    if os.path.exists(gif_path):
        st.divider()
        st.markdown("#### GIF completo de la simulacion")
        st.image(gif_path)
