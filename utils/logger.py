import csv
import os
from collections import Counter
from .metricas import f_estrategia

def inicializar_logger(path="resultados/logs/log.csv"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode='w', newline='') as archivo:
        writer = csv.writer(archivo)
        writer.writerow([
            'paso', 'cooperacion_global', 
            'E', 'P', 'O', 'A', 'R'
        ])

def registrar_estado(reticula, paso, path="resultados/logs/log.csv"):
    G = reticula.G
    nodos = list(G.nodes)
    N = len(nodos)

    # Fenotipos
    fenotipos = [G.nodes[n]['jugador'].fenotipo for n in nodos]
    conteo = Counter(fenotipos)

    # Cooperación global
    estrategias = [G.nodes[n]['jugador'].estrategia for n in nodos]
    coop = sum(f_estrategia(e) for e in estrategias) / N

    # Guardar datos
    fila = [
        paso, round(coop, 4),
        conteo.get('E', 0) / N,
        conteo.get('P', 0) / N,
        conteo.get('O', 0) / N,
        conteo.get('A', 0) / N,
        conteo.get('R', 0) / N
    ]

    with open(path, mode='a', newline='') as archivo:
        writer = csv.writer(archivo)
        writer.writerow(fila)
