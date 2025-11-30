import torch
from torchvision import models, transforms
from PIL import Image
import sys
import os

# Función para predecir la emoción en una sola imagen estática.
def predecir_emocion(ruta_imagen):
    # Configuración
    num_clases = 4
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_modelo = os.path.join(script_dir, "emotion_model.pth")
    nombres_clases = ['Enojado', 'Feliz', 'Neutral', 'Triste'] # Debe coincidir con el orden de las carpetas (alfabético)

    dispositivo = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    # Cargar Modelo
    modelo = models.resnet18(weights=None) # No es necesario descargar pesos de nuevo, cargamos los nuestros
    num_ftrs = modelo.fc.in_features
    modelo.fc = torch.nn.Linear(num_ftrs, num_clases)
    
    if not os.path.exists(ruta_modelo):
        print("Archivo del modelo no encontrado. Por favor entrene el modelo primero.")
        return

    modelo.load_state_dict(torch.load(ruta_modelo, map_location=dispositivo))
    modelo = modelo.to(dispositivo)
    modelo.eval()

    # Preprocesar Imagen
    transformacion = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    try:
        # Cargar imagen y convertir a RGB
        imagen = Image.open(ruta_imagen).convert('RGB')
        # Aplicar transformaciones y agregar dimensión de lote (batch dimension)
        # El modelo espera un lote de imágenes [Batch, Canales, Alto, Ancho], así que agregamos la dimensión 0.
        imagen = transformacion(imagen).unsqueeze(0) 
        imagen = imagen.to(dispositivo)

        # Realizar predicción sin calcular gradientes
        with torch.no_grad():
            salidas = modelo(imagen)
            _, preds = torch.max(salidas, 1) # Obtener índice de la clase con mayor valor
            probs = torch.nn.functional.softmax(salidas, dim=1) # Convertir salidas a probabilidades (0 a 1)
        
        clase_predicha = nombres_clases[preds[0]]
        probabilidad = probs[0][preds[0]].item()

        print(f"Predicción: {clase_predicha}")
        print(f"Confianza: {probabilidad:.2%}")
        
        return clase_predicha, probabilidad

    except Exception as e:
        print(f"Error procesando imagen: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ruta_imagen = sys.argv[1]
        predecir_emocion(ruta_imagen)
    else:
        print("Uso: python predecir.py <ruta_a_la_imagen>")
