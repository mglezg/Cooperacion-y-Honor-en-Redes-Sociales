# ============================================================
#  core/jugador.py
#  Clase Jugador ampliada con:
#    - Sistema de honor bidireccional (rep_pos, rep_neg)
#    - Historial por vecino (buffer circular)
#    - Decisión delegada al LLM
# ============================================================

import random
from collections import deque
from math import exp
from scipy.special import expit
from config.parametros import ALPHA_REPUTACION


class ResumenVecino:
    """Estadísticas pre-calculadas del historial con un vecino."""
    def __init__(self):
        self.coop_yo  = 0.0   # % veces que yo cooperé con él
        self.coop_el  = 0.0   # % veces que él cooperó conmigo
        self.racha_el = 0     # rondas consecutivas (+coop / -defect)
        self.n        = 0     # total interacciones registradas


class Jugador:
    def __init__(self, id, fenotipo, estrategia, tau, theta, tau_limites):
        # ── Atributos originales ──────────────────────────────
        self.id               = id
        self.fenotipo         = fenotipo
        self.fenotipo_anterior = fenotipo
        self.estrategia       = estrategia
        self.tau              = tau
        self.theta            = theta
        self.pago_acumulado   = 0.0
        self.vecinos          = []
        self.tau_limites      = tau_limites

        # ── NUEVO: sistema de honor ───────────────────────────
        self.rep_pos = 0.5    # reputación positiva  [0, 1]
        self.rep_neg = 0.5    # reputación negativa  [0, 1]
        # Arrancan en 0.5: agente desconocido, ni bueno ni malo

        # ── NUEVO: historial por vecino ───────────────────────
        # buffer_vecinos: { id_vecino: deque(maxlen=10) }
        # cada entrada: (yo_cooperé: bool, él_cooperó: bool)
        self.buffer_vecinos  = {}
        self.resumen_vecinos = {}   # { id_vecino: ResumenVecino }

        # ── NUEVO: justificación del LLM (para el log) ───────
        self.justif_llm = ""

        # ── NUEVO: phi_local previo (para calcular tendencia) ─
        self._phi_local_prev = 0.5

    # ── Métodos originales sin cambios ───────────────────────

    def reiniciar_pago(self):
        self.pago_acumulado = 0.0

    def actualizar_theta(self):
        self.theta += 1

    def reiniciar_theta(self):
        self.theta = 0

    def agregar_vecino(self, vecino):
        self.vecinos.append(vecino)

    def ajustar_tau(self, phi_local, phi_global, delta_tau, K1):
        diff = (phi_local - phi_global) / K1
        prob_aumentar = expit(diff)
        if random.random() < prob_aumentar:
            self.tau = min(self.tau + delta_tau, self.tau_limites[1])
        else:
            self.tau = max(self.tau - delta_tau, self.tau_limites[0])

    def considerar_cambio_de_fenotipo(self, K2):
        if self.theta < self.tau:
            self.theta += 1
            return
        vecino    = random.choice(self.vecinos)
        pi_i      = self.pago_acumulado
        pi_j      = vecino.pago_acumulado
        prob_imitar = expit((pi_j - pi_i) / K2)
        if random.random() < prob_imitar:
            self.fenotipo_anterior = self.fenotipo
            self.fenotipo = vecino.fenotipo
        self.theta = 0

    # ── Método nuevo: decidir con LLM ────────────────────────

    def decidir_estrategia(self, vecino, T, S, paso, pasos_total,
                            phi_local, tendencia_phi):
        """
        Reemplaza la lógica matemática de fenotipos.py.
        Construye el prompt situacional y llama al LLM.
        self.estrategia sigue siendo 'C' o 'D' — compatible
        con el resto del código sin cambios.
        """
        from utils.prompt_builder import construir_user_prompt
        from utils.llm_client import llamar_llm

        user_prompt = construir_user_prompt(
            jugador       = self,
            vecino        = vecino,
            T             = T,
            S             = S,
            paso          = paso,
            pasos_total   = pasos_total,
            phi_local     = phi_local,
            tendencia_phi = tendencia_phi
        )

        resultado = llamar_llm(self.fenotipo, user_prompt)

        self.estrategia = (
            'C' if resultado["decision"] == "COOPERAR" else 'D'
        )
        self.justif_llm = resultado.get("justificacion", "")

    # ── Método nuevo: actualizar honor ────────────────────────

    def actualizar_reputacion(self, coopero: bool):
        """
        Llamar UNA vez al final de cada ronda, después de
        que la estrategia esté decidida y el juego jugado.
        """
        a = ALPHA_REPUTACION
        if coopero:
            self.rep_pos = a * self.rep_pos + (1 - a) * 1.0
            self.rep_neg = a * self.rep_neg + (1 - a) * 0.0
        else:
            self.rep_pos = a * self.rep_pos + (1 - a) * 0.0
            self.rep_neg = a * self.rep_neg + (1 - a) * 1.0

    # ── Método nuevo: registrar interacción con vecino ────────

    def registrar_interaccion(self, id_vecino: str,
                               yo_coopere: bool, el_coopero: bool):
        """
        Actualiza buffer circular y resumen pre-calculado.
        Llamar desde simular_juego() para los dos jugadores.
        """
        if id_vecino not in self.buffer_vecinos:
            self.buffer_vecinos[id_vecino]  = deque(maxlen=10)
            self.resumen_vecinos[id_vecino] = ResumenVecino()

        buf = self.buffer_vecinos[id_vecino]
        buf.append((yo_coopere, el_coopero))

        res    = self.resumen_vecinos[id_vecino]
        res.n  = len(buf)
        res.coop_yo = round(sum(b[0] for b in buf) / res.n, 2)
        res.coop_el = round(sum(b[1] for b in buf) / res.n, 2)

        # racha: contar desde el final hasta que cambie patrón
        signo = 1 if el_coopero else -1
        racha = 0
        for _, dec in reversed(buf):
            if (dec and signo > 0) or (not dec and signo < 0):
                racha += 1
            else:
                break
        res.racha_el = racha * signo
