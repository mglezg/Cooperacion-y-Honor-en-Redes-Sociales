# ============================================================
#  utils/prompt_builder.py
#  Construye el user prompt situacional para cada decisión.
#  Coste fijo ~100 tokens por llamada independientemente
#  de cuántas rondas lleve la simulación.
# ============================================================

import numpy as np
from config.parametros import SIGMA_PERCEPCION


def percibir_reputacion(jugador):
    """
    Devuelve (rep_pos, rep_neg) del jugador tal como las
    percibe un vecino: con ruido gaussiano ±SIGMA_PERCEPCION.
    Resultado siempre acotado a [0, 1].
    """
    sigma = SIGMA_PERCEPCION
    rep_pos = float(np.clip(
        jugador.rep_pos + np.random.normal(0, sigma), 0.0, 1.0
    ))
    rep_neg = float(np.clip(
        jugador.rep_neg + np.random.normal(0, sigma), 0.0, 1.0
    ))
    return round(rep_pos, 2), round(rep_neg, 2)


def resumen_historial(jugador, id_vecino: str) -> str:
    """
    Devuelve una línea compacta (~35 tokens) lista para el prompt.
    Nunca crece aunque la simulación lleve 1000 rondas.
    """
    res = jugador.resumen_vecinos.get(id_vecino)
    if res is None or res.n == 0:
        return "Sin historial previo con este vecino."

    if res.racha_el > 0:
        racha_str = f"lleva {res.racha_el} rondas cooperando seguidas"
    elif res.racha_el < 0:
        racha_str = f"lleva {abs(res.racha_el)} rondas traicionando seguidas"
    else:
        racha_str = "su última decisión fue mixta"

    return (
        f"Historial ({res.n} rondas): "
        f"yo cooperé {int(res.coop_yo * 100)}% | "
        f"él cooperó {int(res.coop_el * 100)}% | "
        f"{racha_str}."
    )


def construir_user_prompt(jugador, vecino, T: float, S: float,
                           paso: int, pasos_total: int,
                           phi_local: float,
                           tendencia_phi: float) -> str:
    """
    Construye el user prompt situacional completo.
    Tamaño fijo ~100 tokens — no crece con el tiempo.
    """
    rep_pos_obs, rep_neg_obs = percibir_reputacion(vecino)
    hist_str = resumen_historial(jugador, vecino.id)

    tendencia = ("subiendo ↑" if tendencia_phi > 0.02
                 else "bajando ↓" if tendencia_phi < -0.02
                 else "estable →")

    return (
        f"--- Ronda {paso + 1} de {pasos_total} ---\n\n"
        f"Recompensas actuales:\n"
        f"  Tentación (T) = {T:.2f}\n"
        f"  Sacrificio (S) = {S:.2f}\n\n"
        f"Tu reputación en el vecindario:\n"
        f"  Positiva: {jugador.rep_pos:.2f} | "
        f"Negativa: {jugador.rep_neg:.2f}\n\n"
        f"Vecino #{vecino.id}:\n"
        f"  Reputación positiva percibida: {rep_pos_obs:.2f}\n"
        f"  Reputación negativa percibida: {rep_neg_obs:.2f}\n"
        f"  {hist_str}\n\n"
        f"Norma social local (últimas 5 rondas):\n"
        f"  Cooperación media: {phi_local:.0%} ({tendencia})\n\n"
        f"¿Cuál es tu decisión?"
    )
