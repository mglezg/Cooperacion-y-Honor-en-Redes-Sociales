import os

def crear_estructura():
    """
    Crea la estructura de carpetas necesaria para guardar los resultados de la simulación.
    """
    # Definir estructura de carpetas
    estructura = [
        "img/frames",
        "resultados/data",
        "resultados/logs",
        "resultados/plots"
    ]

    # Crear carpetas si no existen
    for carpeta in estructura:
        os.makedirs(carpeta, exist_ok=True)
        print(f"Carpeta verificada o creada: {carpeta}")
