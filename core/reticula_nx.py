import networkx as nx
import numpy as np
import random
import imageio
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Patch 
from collections import Counter
from core.jugador import Jugador

# Colores por fenotipo
colores_fenotipos = {
    'E': 'red',      # Envidioso
    'P': 'blue',     # Pesimista
    'O': 'orange',   # Optimista
    'A': 'green',    # Altruista
    'R': 'purple'    # Aleatorio
}

class ReticulaNX:
    def __init__(self, L, distrib_fenotipos, tau_limites):
        self.L = L
        self.G = nx.grid_2d_graph(L, L, periodic=True)
        self.distrib_fenotipos = distrib_fenotipos
        self.tau_limites = tau_limites
        self._asignar_jugadores()

    def _samplear_fenotipo(self):
        tipos = list(self.distrib_fenotipos.keys())
        pesos = list(self.distrib_fenotipos.values())
        return random.choices(tipos, weights=pesos, k=1)[0]
    """
    def _asignar_jugadores(self):
        for nodo in self.G.nodes:
            id_str = f"{nodo[0]}-{nodo[1]}"
            fenotipo = self._samplear_fenotipo()
            estrategia = None
            tau = random.randint(*self.tau_limites)
            theta = 0
            jugador = Jugador(id_str, fenotipo, estrategia, tau, theta, self.tau_limites)
            self.G.nodes[nodo]['jugador'] = jugador"""

    def _asignar_jugadores(self):
        total_nodos = self.L * self.L
        tipos = list(self.distrib_fenotipos.keys())
        pesos = list(self.distrib_fenotipos.values())

        # Calcular número exacto por tipo
        conteo_fenotipos = {
            tipo: int(round(p * total_nodos)) for tipo, p in self.distrib_fenotipos.items()
        }

        # Ajuste si sobran o faltan por redondeo
        suma = sum(conteo_fenotipos.values())
        diferencia = total_nodos - suma
        if diferencia != 0:
            # Ajustar el primero proporcionalmente
            conteo_fenotipos[tipos[0]] += diferencia

        # Crear lista expandida y mezclar
        lista_fenotipos = []
        for tipo, cantidad in conteo_fenotipos.items():
            lista_fenotipos.extend([tipo] * cantidad)
        random.shuffle(lista_fenotipos)

        # Asignar uno a uno
        for i, nodo in enumerate(self.G.nodes):
            id_str = f"{nodo[0]}-{nodo[1]}"
            fenotipo = lista_fenotipos[i]
            estrategia = None
            tau = random.randint(*self.tau_limites)
            theta = 0
            jugador = Jugador(id_str, fenotipo, estrategia, tau, theta, self.tau_limites)
            self.G.nodes[nodo]['jugador'] = jugador


    def nodos(self):
        return self.G.nodes

    def vecinos(self, nodo):
        return list(self.G.neighbors(nodo))
    
def graficar_y_guardar_fenotipos(reticula, paso, parametros, carpeta="frames"):
    """
    Retícula mejorada con 4 canales visuales independientes:
      Canal 1: color de fondo     = fenotipo
      Canal 2: alpha del nodo     = reputacion positiva (brillo)
      Canal 3: borde del nodo     = balance de honor (verde/rojo)
      Canal 4: punto central      = decision esta ronda (blanco=C, negro=D)
    Misma firma que la version original. main.py no cambia.
    """
    import matplotlib.patches as mpatches

    os.makedirs(carpeta, exist_ok=True)
    G   = reticula.G
    L   = reticula.L

    # Paleta de fenotipos mejorada (mas distinguible)
    COLORES = {
        'E': '#E15759',   # Envidioso  - rojo
        'P': '#4E79A7',   # Pesimista  - azul
        'O': '#F28E2B',   # Optimista  - naranja
        'A': '#59A14F',   # Altruista  - verde
        'R': '#B07AA1',   # Aleatorio  - morado
    }

    ETIQUETAS = {
        'E': 'Envidioso',
        'P': 'Pesimista',
        'O': 'Optimista',
        'A': 'Altruista',
        'R': 'Aleatorio',
    }

    def _color_borde_honor(rep_pos, rep_neg):
        delta = rep_pos - rep_neg
        if   delta >  0.25: return '#27AE60', 1.5 + delta * 3.0
        elif delta < -0.25: return '#E74C3C', 1.5 + abs(delta) * 3.0
        else:               return '#888888', 0.8

    fig, ax = plt.subplots(figsize=(10, 9))
    ax.set_xlim(-0.5, L - 0.5)
    ax.set_ylim(-0.5, L - 0.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_facecolor('#1a1a2e')
    fig.patch.set_facecolor('#1a1a2e')

    conteo = Counter()
    pos = {}


    for nodo in G.nodes:
        j   = G.nodes[nodo]['jugador']
        if isinstance(nodo, tuple):
            row, col = nodo
        else:
            col = nodo % L
            row = nodo // L

        pos[nodo] = np.array([col, -row])
        conteo[j.fenotipo] += 1

        color_fondo          = COLORES.get(j.fenotipo, '#888888')
        rep_pos              = getattr(j, 'rep_pos', 0.7)
        rep_neg              = getattr(j, 'rep_neg', 0.3)
        alpha                = 0.25 + 0.75 * rep_pos
        color_borde, grosor  = _color_borde_honor(rep_pos, rep_neg)
        estrategia           = getattr(j, 'estrategia', None)
        color_punto          = 'white' if estrategia == 'C' else '#111111' if estrategia == 'D' else None

        # Celda con esquinas redondeadas
        rect = mpatches.FancyBboxPatch(
            (col - 0.42, row - 0.42), 0.84, 0.84,
            boxstyle="round,pad=0.04",
            facecolor=color_fondo,
            alpha=alpha,
            edgecolor=color_borde,
            linewidth=grosor,
            zorder=2
        )
        ax.add_patch(rect)

        # Punto central: decision esta ronda
        if color_punto:
            ax.plot(col, row, 'o',
                    color=color_punto,
                    markersize=4.5,
                    zorder=3,
                    alpha=0.9)

    total = sum(conteo.values())

    # Leyenda fenotipos
    parches_fenotipo = []
    for clave, color in COLORES.items():
        pct = (conteo[clave] / total * 100) if total > 0 else 0
        parches_fenotipo.append(
            mpatches.Patch(color=color, label=f"{ETIQUETAS[clave]}: {pct:.1f}%")
        )
    leg1 = ax.legend(
        handles=parches_fenotipo,
        title='Fenotipo',
        loc='upper left',
        bbox_to_anchor=(1.01, 1.0),
        fontsize=8,
        title_fontsize=9,
        framealpha=0.15,
        labelcolor='white',
        facecolor='#2a2a3e',
        edgecolor='#444'
    )
    leg1.get_title().set_color('white')
    ax.add_artist(leg1)

    # Leyenda honor
    parches_honor = [
        mpatches.Patch(edgecolor='#27AE60', facecolor='none', linewidth=2, label='Rep+ alta (honrado)'),
        mpatches.Patch(edgecolor='#E74C3C', facecolor='none', linewidth=2, label='Rep- alta (deshonrado)'),
        mpatches.Patch(facecolor='white',   edgecolor='none', label='Coopero esta ronda'),
        mpatches.Patch(facecolor='#111111', edgecolor='none', label='Defecto esta ronda'),
    ]
    leg2 = ax.legend(
        handles=parches_honor,
        title='Honor y decision',
        loc='lower left',
        bbox_to_anchor=(1.01, 0.0),
        fontsize=8,
        title_fontsize=9,
        framealpha=0.15,
        labelcolor='white',
        facecolor='#2a2a3e',
        edgecolor='#444'
    )
    leg2.get_title().set_color('white')

    # Titulo y parametros
    ax.set_title(
        f"Ronda {paso + 1}   |   brillo = rep+   |   borde = honor",
        fontsize=11, color='white', pad=10
    )

    # Parametros en texto lateral
    lineas = []
    for k, v in parametros.items():
        if isinstance(v, list):
            lineas.append(f"{k}:")
            lineas.extend([f"  {item}" for item in v])
        else:
            lineas.append(f"{k} = {v}")
    texto = "\n".join(lineas)
    fig.text(0.98, 0.5, texto,
             fontsize=7, va='center', ha='right',
             color='#aaaaaa',
             transform=fig.transFigure)

    filename = os.path.join(carpeta, f"frame_{paso:03d}.png")
    plt.savefig(filename, dpi=120, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)

def graficar_fenotipos(reticula, paso, parametros):
    G = reticula.G
    pos = dict((n, n) for n in G.nodes)

    # Recolectar fenotipos
    fenotipos_actuales = [G.nodes[n]['jugador'].fenotipo for n in G.nodes]
    conteo = Counter(fenotipos_actuales)
    total = sum(conteo.values())

    # Colores por nodo
    colores = [colores_fenotipos.get(G.nodes[n]['jugador'].fenotipo, 'gray') for n in G.nodes]

    fig = plt.figure(figsize=(12.2, 9.7), dpi=100)
    nx.draw(G, pos=pos, node_color=colores, with_labels=False, node_size=100)

    # Título
    plt.title(f"Fenotipos - PASO {paso}", fontsize=20, pad=20)

    # Leyenda
    leyenda = []
    etiquetas = {
        'E': 'Envidioso',
        'P': 'Pesimista',
        'O': 'Optimista',
        'A': 'Altruista',
        'R': 'Aleatorio'
    }

    for clave in colores_fenotipos:
        porcentaje = (conteo[clave] / total) * 100 if clave in conteo else 0.0
        etiqueta = f"{etiquetas[clave]}: {porcentaje:.1f}%"
        leyenda.append(Patch(color=colores_fenotipos[clave], label=etiqueta))

    plt.legend(handles=leyenda, title="Fenotipos", loc="lower left", bbox_to_anchor=(1.02, 0.3))

    # Parámetros
    lineas = []
    for k, v in parametros.items():
        if isinstance(v, list):
            lineas.append(f"{k}:")
            lineas.extend([f"  {item}" for item in v])
        else:
            lineas.append(f"{k} = {v}")
    texto_parametros = "\n".join(lineas)
    plt.gcf().text(1.02, 0.65, texto_parametros, fontsize=9, va='top')

    return fig


def guardar_grafico(fig, nombre_archivo):
    os.makedirs(os.path.dirname(nombre_archivo), exist_ok=True)
    fig.tight_layout()
    fig.savefig(nombre_archivo, bbox_inches='tight')
    plt.close(fig)



def crear_gif(carpeta="img/frames", nombre_salida="simulacion.gif", fps=5):
    imagenes = []
    tamanos = set()

    for archivo in sorted(os.listdir(carpeta)):
        if archivo.lower().endswith('.png'):
            ruta = os.path.join(carpeta, archivo)
            img = imageio.imread(ruta)

            # Convertir RGBA a RGB si es necesario
            if img.shape[2] == 4:
                img = img[:, :, :3]

            tamanos.add(img.shape)
            imagenes.append(img)

    if len(tamanos) > 1:
        raise ValueError(f"❌ Las imágenes no tienen el mismo tamaño: {tamanos}")

    imageio.mimsave(nombre_salida, imagenes, fps=fps)
    print(f"✅ GIF guardado como '{nombre_salida}'")