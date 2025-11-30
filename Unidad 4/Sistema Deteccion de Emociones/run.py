import cv2  # OpenCV para procesamiento de imágenes y captura de video
import torch  # PyTorch para cargar y usar el modelo de IA
from torchvision import models, transforms  # Utilidades para modelos de visión
from PIL import Image  # Librería de imágenes de Python para manipulación
import numpy as np  # Librería para manejo de matrices numéricas
import os  # Para manejo de rutas de archivos

def deteccion_emociones_tiempo_real():
    """
    Función principal para ejecutar la detección de emociones en tiempo real.
    Captura video de la cámara web, detecta rostros, y utiliza el modelo entrenado
    para predecir la emoción de cada rostro detectado.
    """
    # Configuración
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_modelo = os.path.join(script_dir, "emotion_model.pth")
    nombres_clases = ['Enojado', 'Feliz', 'Neutral', 'Triste']
    
    dispositivo = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"Usando dispositivo: {dispositivo}")

    # Cargar Modelo
    print("Cargando modelo...")
    modelo = models.resnet18(weights=None)
    num_ftrs = modelo.fc.in_features
    modelo.fc = torch.nn.Linear(num_ftrs, len(nombres_clases))
    
    if not os.path.exists(ruta_modelo):
        print(f"Error: Archivo del modelo '{ruta_modelo}' no encontrado.")
        print("Por favor ejecute 'entrenar.py' primero para entrenar el modelo.")
        return

    modelo.load_state_dict(torch.load(ruta_modelo, map_location=dispositivo))
    modelo = modelo.to(dispositivo)
    modelo.eval()
    print("Modelo cargado.")

    # Detección de Rostros (Haar Cascade)
    # Cargamos un clasificador pre-entrenado para detectar rostros frontales
    cascada_rostros = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Preprocesamiento
    # Preprocesamiento
    # Definimos las mismas transformaciones que usamos en el entrenamiento
    # para que el modelo reciba los datos en el formato que espera.
    transformacion = transforms.Compose([
        transforms.Resize((224, 224)), # Redimensionar a 224x224
        transforms.ToTensor(), # Convertir a tensor
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]) # Normalizar
    ])

    # Abrir Cámara Web
    captura = cv2.VideoCapture(0)
    if not captura.isOpened():
        print("Error: No se pudo abrir la cámara web.")
        return

    print("Iniciando cámara web... Presione 'q' para salir.")

    # Bucle principal de captura de video
    while True:
        ret, cuadro = captura.read()
        if not ret:
            print("Fallo al capturar el cuadro")
            break

        # Convertir a escala de grises para detección de rostros (requerido por Haar Cascade)
        gris = cv2.cvtColor(cuadro, cv2.COLOR_BGR2GRAY)
        # Detectar rostros en la imagen
        rostros = cascada_rostros.detectMultiScale(gris, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in rostros:
            # Dibujar rectángulo alrededor del rostro
            cv2.rectangle(cuadro, (x, y), (x+w, y+h), (255, 0, 0), 2)

            # Extraer ROI (Región de Interés) del rostro
            roi_rostro = cuadro[y:y+h, x:x+w]
            
            # Convertir a Imagen PIL
            rostro_pil = Image.fromarray(cv2.cvtColor(roi_rostro, cv2.COLOR_BGR2RGB))

            # Preprocesar
            # Transformamos la imagen del rostro para que sea compatible con el modelo
            tensor_rostro = transformacion(rostro_pil).unsqueeze(0).to(dispositivo)

            # Predecir
            with torch.no_grad():
                salidas = modelo(tensor_rostro)
                _, preds = torch.max(salidas, 1)
                probs = torch.nn.functional.softmax(salidas, dim=1)
                
            prediccion = nombres_clases[preds[0]]
            confianza = probs[0][preds[0]].item()

            # Mostrar etiqueta
            # Escribimos la emoción predicha y la confianza sobre el cuadro de video
            etiqueta = f"{prediccion} ({confianza:.1%})"
            cv2.putText(cuadro, etiqueta, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)

        cv2.imshow('Detector de Emociones', cuadro)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    captura.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    deteccion_emociones_tiempo_real()
