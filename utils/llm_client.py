# ============================================================
#  utils/llm_client.py
#  Cliente LLM con modo dual: API (Anthropic) o local (Ollama)
#  Cambiar MODO_LLM en config/parametros.py para alternar.
# ============================================================

import json
import anthropic
from config.parametros import MODO_LLM, MODELO_API, MODELO_LOCAL, MAX_TOKENS
from config.system_prompts import SYSTEM_PROMPTS

# Cliente Anthropic singleton (se crea una sola vez)
_anthropic_client = None

def _get_anthropic_client():
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = anthropic.Anthropic()
    return _anthropic_client


def _llamar_api(fenotipo: str, user_prompt: str) -> dict:
    """Llamada a Claude Haiku via Anthropic API con prompt caching."""
    client = _get_anthropic_client()
    response = client.messages.create(
        model      = MODELO_API,
        max_tokens = MAX_TOKENS,
        system     = [
            {
                "type": "text",
                "text": SYSTEM_PROMPTS[fenotipo],
                "cache_control": {"type": "ephemeral"}
                # ↑ Prompt caching: el system prompt de cada fenotipo
                # se cobra solo la primera vez. El resto de llamadas
                # del mismo fenotipo son ~80% más baratas.
            }
        ],
        messages = [
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.content[0].text.strip()


def _llamar_local(fenotipo: str, user_prompt: str) -> str:
    """Llamada a modelo local via Ollama (sin dependencia de API key)."""
    import urllib.request
    import urllib.error

    payload = json.dumps({
        "model": MODELO_LOCAL,
        "messages": [
            {"role": "system",  "content": SYSTEM_PROMPTS[fenotipo]},
            {"role": "user",    "content": user_prompt}
        ],
        "stream": False,
        "options": {"num_predict": MAX_TOKENS}
    }).encode("utf-8")

    req = urllib.request.Request(
        "http://localhost:11434/api/chat",
        data    = payload,
        headers = {"Content-Type": "application/json"},
        method  = "POST"
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["message"]["content"].strip()


def llamar_llm(fenotipo: str, user_prompt: str) -> dict:
    """
    Punto de entrada único. Usa API o local según MODO_LLM.
    Siempre devuelve:
        {"decision": "COOPERAR"|"DEFECTAR", "justificacion": str}
    Nunca lanza excepción: en caso de error devuelve fallback
    matemático para que la simulación no se interrumpa.
    """
    try:
        if MODO_LLM == "api":
            raw = _llamar_api(fenotipo, user_prompt)
        else:
            raw = _llamar_local(fenotipo, user_prompt)

        # Limpiar por si el modelo añade ```json ... ```
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        resultado = json.loads(raw)

        # Validar estructura
        if resultado.get("decision") not in ("COOPERAR", "DEFECTAR"):
            raise ValueError(f"decision inesperada: {resultado}")

        return resultado

    except Exception as e:
        # Fallback: lógica matemática original para no romper la sim
        print(f"  [LLM fallback] {fenotipo} (modo={MODO_LLM}): {e}")
        decision = _fallback_matematico(fenotipo,
                                        _extraer_T(user_prompt),
                                        _extraer_S(user_prompt))
        return {
            "decision":      decision,
            "justificacion": "[fallback matemático por error LLM]"
        }


def _fallback_matematico(fenotipo: str, T: float, S: float) -> str:
    """Replica la lógica original de fenotipos.py como fallback."""
    import random as _random
    if   fenotipo == 'E': return 'COOPERAR' if S > T  else 'DEFECTAR'
    elif fenotipo == 'O': return 'COOPERAR' if T < 1  else 'DEFECTAR'
    elif fenotipo == 'P': return 'COOPERAR' if S > 0  else 'DEFECTAR'
    elif fenotipo == 'A': return 'COOPERAR'
    elif fenotipo == 'R': return _random.choice(['COOPERAR', 'DEFECTAR'])
    return 'COOPERAR'


def _extraer_T(prompt: str) -> float:
    """Extrae T del user prompt para el fallback."""
    try:
        for linea in prompt.split('\n'):
            if 'Tentación (T)' in linea or 'T)' in linea:
                return float(linea.split('=')[-1].strip())
    except Exception:
        pass
    return 1.0


def _extraer_S(prompt: str) -> float:
    """Extrae S del user prompt para el fallback."""
    try:
        for linea in prompt.split('\n'):
            if 'Sacrificio (S)' in linea or 'S)' in linea:
                return float(linea.split('=')[-1].strip())
    except Exception:
        pass
    return 0.0
