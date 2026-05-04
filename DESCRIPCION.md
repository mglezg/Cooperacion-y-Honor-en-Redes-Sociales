# Descripcion del proyecto

## Simulacion de Fenotipos Conductuales en Redes Sociales
## mediante Agentes de Inteligencia Artificial Generativa

---

Este trabajo parte de una simulacion previa de teoria de juegos
evolutiva sobre redes sociales, en la que individuos con distintos
fenotipos conductuales — Altruista, Envidioso, Optimista, Pesimista
y Aleatorio — interactuaban en una reticula bidimensional decidiendo
si cooperar o defectar segun modelos matematicos cerrados.

El salto que propone este proyecto es sustituir esos modelos
matematicos por agentes de inteligencia artificial generativa
(LLM, Large Language Models). En lugar de que cada individuo
aplique una formula sobre los parametros de recompensa T y S,
el agente razona en lenguaje natural sobre su situacion
completa: quien tiene enfrente, que historial tiene con el,
como es su reputacion en el vecindario, y cual es la norma
social del entorno en ese momento. El fenotipo deja de ser
una regla y pasa a ser una personalidad: el Altruista recibe
instrucciones de priorizar el bienestar colectivo incluso a
costa propia; el Envidioso, de no tolerar que el otro gane
mas que el; el Pesimista, de desconfiar por defecto y
protegerse del peor caso posible.

Para enriquecer aun mas el modelo, se introduce un sistema de
honor bidireccional. Cada agente acumula a lo largo del tiempo
dos valores de reputacion: positiva (cuanto coopera) y negativa
(cuanto defecta), que evolucionan con un decay exponencial
configurable y son visibles para los vecinos con ruido perceptivo.
Esto permite que emerjan fenomenos que los modelos cerrados no
pueden capturar: agentes socialmente aislados por reputacion
negativa acumulada, clusters de cooperacion sostenidos por
confianza mutua construida ronda a ronda, o cambios de
comportamiento motivados por el deterioro de la propia imagen
social antes de que los pagos economicos lo justifiquen.

La arquitectura tecnica preserva intacta la reticula NetworkX,
la matriz de pagos lineal T/S, el mecanismo de cambio de fenotipo
por imitacion y todos los parametros originales K1, K2, tau.
Los agentes LLM se integran como una capa de decision que recibe
contexto situacional compacto (~255 tokens por llamada, de coste
fijo independientemente del avance de la simulacion) y devuelve
siempre una decision estructurada en JSON junto con una
justificacion textual que queda registrada en el log. Esa
justificacion es el activo diferencial del proyecto: al terminar
la simulacion existe un corpus de razonamientos por fenotipo que
permite analisis cualitativos imposibles en cualquier modelo
matematico cerrado. Por que coopero el Altruista con alguien
que lleva cuatro rondas traicionandole? Como justifica el
Envidioso defectar frente a un vecino con reputacion excelente?
Esas preguntas tienen respuesta textual en el log.

El sistema soporta dos modos de ejecucion intercambiables con
un solo parametro: modo API usando Claude Haiku de Anthropic
(recomendado para resultados finales, ~0.30 euros y 6 minutos
por simulacion completa de 10x10 agentes y 100 pasos) y modo
local usando modelos pequenos via Ollama (para desarrollo y
depuracion sin coste de API). El fallback matematico original
garantiza que la simulacion nunca se interrumpe por un error
de la API.

El objetivo final es comparar directamente los resultados de
ambas versiones — modelo matematico cerrado versus agentes LLM —
sobre los mismos parametros iniciales, y responder si los
fenotipos conservan su comportamiento caracteristico cuando
razonan en lugar de calcular, si el sistema de honor acelera
o frena la emergencia de cooperacion, y como interactuan la
memoria de corto plazo y la reputacion acumulada en la
dinamica global de la red.
