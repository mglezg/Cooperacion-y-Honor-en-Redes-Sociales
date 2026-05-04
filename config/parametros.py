# ============================================================
#  config/parametros.py
#  Parámetros originales + nuevos para LLM, honor y memoria
# ============================================================

# ── PARÁMETROS ORIGINALES (sin cambios) ──────────────────────
L      = 5       # Tamaño de la retícula L×L
pasos  = 3      # Número de rondas de la simulación

distrib_fenotipos = {
    'E': 0.1,
    'P': 0.2,
    'O': 0.4,
    'A': 0.2,
    'R': 0.1
}

tau_limites = (3, 10)
delta_tau   = 1
K1          = 1
K2          = 0.1

# ── PARÁMETROS NUEVOS: SISTEMA DE HONOR ──────────────────────
ALPHA_REPUTACION = 0.90
# Decay exponencial de la memoria de reputación.
# 0.85 = memoria corta (~6 rondas efectivas)
# 0.90 = memoria media (~10 rondas)   ← recomendado para empezar
# 0.95 = memoria larga (~20 rondas)

SIGMA_PERCEPCION = 0.05
# Ruido gaussiano en la percepción de reputación ajena.
# 0.00 = información perfecta (poco realista)
# 0.05 = ruido bajo                   ← recomendado para empezar
# 0.10 = ruido alto (red ruidosa)

# ── PARÁMETROS NUEVOS: LLM ───────────────────────────────────
MODO_LLM = "api"
# "api"   → Claude Haiku via Anthropic API (resultados finales)
# "local" → Phi-3 Mini via Ollama (desarrollo y pruebas)

MODELO_API   = "claude-haiku-4-5-20251001"
MODELO_LOCAL = "phi3"          # nombre del modelo en Ollama
MAX_TOKENS   = 300             # respuesta corta: solo JSON
