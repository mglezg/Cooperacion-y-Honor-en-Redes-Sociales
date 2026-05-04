import os
import cv2
import numpy as np

def pad_imagenes_en_carpeta(carpeta, extensiones=('.png', '.jpg', '.jpeg')):
    """
    Añade padding negro a todas las imágenes en la carpeta para igualarlas al tamaño máximo encontrado.
    Esto evita errores al generar GIFs con imageio.mimsave().

    Args:
        carpeta (str): Ruta a la carpeta con las imágenes.
        extensiones (tuple): Tipos de archivo válidos (por defecto PNG y JPG).
    """
    ancho_max, alto_max = 0, 0

    # 1. Encontrar dimensiones máximas
    for archivo in os.listdir(carpeta):
        if archivo.lower().endswith(extensiones):
            img = cv2.imread(os.path.join(carpeta, archivo))
            if img is not None:
                alto, ancho = img.shape[:2]
                ancho_max = max(ancho_max, ancho)
                alto_max = max(alto_max, alto)

    # 2. Aplicar padding a cada imagen
    for archivo in os.listdir(carpeta):
        if archivo.lower().endswith(extensiones):
            ruta = os.path.join(carpeta, archivo)
            img = cv2.imread(ruta)
            if img is not None:
                alto, ancho = img.shape[:2]
                pad_top = (alto_max - alto) // 2
                pad_bottom = alto_max - alto - pad_top
                pad_left = (ancho_max - ancho) // 2
                pad_right = ancho_max - ancho - pad_left

                if pad_top or pad_bottom or pad_left or pad_right:
                    img_padded = cv2.copyMakeBorder(
                        img, pad_top, pad_bottom, pad_left, pad_right,
                        cv2.BORDER_CONSTANT, value=[0, 0, 0]
                    )
                    cv2.imwrite(ruta, img_padded)
