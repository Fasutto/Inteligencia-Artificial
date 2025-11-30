
# Importar librerías necesarias
import torch  # Librería principal de PyTorch para aprendizaje profundo
import torch.nn as nn  # Módulos de redes neuronales (capas, funciones de pérdida)
import torch.optim as optim  # Algoritmos de optimización (Adam, SGD, etc.)
from torchvision import datasets, models, transforms  # Herramientas para visión por computadora
from torch.utils.data import DataLoader  # Clase para cargar datos en lotes de manera eficiente
import os  # Para interactuar con el sistema operativo (rutas de archivos)
import time  # Para medir el tiempo de ejecución
import copy  # Para copiar objetos (guardar los mejores pesos)
import matplotlib.pyplot as plt  # Para graficar resultados

# Función principal para configurar, entrenar y guardar el modelo de detección de emociones.
def entrenar_modelo():
    # Configuración
    # Obtener la ruta absoluta del directorio donde se encuentra el script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dir_datos = os.path.join(script_dir, "Imagenes")
    num_clases = 4
    tamano_lote = 32
    num_epocas = 15
    tamano_entrada = 224  # ResNet espera 224x224

    # Aumento de Datos y Normalización
    # Las transformaciones ayudan a que el modelo sea más robusto y generalice mejor.
    transformaciones_datos = {
        'train': transforms.Compose([
            transforms.Resize((tamano_entrada, tamano_entrada)), # Redimensiona imagen al tamaño esperado por ResNet
            transforms.RandomHorizontalFlip(), # Voltea horizontalmente aleatoriamente (aumento de datos)
            transforms.RandomRotation(10), # Rotar levemente la imagen (aumento de datos)
            transforms.ToTensor(), # Convertir imagen a tensor de PyTorch
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]) # Normaliza con medias y desviaciones estándar de ImageNet
        ]),
        'test': transforms.Compose([
            transforms.Resize((tamano_entrada, tamano_entrada)), # Solo redimensiona para validación
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
    }

    # 1. CARGA DE DATOS
    print("Cargando datos...")
    # Carga los datasets usando ImageFolder
    # ImageFolder asume que las imágenes están organizadas en carpetas por clase.
    datasets_imagenes = {x: datasets.ImageFolder(os.path.join(dir_datos, x), transformaciones_datos[x])
                      for x in ['train', 'test']}
    
    # Crea DataLoaders
    # Los DataLoaders manejan la carga de datos en lotes (batches) y el barajado (shuffling).
    cargadores_datos = {x: DataLoader(datasets_imagenes[x], batch_size=tamano_lote, shuffle=True, num_workers=0)
                   for x in ['train', 'test']}
    
    tamanos_dataset = {x: len(datasets_imagenes[x]) for x in ['train', 'test']}
    nombres_clases_raw = datasets_imagenes['train'].classes
    mapa_traduccion = {'angry': 'Enojado', 'happy': 'Feliz', 'neutral': 'Neutral', 'sad': 'Triste'}
    nombres_clases = [mapa_traduccion.get(nombre, nombre) for nombre in nombres_clases_raw]
    
    print(f"Clases: {nombres_clases}")
    print(f"Muestras de entrenamiento: {tamanos_dataset['train']}")
    print(f"Muestras de prueba: {tamanos_dataset['test']}")

    dispositivo = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"Usando dispositivo: {dispositivo}")

    # 2. CONFIGURACIÓN DE LA RED NEURONAL
    # Carga ResNet18 Pre-entrenado
    print("Cargando modelo ResNet18...")
    # Usamos pesos pre-entrenados en ImageNet para aprovechar el aprendizaje previo (Transfer Learning)
    modelo = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
    
    # Modifica la capa final para 4 clases
    # La capa original tiene 1000 salidas (clases de ImageNet), la cambiamos a 4 (nuestras emociones)
    num_ftrs = modelo.fc.in_features
    modelo.fc = nn.Linear(num_ftrs, num_clases)

    modelo = modelo.to(dispositivo)

    # Define criterio de pérdida (CrossEntropyLoss es estándar para clasificación)
    criterio = nn.CrossEntropyLoss()
    
    # Define optimizador (Adam es un algoritmo eficiente de descenso de gradiente)
    optimizador = optim.Adam(modelo.parameters(), lr=0.001)
    
    # Define scheduler para reducir la tasa de aprendizaje cada 7 épocas
    # Esto ayuda a afinar el entrenamiento conforme avanza
    programador_lr = optim.lr_scheduler.StepLR(optimizador, step_size=7, gamma=0.1)

    inicio = time.time()

    mejores_pesos_modelo = copy.deepcopy(modelo.state_dict())
    mejor_precision = 0.0
    
    historial_precision_entrenamiento = []
    historial_precision_validacion = []

    # 3. BUCLE DE ENTRENAMIENTO Y VALIDACIÓN
    for epoca in range(num_epocas):
        print(f'Época {epoca}/{num_epocas - 1}')
        print('-' * 10)

        # Cada época tiene una fase de entrenamiento y validación
        for fase in ['train', 'test']:
            if fase == 'train':
                modelo.train()  # Establecer modelo en modo entrenamiento
            else:
                modelo.eval()   # Establece el modelo en modo evaluación

            perdida_actual = 0.0
            correctos_actuales = 0

            # Itera sobre los datos.
            for entradas, etiquetas in cargadores_datos[fase]:
                entradas = entradas.to(dispositivo)
                etiquetas = etiquetas.to(dispositivo)

                # Reinicia los gradientes de los parámetros
                optimizador.zero_grad()

                # Adelante (Forward pass)
                # Rastrea historial de gradientes solo en entrenamiento
                with torch.set_grad_enabled(fase == 'train'):
                    salidas = modelo(entradas) # Obtiene predicciones del modelo
                    _, preds = torch.max(salidas, 1) # Obtiene la clase con mayor probabilidad
                    perdida = criterio(salidas, etiquetas) # Calcula la diferencia entre predicción y realidad

                    # Retropropagación + optimización solo en fase de entrenamiento
                    if fase == 'train':
                        perdida.backward() # Calcular gradientes
                        optimizador.step() # Actualizar pesos

                # Estadísticas
                perdida_actual += perdida.item() * entradas.size(0)
                correctos_actuales += torch.sum(preds == etiquetas.data)

            if fase == 'train':
                programador_lr.step()

            perdida_epoca = perdida_actual / tamanos_dataset[fase]
            precision_epoca = correctos_actuales.double() / tamanos_dataset[fase]

            print(f'{fase} Pérdida: {perdida_epoca:.4f} Precisión: {precision_epoca:.4f}')
            
            if fase == 'train':
                historial_precision_entrenamiento.append(precision_epoca.item())
            else:
                historial_precision_validacion.append(precision_epoca.item())

            # Copia profunda del modelo
            if fase == 'test' and precision_epoca > mejor_precision:
                mejor_precision = precision_epoca
                mejores_pesos_modelo = copy.deepcopy(modelo.state_dict())

        print()

    tiempo_transcurrido = time.time() - inicio
    print(f'Entrenamiento completado en {tiempo_transcurrido // 60:.0f}m {tiempo_transcurrido % 60:.0f}s')
    print(f'Mejor Precisión de validación: {mejor_precision:4f}')

    # 4. GUARDADO DEL MODELO Y GENERACIÓN DE GRÁFICA
    # Carga los mejores pesos del modelo
    modelo.load_state_dict(mejores_pesos_modelo)
    
    # Guarda el modelo
    ruta_guardado = r"c:/Users/Hirai Momo/Documents/01 - Inteligencia Artificial/Unidad 4/Sistema Deteccion de Emociones/emotion_model.pth"
    torch.save(modelo.state_dict(), ruta_guardado)
    print(f"Modelo guardado en {ruta_guardado}")
    
    # Grafica la precisión
    plt.figure(figsize=(10, 5))
    plt.title("Precisión de Entrenamiento y Validación")
    plt.plot(historial_precision_entrenamiento, label="Entrenamiento")
    plt.plot(historial_precision_validacion, label="Validación")
    plt.xlabel("Épocas")
    plt.ylabel("Precisión")
    plt.legend()
    plt.savefig(r"c:/Users/Hirai Momo/Documents/01 - Inteligencia Artificial/Unidad 4/Sistema Deteccion de Emociones/accuracy_plot.png")
    print("Gráfica de precisión guardada.")

if __name__ == '__main__':
    entrenar_modelo()
