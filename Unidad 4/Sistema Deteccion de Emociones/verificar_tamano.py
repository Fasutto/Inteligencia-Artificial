import os
from PIL import Image

script_dir = os.path.dirname(os.path.abspath(__file__))
ruta_base = os.path.join(script_dir, "Imagenes", "train")
# Encontrar primera imagen
for raiz, dirs, archivos in os.walk(ruta_base):
    for archivo in archivos:
        if archivo.lower().endswith(('.png', '.jpg', '.jpeg')):
            ruta_completa = os.path.join(raiz, archivo)
            try:
                # Intentar abrir la imagen
                imagen = Image.open(ruta_completa)
                print(f"Imagen: {archivo}")
                print(f"Tamaño: {imagen.size}") # Imprime dimensiones (Ancho, Alto)
                print(f"Modo: {imagen.mode}") # Imprime modo de color (ej. RGB, L)
                exit() # Salir después de encontrar la primera imagen válida
            except Exception as e:
                print(f"Error leyendo {archivo}: {e}")
