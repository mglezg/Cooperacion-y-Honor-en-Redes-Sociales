# ============================================================
#  core/juego.py
#  Misma lógica original + registro de historial por vecino
# ============================================================

def simular_juego(jugador1, jugador2, T, S):
    """
    Simula un juego entre jugador1 y jugador2.
    Calcula pagos según la matriz estándar.
    NUEVO: registra la interacción en el historial de ambos.
    """
    e1 = jugador1.estrategia
    e2 = jugador2.estrategia

    matriz = {
        ('C', 'C'): (1, 1),
        ('C', 'D'): (S, T),
        ('D', 'C'): (T, S),
        ('D', 'D'): (0, 0),
    }

    pago1, pago2 = matriz[(e1, e2)]
    jugador1.pago_acumulado += pago1
    jugador2.pago_acumulado += pago2

    # ── NUEVO: registrar historial bidireccional ──────────────
    jugador1.registrar_interaccion(
        jugador2.id,
        yo_coopere = (e1 == 'C'),
        el_coopero = (e2 == 'C')
    )
    jugador2.registrar_interaccion(
        jugador1.id,
        yo_coopere = (e2 == 'C'),
        el_coopero = (e1 == 'C')
    )

    return pago1, pago2
