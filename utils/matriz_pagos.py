# utils/matriz_pagos.py

def calcular_pagos_lineales(paso, total_pasos):
    T = 2 - (2 * paso / (total_pasos - 1))
    S = 1 - (2 * paso / (total_pasos - 1))
    return T, S
