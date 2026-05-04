# Simulacion de Fenotipos Conductuales en Redes Sociales mediante Agentes de Inteligencia Artificial Generativa

**Trabajo de Fin de Grado — Ingenieria Matematica**
**Autor:** Manuel Gonzalez
**Proyecto antiguo del proyecto:** [TFG_SimulacionAgentesFenotipos](https://github.com/mglezg/TFG_SimulacionAgentesFenotipos)
**Evolucion del proyecto:** [Cooperacion-y-Honor-en-Redes-Sociales](https://github.com/mglezg/Cooperacion-y-Honor-en-Redes-Sociales)

---

## Descripcion

Este proyecto extiende una simulacion de teoria de juegos evolutiva sobre redes sociales,
sustituyendo los modelos matematicos cerrados de decision por agentes de inteligencia
artificial generativa (LLM). Cada nodo de la reticula representa un individuo con un
fenotipo conductual definido — Altruista, Envidioso, Optimista, Pesimista o Aleatorio —
que decide si cooperar o defectar en cada ronda mediante razonamiento en lenguaje natural,
en lugar de aplicar una formula fija.

Ademas, se introduce un sistema de honor bidireccional: cada agente acumula reputacion
positiva y negativa a lo largo del tiempo, visible para sus vecinos con ruido perceptivo,
que influye en las decisiones del LLM y genera fenomenos emergentes de aislamiento social
y cooperacion reputacional que los modelos matematicos no pueden capturar.

---

## Que hay de nuevo respecto al TFG original

| Elemento | TFG original | Esta version |
|---|---|---|
| Decision del agente | Formula matematica por fenotipo | LLM con razonamiento contextual |
| Factores de decision | T, S, tau | T, S, reputacion, historial, norma social |
| Memoria | Sin memoria entre rondas | Buffer circular por vecino (10 rondas) |
| Reputacion | No existe | Sistema bidireccional rep+ / rep- con decay |
| Percepcion del vecino | Perfecta (modelo exacto) | Con ruido gaussiano configurable |
| Log de resultados | paso, fenotipo, estrategia, pago | + rep_pos, rep_neg, justificacion LLM |
| Visualizacion | Color por fenotipo | + brillo (rep+), borde de honor (rep-) |
| Modo de ejecucion | Local, sin API | API (Haiku) o local (Ollama + Phi-3) |

---

## Estructura del proyecto

```
proyecto_v2/
|
|-- main.py                     # Bucle principal de la simulacion
|
|-- config/
|   |-- parametros.py           # Todos los parametros configurables
|   |-- system_prompts.py       # System prompts de los 5 fenotipos
|
|-- core/
|   |-- jugador.py              # Clase Jugador: honor, historial, LLM
|   |-- juego.py                # Logica del juego y registro de interacciones
|   |-- reticula_nx.py          # Reticula NetworkX (sin cambios)
|   |-- fenotipos.py            # Logica matematica original (fallback)
|
|-- utils/
|   |-- llm_client.py           # Cliente LLM: modo API / local
|   |-- prompt_builder.py       # Construccion del prompt situacional
|   |-- logger.py               # Log global (sin cambios)
|   |-- logger_jugadores.py     # Log por jugador (+ columnas honor y LLM)
|   |-- visualizacion.py        # Graficas (+ reputacion y honor)
|   |-- metricas.py             # Metricas globales (sin cambios)
|   |-- matriz_pagos.py         # Pagos lineales T/S (sin cambios)
|   |-- crear_estructura.py     # Creacion de carpetas (sin cambios)
|   |-- resize_imagenes.py      # Utilidad de imagenes (sin cambios)
|
|-- resultados/
|   |-- logs/
|   |   |-- log.csv             # Log global por paso
|   |   |-- log_jugadores.csv   # Log por jugador con honor y justificaciones
|   |-- plots/                  # Graficas generadas
|
|-- img/
|   |-- frames/                 # Frames de la reticula por paso
|   |-- simulacion.gif          # GIF animado de la simulacion
```

---

## Instalacion

### 1. Clonar o descomprimir el proyecto

> Descargar el repositorio y descomprimirlo dentro de una carpeta

### 2. Instalar dependencias

```bash
pip install anthropic networkx matplotlib numpy scipy pandas imageio
```

### 3. Configurar la API key

**Windows (PowerShell):**
```powershell
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-ant-tu-clave", "User")
```

**Mac / Linux:**
```bash
export ANTHROPIC_API_KEY="sk-ant-tu-clave"
```

Obtener API key en: https://console.anthropic.com

---

## Configuracion

Todos los parametros se controlan desde `config/parametros.py`:

```python
# --- Reticula y simulacion ---
L     = 10      # Tamano de la reticula L x L
pasos = 100     # Numero de rondas

# --- Distribucion inicial de fenotipos ---
distrib_fenotipos = {
    'E': 0.2,   # Envidioso
    'P': 0.2,   # Pesimista
    'O': 0.2,   # Optimista
    'A': 0.2,   # Altruista
    'R': 0.2    # Aleatorio
}

# --- Sistema de honor ---
ALPHA_REPUTACION = 0.90   # Decay de memoria (0.85=corta, 0.95=larga)
SIGMA_PERCEPCION = 0.05   # Ruido perceptivo (0.0=perfecto, 0.10=ruidoso)

# --- LLM ---
MODO_LLM   = "api"        # "api" o "local"
MODELO_API = "claude-haiku-4-5-20251001"
```

### Modo de prueba rapida (antes de gastar API)

Cambia temporalmente en `parametros.py`:
```python
L     = 5    # 25 agentes
pasos = 3    # 3 rondas = ~75 llamadas = centimos
```

---

## Ejecucion

```bash
python main.py
```

La simulacion imprime el progreso por consola ronda a ronda.
Al terminar genera automaticamente:

- `img/simulacion.gif` — animacion de la reticula
- `resultados/plots/cooperacion_global.png`
- `resultados/plots/fenotipos_evolucion.png`
- `resultados/plots/reputacion_evolucion.png` (nuevo)
- `resultados/plots/rendimiento/` — una grafica por jugador

---

## Modo local (sin API, para desarrollo)

Instala [Ollama](https://ollama.com) y descarga el modelo:

```bash
ollama pull phi3
```

Cambia en `parametros.py`:
```python
MODO_LLM = "local"
```

Recomendado solo para reticulaas pequenas (5x5, pocos pasos) y
verificar que el codigo funciona. La calidad del razonamiento
es inferior a la API para fenotipos complejos.

---

## Como funciona internamente

### Ciclo de cada ronda

```
Para cada agente:
  1. Calcular phi_local y tendencia del vecindario
  2. Llamar al LLM con: fenotipo (system prompt) +
     T, S, reputacion propia, reputacion del vecino,
     historial con ese vecino, norma social local
  3. LLM devuelve: {"decision": "COOPERAR"|"DEFECTAR",
                    "justificacion": "..."}
  4. Jugar contra todos los vecinos con esa estrategia
  5. Actualizar reputacion positiva y negativa (decay exponencial)
  6. Registrar interaccion en el buffer circular del vecino
  7. Ajustar tau y considerar cambio de fenotipo (igual que antes)
```

### Sistema de honor

Cada agente tiene dos valores continuos en [0, 1]:

- `rep_pos`: frecuencia de cooperacion historica (decay alpha)
- `rep_neg`: frecuencia de defeccion historica (decay alpha)

No son complementarios. Un agente con historial mixto puede tener
ambos valores en valores intermedios. Los vecinos los perciben con
ruido gaussiano de desviacion `SIGMA_PERCEPCION`.

### Estructura del prompt (por llamada, ~255 tokens fijos)

```
[SYSTEM - cacheado]  Personalidad del fenotipo (~150 tokens)
[USER]               Ronda actual, T, S
                     Reputacion propia
                     Reputacion percibida del vecino
                     Historial con ese vecino (1 linea, ~35 tokens)
                     Norma social local (% cooperacion + tendencia)
```

---

## Coste estimado

| Configuracion | Llamadas | Coste (Haiku + cache) | Tiempo |
|---|---|---|---|
| Prueba 5x5, 3 pasos | ~75 | < 0.01 EUR | ~10 seg |
| Simulacion 10x10, 100 pasos | ~100.000 | ~0.30 EUR | ~6 min |
| 30 simulaciones TFG | ~3.000.000 | ~9 EUR | ~3 horas |

---

## Resultados generados

### log_jugadores.csv

| Campo | Descripcion |
|---|---|
| paso | Numero de ronda |
| id | Identificador del nodo |
| fenotipo | Fenotipo actual |
| cambio_fenotipo | 1 si cambio en esta ronda |
| estrategia | C o D |
| pago | Pago acumulado |
| tau | Umbral de cambio actual |
| rep_pos | Reputacion positiva al final de la ronda |
| rep_neg | Reputacion negativa al final de la ronda |
| justif_llm | Justificacion textual del LLM |

### Visualizacion de la reticula (GIF)

Cuatro canales visuales simultaneos:

- **Color de fondo**: fenotipo del agente
- **Brillo (alpha)**: reputacion positiva (brillante = cooperador historico)
- **Borde**: balance de honor (verde = honrado, rojo = deshonrado)
- **Punto central**: decision en esta ronda (blanco = C, negro = D)

---

## Preguntas de investigacion que habilita este diseno

- Los fenotipos mantienen su comportamiento caracteristico cuando
  razonan en lenguaje natural frente a cuando aplican una formula?
- Emerge aislamiento social en agentes con reputacion negativa alta
  independientemente de los valores de T y S?
- La memoria de interacciones pasadas cambia la dinamica de
  cooperacion respecto al modelo sin memoria?
- Como afecta ALPHA_REPUTACION (memoria larga vs corta) a la
  velocidad de consolidacion de clusters de cooperacion?

---

## Licencia

Proyecto academico — Ingenieria Matematica.
Uso educativo y de investigacion.
