# Sistema de Detección de Spam con ML y GUI.
Este proyecto implementa un robusto sistema de clasificación de correos electrónicos para distinguir entre spam y correo legítimo (ham). Utiliza un modelo de Machine Learning (Naïve Bayes) y una Interfaz Gráfica de Usuario (GUI) en Tkinter, siguiendo un patrón de diseño MVC (Modelo-Vista-Controlador) para una arquitectura limpia y modular.

# Propósito
Detectar automáticamente si un correo es spam o no, ofrecer una interfaz para inspeccionar los datos y facilitar entrenar / cargar el modelo de ML de forma sencilla.

# Funciones principales
- Clasificar correos (spam vs ham) usando un pipeline TF‑IDF + MultinomialNB.
- Mostrar el dataset (Emails.csv) en una tabla y permitir seleccionar filas para autocompletar los campos.
- Permitir al usuario pegar/editar un correo (asunto + mensaje) y obtener la predicción con un botón.
- Cargar un modelo ya entrenado (spam_detector_model.pkl) o entrenarlo automáticamente desde el CSV si no existe.
- Evaluar el detector sobre todos los correos etiquetados al arrancar y reportar el porcentaje de acierto en consola.

# Estructura del Directorio
El proyecto se organiza en la carpeta raíz Deteccion de Spam con la siguiente estructura:

Deteccion de Spam/
├── data/
│   └── Emails.csv              - Conjunto de datos para entrenamiento.
├── models/
│   └── spam_detector_model.pkl - Modelo ML entrenado (guardado).
├── controller.py               - Lógica del Controlador (enlaza la Vista y el Modelo, maneja eventos).
├── detector.py                 - Módulo principal (Punto de inicio de la aplicación).
├── model.py                    - Lógica del Modelo (Entrenamiento, carga de datos y serialización del modelo).
└── view.py                     - Lógica de la Vista (Construcción de la Interfaz Gráfica Tkinter).

# Instalación y Requisitos
Asegúrate de tener Python 3.8+ instalado.

1. Requisitos de Python
- Python 3.10+ (3.11/3.12/3.13 funcionan).
- Paquetes: `pandas`, `scikit-learn`, `joblib`. `tkinter` suele venir con Python en Windows.

2. Configuración de Archivos
Asegúrate de que tus archivos estén en las ubicaciones correctas para que el programa pueda cargarlos:

  - El archivo de datos Emails.csv debe estar dentro de la carpeta data/.
  - El archivo del modelo spam_detector_model.pkl debe estar dentro de la carpeta models/.

  - Nota: El módulo model.py creará y guardará este archivo automáticamente si no existe al iniciar la aplicación.

# Uso y Ejecución del Programa
Para iniciar la aplicación, navega a la carpeta raíz Deteccion de Spam en tu terminal y ejecuta el módulo principal main.py:

- python main.py

# Funcionalidad de la Interfaz (GUI)
La aplicación es redimensionable y ofrece la siguiente funcionalidad clave:

Análisis en Tiempo Real: Ingresa el Asunto y el Mensaje en los campos de entrada. Al hacer clic en "Analizar Correo", el modelo predice la categoría.

Visualización de Resultados: El resultado de la clasificación se muestra de forma destacada:

- CORREO LEGÍTIMO (en verde)
- ¡SPAM DETECTADO! (en rojo)

Visor de Datos: La sección inferior muestra las primeras filas de Emails.csv. Esta tabla (TreeView) cuenta con scroll horizontal y vertical y permite seleccionar una fila para cargar sus datos directamente en los campos de entrada.

# Metodología de Machine Learning
El núcleo del sistema de detección es un clasificador Multinomial Naïve Bayes, ideal para tareas de filtrado basadas en el contexto del texto.

  # Modelo: 
  MultinomialNB dentro de un Pipeline.

  # Preprocesamiento: 
  Se utiliza el Vectorizador TF-IDF (Frecuencia de Término - Frecuencia Inversa de Documento) para convertir el texto a vectores numéricos, dando peso a las palabras más distintivas de cada clase.

  # Enfoque de Seguridad: 
  El modelo está optimizado para una alta Precisión (Precision), garantizando que los correos legítimos no sean bloqueados.

# Créditos.
- Desarrollado por: *Espinoza Felix Fausto Gabriel*
- Fecha de entrega: *12 de octubre de 2025*

# Reflexion y Analisis.
  
  # Resumen del enfoque actual
  - Pipeline simple: TfidfVectorizer (texto) + MultinomialNB (clasificador).
  - Entrenamiento sobre la columna Message (y en la evaluación se concatena Asunto + Message).
  - Etiquetas: 'ham' -> 0, 'spam' -> 1'.
  - Evaluación al inicio: controller imprime % acierto sobre filas etiquetadas.
  
  # Ventajas
  - Simplicidad y rapidez: TF‑IDF + Naive Bayes es ligero, rápido de entrenar y de inferir. Útil para prototipos.
  - Requiere pocas dependencias y es fácil de entender.
  - Buen rendimiento en problemas de texto con palabras distintivas (palabras que aparecen frecuentemente en spam).
  - Pipeline reproducible y serializable (joblib), lo cual facilita despliegue en la GUI.

  # Desventajas
  - Mala generalización a tokens raros/únicos como URLs: cada URL es tratado como palabra distinta; el modelo no generaliza bien a enlaces nuevos.
  - No captura señales estructurales (número de enlaces, dominios, acortadores, mayúsculas, símbolos monetarios) porque solo usa texto bruto.
  - MultinomialNB asume independencia condicional de features y puede ser superado por clasificadores discriminativos (LogisticRegression) o por ensembles.
  - Sensible al vocabulario del dataset; necesita más y diversa data para reducir sesgo.

  # Opinion
  - El modelo actual usa TF‑IDF + MultinomialNB: es rápido y funciona bien cuando hay palabras repetidas y distintivas en spam.
  - Mejora recomendada: normalizar URLs a un token, añadir features como has_url/num_urls y usar FeatureUnion (TF‑IDF + features) con un clasificador discriminativo (ej. LogisticRegression).