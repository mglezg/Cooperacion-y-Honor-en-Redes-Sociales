import pandas as pd
import matplotlib.pyplot as plt
import os

colores_fenotipos = {
    'E': 'red',
    'P': 'blue',
    'O': 'orange',
    'A': 'green',
    'R': 'purple'
}

def graficar_resultados_globales(log_path="resultados/logs/log.csv", out_dir="resultados/plots"):
    os.makedirs(out_dir, exist_ok=True)
    
    df = pd.read_csv(log_path)

    # Gráfico 1: Cooperación global
    plt.figure(figsize=(8, 4))
    plt.plot(df['paso'], df['cooperacion_global'], color='green')
    plt.title("Evolución de la cooperación global")
    plt.xlabel("Paso")
    plt.ylabel("ϕ(t)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "cooperacion_global.png"))
    plt.close()

    # Gráfico 2: Proporciones de fenotipos
    plt.figure(figsize=(10, 5))
    for fenotipo, color in zip(['E', 'P', 'O', 'A', 'R'], ['red', 'blue', 'orange', 'green', 'purple']):
        plt.plot(df['paso'], df[fenotipo], label=fenotipo, color=color)

    plt.title("Evolución de la proporción de fenotipos")
    plt.xlabel("Paso")
    plt.ylabel("Proporción")
    plt.legend(title="Fenotipos")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fenotipos_evolucion.png"))
    plt.close()

    print("✅ Gráficas guardadas en:", out_dir)


def graficar_rendimiento_jugador(log_path="resultados/logs/log_jugadores.csv", jugador_id="5-3", out_dir="resultados/plots"):
    df = pd.read_csv(log_path)
    jugador_df = df[df['id'] == jugador_id]

    if jugador_df.empty:
        print(f"❌ No se encontraron datos para el jugador {jugador_id}")
        return

    # Crear figura
    plt.figure(figsize=(10, 4))

    # Dibujar puntos con color según fenotipo
    for fenotipo, grupo in jugador_df.groupby('fenotipo'):
        plt.plot(
            grupo['paso'], grupo['pago'],
            marker='o', linestyle='-', color=colores_fenotipos.get(fenotipo, 'gray'),
            label=fenotipo
        )

    plt.title(f"Rendimiento del Jugador {jugador_id} (por fenotipo)")
    plt.xlabel("Paso")
    plt.ylabel("Pago acumulado")
    plt.grid(True)
    plt.legend(title="Fenotipo")
    plt.tight_layout()

    # Guardar la gráfica
    subdir = os.path.join(out_dir, "rendimiento")
    os.makedirs(subdir, exist_ok=True)
    filename = os.path.join(subdir, f"{jugador_id.replace('-', '_')}.png")
    plt.savefig(filename)
    plt.close()

    print(f"✅ Gráfico guardado para jugador {jugador_id}: {filename}")
