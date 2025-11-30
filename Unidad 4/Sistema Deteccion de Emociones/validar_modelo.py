import torch
import torch.nn as nn
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader
import os
import matplotlib.pyplot as plt
import numpy as np
import itertools

# Función para validar el modelo entrenado utilizando el conjunto de datos de prueba.
def validar_modelo():
    
    # Configuración
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dir_datos = os.path.join(script_dir, "Imagenes")
    ruta_modelo = os.path.join(script_dir, "emotion_model.pth")
    num_clases = 4
    tamano_entrada = 224
    tamano_lote = 32

    dispositivo = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"Usando dispositivo: {dispositivo}")

    # Transformaciones de Datos
    transformaciones_datos = transforms.Compose([
        transforms.Resize((tamano_entrada, tamano_entrada)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # Cargar Datos de Prueba
    print("Cargando datos de prueba...")
    dir_prueba = os.path.join(dir_datos, 'test')
    if not os.path.exists(dir_prueba):
        print(f"Error: Directorio de prueba no encontrado en {dir_prueba}")
        return

    # Cargar dataset de prueba
    dataset_prueba = datasets.ImageFolder(dir_prueba, transformaciones_datos)
    # DataLoader para iterar sobre los datos de prueba
    cargador_prueba = DataLoader(dataset_prueba, batch_size=tamano_lote, shuffle=False, num_workers=0)
    nombres_clases_raw = dataset_prueba.classes
    mapa_traduccion = {
        'angry': 'Enojado',
        'happy': 'Feliz',
        'neutral': 'Neutral',
        'sad': 'Triste'
    }
    nombres_clases = [mapa_traduccion.get(nombre, nombre) for nombre in nombres_clases_raw]
    print(f"Clases: {nombres_clases}")

    # Cargar Modelo
    print("Cargando modelo...")
    modelo = models.resnet18(weights=None)
    num_ftrs = modelo.fc.in_features
    modelo.fc = nn.Linear(num_ftrs, num_clases)
    
    if os.path.exists(ruta_modelo):
        modelo.load_state_dict(torch.load(ruta_modelo, map_location=dispositivo))
        modelo = modelo.to(dispositivo)
        modelo.eval()
    else:
        print("Archivo del modelo no encontrado.")
        return

    # Evaluación
    # Inicializar matriz de confusión vacía
    matriz_confusion = torch.zeros(num_clases, num_clases)
    
    print("Evaluando...")
    print("Evaluando...")
    # Desactivar el cálculo de gradientes para ahorrar memoria y cómputo (no estamos entrenando)
    with torch.no_grad():
        for entradas, etiquetas in cargador_prueba:
            entradas = entradas.to(dispositivo)
            etiquetas = etiquetas.to(dispositivo)

            # Obtener predicciones del modelo
            salidas = modelo(entradas)
            _, preds = torch.max(salidas, 1)

            # Llenar la matriz de confusión comparando predicciones con etiquetas reales
            for t, p in zip(etiquetas.view(-1), preds.view(-1)):
                matriz_confusion[t.long(), p.long()] += 1

    # Normalizar
    cm = matriz_confusion.numpy()
    
    print("Matriz de Confusión:")
    print(cm)
    
    # Calcular Precisión por clase
    print("\nPrecisión por clase:")
    for i, nombre_clase in enumerate(nombres_clases):
        acc = cm[i, i] / cm[i].sum() if cm[i].sum() > 0 else 0
        print(f"{nombre_clase}: {acc:.2%}")

    # Graficar Matriz de Confusión
    plt.figure(figsize=(8, 6))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title('Matriz de Confusión')
    plt.colorbar()
    marcas_tic = np.arange(len(nombres_clases))
    plt.xticks(marcas_tic, nombres_clases, rotation=45)
    plt.yticks(marcas_tic, nombres_clases)

    # Agregar anotaciones de texto
    umbral = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, int(cm[i, j]),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > umbral else "black")

    plt.tight_layout()
    plt.ylabel('Etiqueta Verdadera')
    plt.xlabel('Etiqueta Predicha')
    
    ruta_guardado = r"c:/Users/Hirai Momo/Documents/01 - Inteligencia Artificial/Unidad 4/Sistema Deteccion de Emociones/confusion_matrix.png"
    plt.savefig(ruta_guardado)
    print(f"Gráfica de matriz de confusión guardada en {ruta_guardado}")

if __name__ == '__main__':
    validar_modelo()
