# ============================================================
#  main.py
#  Simulación con agentes LLM + sistema de honor
#  Cambios respecto al original:
#    1. decidir_estrategia recibe vecino + contexto social
#    2. actualizar_reputacion al final de cada ronda
#    3. phi_local y tendencia calculados antes de decidir
#    4. El resto del flujo es idéntico al original
# ============================================================

import pandas as pd

from config.parametros import *
from core.reticula_nx  import ReticulaNX, graficar_y_guardar_fenotipos, crear_gif
from core.juego        import simular_juego
from utils.crear_estructura   import crear_estructura
from utils.metricas           import f_estrategia
from utils.logger             import inicializar_logger, registrar_estado
from utils.logger_jugadores   import (inicializar_logger_jugadores,
                                      registrar_estado_jugadores)
from utils.visualizacion      import (graficar_resultados_globales,
                                      graficar_rendimiento_jugador)
from utils.resize_imagenes    import pad_imagenes_en_carpeta
from utils.matriz_pagos       import calcular_pagos_lineales

crear_estructura()
inicializar_logger()
inicializar_logger_jugadores()

# ── PARÁMETROS DEL MODELO ────────────────────────────────────
parametros = {
    "Pasos":  pasos,
    "K1":     K1,
    "K2":     K2,
    "τD":     tau_limites[0],
    "τU":     tau_limites[1],
    "L":      L,
    "Modo LLM": MODO_LLM,
    "Alpha rep": ALPHA_REPUTACION,
    "Distribucion": [
        f"Envidioso = {int(round(distrib_fenotipos['E']*100,0))}%",
        f"Pesimista = {int(round(distrib_fenotipos['P']*100,0))}%",
        f"Optimista = {int(round(distrib_fenotipos['O']*100,0))}%",
        f"Altruista = {int(round(distrib_fenotipos['A']*100,0))}%",
        f"Aleatorio = {int(round(distrib_fenotipos['R']*100,0))}%"
    ]
}

# ── INICIALIZACIÓN DE LA RETÍCULA ────────────────────────────
reticula = ReticulaNX(L, distrib_fenotipos, tau_limites)

# ── SIMULACIÓN ───────────────────────────────────────────────
graficar_y_guardar_fenotipos(reticula, paso=0,
                              parametros=parametros,
                              carpeta='img/frames')

for t in range(pasos):
    print(f"--- Paso {t + 1}/{pasos} ---")

    # Reiniciar pagos
    for nodo in reticula.nodos():
        reticula.G.nodes[nodo]['jugador'].reiniciar_pago()

    T, S = calcular_pagos_lineales(t, pasos)

    # ── NUEVO: calcular phi_local y tendencia por agente ─────
    # (necesario para construir el user prompt antes de decidir)
    for nodo in reticula.nodos():
        jugador = reticula.G.nodes[nodo]['jugador']
        vecinos_obj = [
            reticula.G.nodes[v]['jugador']
            for v in reticula.vecinos(nodo)
        ]
        # phi_local como media de rep_pos de los vecinos
        if vecinos_obj:
            phi_local = sum(v.rep_pos for v in vecinos_obj) / len(vecinos_obj)
        else:
            phi_local = 0.5

        tendencia = phi_local - jugador._phi_local_prev
        jugador._phi_local_prev = phi_local

        # Guardar en el jugador para usar en decidir_estrategia
        jugador._phi_local_actual    = phi_local
        jugador._tendencia_phi_actual = tendencia

    # ── Decidir estrategias (cada agente vs su primer vecino) ─
    # NOTA: en el original se decidía sin vecino concreto.
    # Aquí decidimos una vez por agente usando el primer vecino
    # como referencia para el prompt. El juego se sigue jugando
    # contra todos los vecinos con la estrategia resultante.
    for nodo in reticula.nodos():
        jugador = reticula.G.nodes[nodo]['jugador']
        vecinos_nodo = list(reticula.vecinos(nodo))
        if not vecinos_nodo:
            continue
        # Usar el vecino con quien más historial tenemos
        vecino_ref_id = max(
            vecinos_nodo,
            key=lambda v: jugador.resumen_vecinos.get(
                reticula.G.nodes[v]['jugador'].id,
                type('obj', (object,), {'n': 0})()
            ).n
        )
        vecino_ref = reticula.G.nodes[vecino_ref_id]['jugador']

        jugador.decidir_estrategia(
            vecino        = vecino_ref,
            T             = T,
            S             = S,
            paso          = t,
            pasos_total   = pasos,
            phi_local     = jugador._phi_local_actual,
            tendencia_phi = jugador._tendencia_phi_actual
        )

    # ── Simular juegos entre pares (igual que antes) ──────────
    jugadas = set()
    for nodo in reticula.nodos():
        jugador = reticula.G.nodes[nodo]['jugador']
        for vecino_nodo in reticula.vecinos(nodo):
            par = tuple(sorted([nodo, vecino_nodo]))
            if par not in jugadas:
                vecino = reticula.G.nodes[vecino_nodo]['jugador']
                simular_juego(jugador, vecino, T, S)
                jugadas.add(par)

    # ── Calcular phi_global ───────────────────────────────────
    total_coop = sum(
        f_estrategia(reticula.G.nodes[n]['jugador'].estrategia)
        for n in reticula.nodos()
    )
    phi_global = total_coop / (L * L)

    # ── NUEVO: actualizar reputación tras el juego ────────────
    for nodo in reticula.nodos():
        jugador = reticula.G.nodes[nodo]['jugador']
        jugador.actualizar_reputacion(jugador.estrategia == 'C')

    # ── Ajustar tau (igual que antes) ─────────────────────────
    for nodo in reticula.nodos():
        jugador = reticula.G.nodes[nodo]['jugador']
        vecinos_obj = [
            reticula.G.nodes[v]['jugador']
            for v in reticula.vecinos(nodo)
        ]
        suma_local = sum(f_estrategia(v.estrategia) for v in vecinos_obj)
        phi_local  = suma_local / len(vecinos_obj) if vecinos_obj else 0.5
        jugador.ajustar_tau(phi_local, phi_global, delta_tau, K1)

    # ── Considerar cambio de fenotipo (igual que antes) ───────
    for nodo in reticula.nodos():
        jugador = reticula.G.nodes[nodo]['jugador']
        jugador.vecinos = [
            reticula.G.nodes[v]['jugador']
            for v in reticula.vecinos(nodo)
        ]
        jugador.considerar_cambio_de_fenotipo(K2)

    # ── Guardar frame y logs ───────────────────────────────────
    graficar_y_guardar_fenotipos(reticula, paso=t,
                                  parametros=parametros,
                                  carpeta='img/frames')
    registrar_estado(reticula, paso=t)
    registrar_estado_jugadores(reticula, paso=t)

# ── CREAR GIF ─────────────────────────────────────────────────
pad_imagenes_en_carpeta(carpeta='img/frames')
crear_gif(carpeta='img/frames',
          nombre_salida='simulacion.gif', fps=5)

# ── GRAFICAR RESULTADOS ───────────────────────────────────────
graficar_resultados_globales()

jugadores_df = pd.read_csv('resultados/logs/log_jugadores.csv')
for jugador_id in jugadores_df['id'].unique():
    graficar_rendimiento_jugador(jugador_id=jugador_id)

print("\n✅ Simulación completada.")
