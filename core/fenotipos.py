import random

def decidir_estrategia(fenotipo, T, S):
    if fenotipo == 'E':  # Envidioso
        return 'C' if S > T else 'D'
    elif fenotipo == 'O':  # Optimista
        return 'C' if T < 1 else 'D'
    elif fenotipo == 'P':  # Pesimista
        return 'C' if S > 0 else 'D'
    elif fenotipo == 'A':  # Altruista
        return 'C'
    elif fenotipo == 'R':  # Aleatorio
        return random.choice(['C', 'D'])
    else:
        raise ValueError(f"Fenotipo desconocido: {fenotipo}")
