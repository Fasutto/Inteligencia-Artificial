# Documentación del Proyecto: Aplicación de Detección Facial

## 1. Desarrollo de la aplicación

### A. Arquitectura modelo
Para este proyecto, se seleccionó una **Red Neuronal Convolucional (CNN)**.
*   **Justificación:** El sistema utiliza Redes Neuronales Convolucionales (CNN) para procesar imágenes y extraer automáticamente características faciales clave. Esto permite clasificar emociones con alta precisión en tiempo real, identificando patrones visuales complejos sin necesidad de ingeniería manual.

### B. Tipo de red neuronal
Se implementó el modelo **ResNet18** (Residual Network de 18 capas) utilizando la técnica de **Transfer Learning**.
*   **Implementación:** Se utilizó un modelo pre-entrenado en ImageNet y se modificó la última capa completamente conectada (Fully Connected) para tener 4 salidas, correspondientes a las 4 emociones: *Enojado, Feliz, Neutral, Triste*.
*   **Ventajas:**
    *   **Eficiencia:** ResNet18 es un modelo ligero y rápido, lo que permite inferencia en tiempo real en una CPU estándar.
    *   **Rendimiento:** El uso de conexiones residuales ("skip connections") permite entrenar redes profundas sin problemas de desvanecimiento de gradiente.
    *   **Transfer Learning:** Al usar pesos pre-entrenados, el modelo converge mucho más rápido y con menos datos, ya que ya "sabe" cómo identificar formas básicas.
*   **Desventajas:**
    *   Aunque es ligero, sigue requiriendo más recursos computacionales que métodos clásicos de ML (como SVM con HOG).
    *   Puede sobreajustarse (overfitting) si el dataset de emociones es muy diferente al de pre-entrenamiento, aunque esto se mitiga con Data Augmentation.

### C. Herramientas y Tecnologías
*   **Python:** Lenguaje de programación principal, elegido por su extenso ecosistema de IA.
*   **PyTorch (torch, torchvision):** Biblioteca de Deep Learning utilizada para construir, entrenar y guardar el modelo neuronal. Se eligió por su flexibilidad y facilidad de depuración.
*   **OpenCV (cv2):** Utilizado para el procesamiento de imágenes en tiempo real y la detección de rostros mediante Haar Cascades.
*   **Pillow (PIL):** Para la manipulación de imágenes antes de pasarlas al modelo.
*   **Scikit-learn & Matplotlib:** Para la generación de métricas de validación (matriz de confusión) y visualización de gráficas de entrenamiento.

### D. Conjuntos de datos
*   **Selección:** Se utilizó un conjunto de datos de imágenes faciales organizado en carpetas por categorías (Enojado, Feliz, Neutral, Triste). Este formato es compatible con `torchvision.datasets.ImageFolder`.
*   **Preprocesamiento y Calidad:**
    *   **Redimensionamiento:** Todas las imágenes se redimensionan a 224x224 píxeles para coincidir con la entrada esperada de ResNet.
    *   **Normalización:** Se normalizaron los valores de píxeles utilizando la media y desviación estándar de ImageNet `mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]`.
    *   **Data Augmentation:** Para mejorar la generalización y calidad del entrenamiento, se aplicaron transformaciones aleatorias al conjunto de entrenamiento: `RandomHorizontalFlip` (espejo) y `RandomRotation` (rotación de +/- 10 grados).


### E. Descripción del modelo
El modelo es un sistema de clasificación de imágenes basado en Deep Learning que toma como entrada una imagen de un rostro humano y predice su estado emocional.
*   **Propósito:** Automatizar la identificación de emociones para mejorar la interacción humano-computadora.
*   **Funcionamiento:** La imagen pasa por múltiples capas convolucionales que extraen mapas de características. Finalmente, una capa lineal clasifica estas características en una de las 4 categorías con un porcentaje de confianza.
*   **Trasfondo Teórico:** La detección facial se basa en encontrar patrones geométricos (ojos, nariz, boca), mientras que el reconocimiento emocional analiza las variaciones sutiles en estos patrones (comisuras de la boca, cejas fruncidas) que universalmente se asocian con estados afectivos.

### F. Fases de construcción
1.  **Recogida de datos:**
    *   Se organizó el dataset en directorios `train` y `test`. Se verificó que las imágenes fueran legibles y estuvieran correctamente etiquetadas en sus carpetas correspondientes.
2.  **Diseño de modelos:**
    *   Se seleccionó la arquitectura ResNet18. Se escribió el código para reemplazar la capa final (`model.fc`) para adaptar el modelo de 1000 clases (ImageNet) a nuestras 4 clases de emociones.
3.  **Entrenamiento:**
    *   Se utilizó el optimizador Adam con una tasa de aprendizaje de 0.001 y un Scheduler para reducir la tasa cada 7 épocas.
    *   Se entrenó durante 15 épocas, monitoreando la pérdida (loss) y la precisión (accuracy) tanto en entrenamiento como en validación.
    *   *Retos:* Ajustar el tamaño del batch para no saturar la memoria y encontrar el equilibrio entre underfitting y overfitting.
4.  **Pruebas:**
    *   Se evaluó el modelo final con el conjunto de datos de prueba (`test`) que el modelo nunca había visto durante el entrenamiento.

### G. Pruebas de validación
Para validar el rendimiento del modelo, se realizaron las siguientes pruebas:

1.  **Gráfica de Precisión (Accuracy):**
    *   Se generó una gráfica (`accuracy_plot.png`) que muestra la evolución de la precisión durante las épocas. Se observa una convergencia estable, alcanzando una precisión de validación satisfactoria (~76%).

2.  **Matriz de Confusión:**
    *   Se generó una matriz de confusión (`confusion_matrix.png`) para analizar qué emociones se confunden entre sí.
    *   *Análisis:* Esto permite ver, por ejemplo, si el modelo confunde frecuentemente "Triste" con "Neutral", lo cual es un error común debido a la sutileza de las expresiones.

3.  **Métrica de Éxito:**
    *   La métrica principal es la **Exactitud (Accuracy)** global en el conjunto de prueba.
    *   También se considera la fluidez de la detección en tiempo real (FPS) como métrica de éxito de la aplicación.

### H. Bibliotecas Utilizadas
El proyecto utiliza las siguientes bibliotecas de Python:

*   **torch & torchvision:** Framework de Deep Learning para construir y entrenar la red neuronal.
*   **opencv-python:** Procesamiento de imágenes y acceso a la cámara web.
*   **numpy:** Operaciones matemáticas y manipulación de matrices.
*   **matplotlib:** Generación de gráficas de precisión y matrices de confusión.
*   **pillow:** Manipulación de imágenes.
*   **scikit-learn:** Herramientas para métricas de evaluación.

### I. Estructura del Proyecto
```
Sistema Deteccion de Emociones/
├── Imagenes/               # Dataset de imágenes
│   ├── train/              # Conjunto de entrenamiento
│   └── test/               # Conjunto de prueba
├── accuracy_plot.png       # Gráfica de precisión generada
├── confusion_matrix.png    # Matriz de confusión generada
├── emotion_model.pth       # Modelo entrenado guardado
├── entrenar.py             # Script de entrenamiento
├── predecir.py             # Script para predecir una sola imagen
├── README.md               # Documentación del proyecto
├── requirements.txt        # Dependencias del proyecto
├── run.py                  # Demo en tiempo real con webcam
├── validar_modelo.py       # Script de validación y métricas
└── verificar_tamano.py     # Utilidad para verificar imágenes
```

### J. Ejecución del Programa
Para ejecutar correctamente el sistema, siga estos pasos en su terminal:

1.  **Configuración del Entorno Virtual:**
    Es recomendable ejecutar el proyecto dentro de un entorno virtual para aislar las dependencias.
    ```bash
    # Crear el entorno virtual
    python -m venv .venv   o   py -3 -m venv .venv (En caso de tener conflictos usando python, usar py -3)

    # Activar el entorno virtual (Windows)
    .venv\Scripts\activate
    ```

2.  **Instalación de dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Entrenamiento del modelo (Opcional si ya tiene `emotion_model.pth`):**
    ```bash
    python entrenar.py
    ```
    *   Este script entrenará la red neuronal y guardará el modelo en `emotion_model.pth`.

4.  **Validación del modelo:**
    ```bash
    python validar_modelo.py
    ```
    *   Genera la matriz de confusión y muestra la precisión por clase.

5.  **Detección en Tiempo Real:**
    ```bash
    python run.py
    ```
    *   Abre la cámara web y detecta emociones en vivo. Presione 'q' para salir.

### K. Video Presentacion
https://drive.google.com/file/d/1A8_xt0BvPp1VzjHFwgiY5R089-Ufy14V/view?usp=sharing