# ============================================================
#  utils/logger_jugadores.py
#  Igual que el original + columnas rep_pos, rep_neg, justif_llm
# ============================================================

import csv
import os


def inicializar_logger_jugadores(
        path="resultados/logs/log_jugadores.csv"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'paso', 'id', 'fenotipo', 'cambio_fenotipo',
            'estrategia', 'pago', 'tau', 'theta',
            'rep_pos', 'rep_neg',   # NUEVO
            'justif_llm'            # NUEVO
        ])


def registrar_estado_jugadores(
        reticula, paso,
        path="resultados/logs/log_jugadores.csv"):
    with open(path, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for nodo in reticula.nodos():
            j = reticula.G.nodes[nodo]['jugador']
            cambio = int(
                j.fenotipo != getattr(j, 'fenotipo_anterior', j.fenotipo)
            )
            writer.writerow([
                paso,
                j.id,
                j.fenotipo,
                cambio,
                j.estrategia,
                round(j.pago_acumulado, 3),
                j.tau,
                j.theta,
                round(getattr(j, 'rep_pos', 0.5), 3),   # NUEVO
                round(getattr(j, 'rep_neg', 0.5), 3),   # NUEVO
                getattr(j, 'justif_llm', '')             # NUEVO
            ])
            j.fenotipo_anterior = j.fenotipo
