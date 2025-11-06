import os                                                       # Sirve para manejar rutas de archivos.
import joblib                                                   # Sirve para guardar y cargar modelos ML.
import pandas as pd                                             # Sirve para manejar DataFrames.
from sklearn.model_selection import train_test_split            # Sirve para dividir datos en train/test.
from sklearn.feature_extraction.text import TfidfVectorizer     # Sirve para convertir texto a vectores TF-IDF.
from sklearn.naive_bayes import MultinomialNB                   # Sirve para importar el clasificador Naive Bayes.
from sklearn.pipeline import Pipeline                           # Sirve para crear un pipeline de procesamiento y modelo.

# Define rutas de archivos.
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))

# Archivo del modelo en models/ (se crea si no existe).
MODEL_FILE = os.path.join(MODULE_DIR, 'models', 'spam_detector_model.pkl')

# Nombre del archivo CSV esperado en data/.
DATA_FILE = 'Emails.csv'


# En este modulo se realiza lo siguiente:
# - Buscar el CSV en data/ o usar una ruta preferida si se pasa.
# - Leer el CSV en un DataFrame (o devolver uno vacío si no existe).
# - Entrenar un pipeline TF-IDF + NaiveBayes y guardarlo en models/ si no existe.
# - Cargar el modelo desde models/ si ya existe.


# Buscar el CSV solo en la carpeta `data/`.
def find_data_file(preferred=None):
    module_dir = os.path.dirname(os.path.abspath(__file__))
    only_path = os.path.join(module_dir, 'data', DATA_FILE)
    return os.path.abspath(only_path)

# Entrena y guarda el modelo (pipeline TF-IDF + NaiveBayes).
def train_and_save_model(data_file=None, model_file=MODEL_FILE):

    # Nota: el entrenamiento usa solo la columna 'Message' y mapea.

    # Encuentra el CSV.
    data_path = find_data_file(data_file)
    try:
        # Leer el CSV.
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        raise

    # X = textos, y = etiquetas numéricas
    X = df['Message']
    y = df['Categoría'].map({'ham': 0, 'spam': 1})

    # Separa para entrenar rápidamente (no se usa el test aquí).
    X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Crea pipeline: vectorizador + clasificador
    model_pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words=None, lowercase=True)),
        ('nb', MultinomialNB())
    ])

    # Entrena el modelo.
    model_pipeline.fit(X_train, y_train)
    # Guarda el modelo entrenado.
    joblib.dump(model_pipeline, model_file)

    return model_pipeline

# Intenta cargar el modelo desde un .pkl; si no existe o falla, reentrena.
def load_model_or_train(model_file=MODEL_FILE, data_file=None):
    # Buscar el .pkl.
    if os.path.exists(model_file):
        try:
            # Cargar el modelo.
            return joblib.load(model_file)
        except Exception:
            # Si el archivo está corrupto o incompatible, se reentrena.
            return train_and_save_model(data_file=data_file, model_file=model_file)
    else:
        # Si no existe el .pkl, se entrena desde el CSV.
        return train_and_save_model(data_file=data_file, model_file=model_file)

# Lee el CSV y devuelve un DataFrame.
def load_data(data_file=None):
    # Buscar el CSV.
    data_path = find_data_file(data_file)
    try:
        # Leer el CSV
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        # Devuelve un DF vacío con columnas esperadas.
        df = pd.DataFrame(columns=["Categoría", "Correo", "Asunto", "Message"])
    return df

# Fin del archivo model.py