
# ------------------------------------------------------------
# Sistema de Recomendación de Películas (backend)
#
# Este archivo contiene la implementación del servidor Flask que
# expone endpoints para búsqueda de películas, recomendaciones
# por contenido y colaborativas, y para registrar valoraciones.
#
# Estructura general:
# - Carga y preprocesamiento de datos (MovieLens csv)
# - Recomendador por contenido (TF-IDF sobre 'genres' + coseno)
# - Recomendador colaborativo (TruncatedSVD sobre matriz user×item)
# - Endpoints REST para la UI frontend
# ------------------------------------------------------------

import re
import pandas as pd
from flask import Flask, jsonify, request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from flask_cors import CORS # Importa CORS
from rapidfuzz import process, fuzz
import numpy as np
from sklearn.decomposition import TruncatedSVD
import os
import pathlib
import time

# --- 1. PREPARACIÓN DE DATOS Y MODELO ---
# En esta sección se cargan los CSV de MovieLens, se limpian
# los géneros para que TF-IDF no falle, y se construye la matriz
# TF-IDF para el recomendador por contenido.

# Cargar el dataset de películas
# Se asume que existe la carpeta `ml-latest-small/` en la raíz
# con al menos `movies.csv`. Si no existe, el proceso se detiene.
try:
    movies = pd.read_csv('ml-latest-small/movies.csv')
except FileNotFoundError:
    print("Error: El archivo 'movies.csv' no se encontró. Asegúrate de que la ruta sea correcta.")
    exit()

# Preprocesamiento: limpiar y normalizar la columna 'genres'
# Algunas entradas pueden tener separadores '|' o caracteres
# mal formateados; esta función los normaliza para producir
# texto coherente para TF-IDF.
def clean_genres(s):
    if pd.isna(s):
        return ''
    s = str(s)
    # Reemplazar separador '|' por espacios
    s = s.replace('|', ' ')
    # Colapsar espacios múltiples
    s = re.sub(r"\s+", ' ', s).strip()
    # Si la cadena está formada por letras separadas por espacios (ej. 'A d v e n t u r e'), unirlas
    parts = s.split(' ')
    if len(parts) > 1 and all(len(p) == 1 for p in parts):
        s = ''.join(parts)
    return s

# Aplicar limpieza a la columna 'genres' del dataset
movies['genres'] = movies['genres'].apply(clean_genres)

# Crear un vectorizador TF-IDF para convertir los géneros en una matriz de características numéricas.
# stop_words='english' elimina palabras comunes que no aportan significado.
tfidf = TfidfVectorizer(stop_words='english')

# Construir la matriz TF-IDF ajustando y transformando los datos
# Resultado: tfidf_matrix es una matriz densa/esparsa (sparse) que
# representa cada película por un vector según sus géneros.
tfidf_matrix = tfidf.fit_transform(movies['genres'])

# Calcular la matriz de similitud del coseno. Esto nos dará una puntuación de similitud entre todas las películas.
# cosine_sim[i, j] es la similitud entre la película i y la j.
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

# Crear un mapa inverso de títulos de películas e índices del DataFrame para buscar películas por título fácilmente.
# indices: map title -> index en el DataFrame `movies`.
indices = pd.Series(movies.index, index=movies['title']).drop_duplicates()

# --- Preparar modelo colaborativo simple (TruncatedSVD sobre user-item) ---
# Aquí se carga `ratings.csv` si existe y se prepara el pipeline
# de factorization (TruncatedSVD). Las variables globales
# `cf_user_factors` y `cf_item_factors` guardan los factores.
try:
    ratings = pd.read_csv('ml-latest-small/ratings.csv')
except FileNotFoundError:
    ratings = None

cf_user_factors = None
cf_item_factors = None
popular_movies = []
# Carpeta donde se guardan los factores CF para acelerar reinicios
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
os.makedirs(MODEL_DIR, exist_ok=True)
CF_FACTORS_PATH = os.path.join(MODEL_DIR, 'cf_factors.npz')

def save_cf_factors(user_ids, movie_ids, user_factors, item_factors):
    # Guarda los factores en disco en formato comprimido (.npz)
    np.savez_compressed(CF_FACTORS_PATH, user_ids=user_ids, movie_ids=movie_ids, user_factors=user_factors, item_factors=item_factors)

def load_cf_factors():
    if not os.path.exists(CF_FACTORS_PATH):
        return None
    data = np.load(CF_FACTORS_PATH, allow_pickle=True)
    return (data['user_ids'], data['movie_ids'], data['user_factors'], data['item_factors'])


def train_cf():
    #Entrena/recalcula los factores CF usando TruncatedSVD y actualiza las variables globales. Guarda los factores en CF_FACTORS_PATH.
    global cf_user_factors, cf_item_factors, popular_movies
    if ratings is None or ratings.empty:
        cf_user_factors = None
        cf_item_factors = None
        popular_movies = []
        return

    # Identificar usuarios y películas presentes en los ratings
    user_ids = ratings['userId'].unique()
    movie_ids = movies['movieId'].unique()
    # Mapas para convertir id -> índice en la matriz R
    user_map = {u:i for i,u in enumerate(user_ids)}
    movie_map = {m:i for i,m in enumerate(movie_ids)}

    # Construir la matriz usuario × película (pivot table)
    pivot = ratings.pivot_table(index='userId', columns='movieId', values='rating', fill_value=0.0)
    pivot = pivot.reindex(index=user_ids, columns=movie_ids, fill_value=0.0)
    R = pivot.values.astype(np.float32)

    # Rellenar los valores faltantes (0) con la media de cada usuario
    # Esto reduce el sesgo por sparsity antes de aplicar SVD.
    nonzero_counts = (R != 0).sum(axis=1)
    sums = R.sum(axis=1)
    user_means = np.divide(sums, nonzero_counts, out=np.zeros_like(sums), where=nonzero_counts!=0)
    mask_zero = (R == 0)
    R[mask_zero] = np.take(user_means, np.nonzero(mask_zero)[0])

    # Entrenar TruncatedSVD para obtener factores latentes
    svd = TruncatedSVD(n_components=50, random_state=42)
    user_factors = svd.fit_transform(R)
    item_factors = svd.components_.T

    # Guardar factores en variables globales para uso en runtime
    cf_user_factors = (user_ids, user_map, user_factors)
    cf_item_factors = (movie_ids, movie_map, item_factors)

    # save factors
    try:
        save_cf_factors(user_ids, movie_ids, user_factors, item_factors)
        print(f"[INFO] Saved CF factors to {CF_FACTORS_PATH}")
    except Exception as e:
        print(f"[WARN] Could not save CF factors: {e}")

    # Actualizar la lista de películas populares (fallback si no hay CF)
    pop = ratings.groupby('movieId').agg({'rating':['count','mean']})
    pop.columns = ['count','mean']
    pop = pop.reset_index().merge(movies[['movieId','title']], on='movieId', how='left')
    pop = pop.sort_values('count', ascending=False)
    popular_movies = pop['title'].dropna().tolist()
# Si tenemos ratings, intentamos cargar factores precomputados para
# acelerar el arranque; si fallan, los recalculamos.
if ratings is not None and not ratings.empty:
    # Intentar cargar factores CF precomputados desde disco para acelerar el arranque
    loaded = load_cf_factors()
    if loaded is not None:
        try:
            lu_ids, lm_ids, l_user_factors, l_item_factors = loaded
            # Reconstruir mapas y factores a partir del archivo
            user_ids = np.asarray(lu_ids)
            movie_ids = np.asarray(lm_ids)
            user_map = {u:i for i,u in enumerate(user_ids)}
            movie_map = {m:i for i,m in enumerate(movie_ids)}
            user_factors = l_user_factors
            item_factors = l_item_factors
            cf_user_factors = (user_ids, user_map, user_factors)
            cf_item_factors = (movie_ids, movie_map, item_factors)
            print(f"[INFO] Loaded CF factors from {CF_FACTORS_PATH}")
        except Exception as e:
            print(f"[WARN] Failed to load CF factors: {e}. Recomputing.")
            loaded = None

    if loaded is None:
        # Construir la matriz usuario×película desde los ratings y entrenar SVD
        user_ids = ratings['userId'].unique()
        movie_ids = movies['movieId'].unique()
        user_map = {u:i for i,u in enumerate(user_ids)}
        movie_map = {m:i for i,m in enumerate(movie_ids)}

        # Crear tabla pivot (usuario × película)
        pivot = ratings.pivot_table(index='userId', columns='movieId', values='rating', fill_value=0.0)
        pivot = pivot.reindex(index=user_ids, columns=movie_ids, fill_value=0.0)
        R = pivot.values.astype(np.float32)

        # Rellenar ceros con la media del usuario (vectorizado)
        nonzero_counts = (R != 0).sum(axis=1)
        sums = R.sum(axis=1)
        user_means = np.divide(sums, nonzero_counts, out=np.zeros_like(sums), where=nonzero_counts!=0)
        mask_zero = (R == 0)
        R[mask_zero] = np.take(user_means, np.nonzero(mask_zero)[0])

        # Entrenar TruncatedSVD para obtener factores latentes
        svd = TruncatedSVD(n_components=50, random_state=42)
        user_factors = svd.fit_transform(R)
        item_factors = svd.components_.T

        # Guardar factores en variables globales
        cf_user_factors = (user_ids, user_map, user_factors)
        cf_item_factors = (movie_ids, movie_map, item_factors)

        # Intentar persistir factores a disco
        try:
            save_cf_factors(user_ids, movie_ids, user_factors, item_factors)
            print(f"[INFO] Saved CF factors to {CF_FACTORS_PATH}")
        except Exception as e:
            print(f"[WARN] Could not save CF factors: {e}")

    # Lista de películas populares (fallback si CF no está disponible)
    pop = ratings.groupby('movieId').agg({'rating':['count','mean']})
    pop.columns = ['count','mean']
    pop = pop.reset_index().merge(movies[['movieId','title']], on='movieId', how='left')
    pop = pop.sort_values('count', ascending=False)
    popular_movies = pop['title'].dropna().tolist()

# --- 2. FUNCIÓN DE RECOMENDACIÓN ---

def get_recommendations(title, cosine_sim=cosine_sim):
    # Esta función toma un título de película y devuelve una lista de 10 películas más similares.
    # Verificar si la película está en nuestro dataset
    if title not in indices:
        return [] # Retorna una lista vacía si no se encuentra

    # Obtener el índice de la película que coincide con el título
    idx = indices[title]

    # Obtener las puntuaciones de similitud de todas las películas con esa película
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Ordenar las películas según las puntuaciones de similitud en orden descendente
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Obtener las puntuaciones de las 10 películas más similares (excluyendo la propia película, por eso empezamos en 1)
    sim_scores = sim_scores[1:11]

    # Obtener los índices de esas películas
    movie_indices = [i[0] for i in sim_scores]

    # Devolver los títulos de las 10 películas más similares
    return movies['title'].iloc[movie_indices].tolist()


def recommend_for_user(user_id, n=10):
    # Recomendaciones basadas en filtrado colaborativo usando TruncatedSVD embeddings. Si el usuario o el modelo no existen, devuelve películas populares.

    if cf_user_factors is None or cf_item_factors is None or ratings is None:
        return popular_movies[:n]

    user_ids, user_map, user_factors = cf_user_factors
    movie_ids, movie_map, item_factors = cf_item_factors

    # si el usuario no está en el mapeo, devolver fallback
    if user_id not in user_map:
        return popular_movies[:n]

    uidx = user_map[user_id]
    uvec = user_factors[uidx]  # shape (k,)


    # movies the user has already rated
    user_rated = set(ratings[ratings['userId'] == user_id]['movieId'].unique())

    preds = []
    # iterar por películas en el dataset y predecir score mediante producto punto
    for mid in movie_ids:
        if mid in user_rated:
            continue
        midx = movie_map.get(mid)
        if midx is None:
            continue
        ivec = item_factors[midx]
        score = float(np.dot(uvec, ivec))
        preds.append((mid, score))

    preds = sorted(preds, key=lambda x: x[1], reverse=True)[:n]
    id_to_title = movies.set_index('movieId')['title'].to_dict()
    id_to_genres = movies.set_index('movieId')['genres'].to_dict()
    results = []
    for mid, score in preds:
        title = id_to_title.get(mid)
        if title is None:
            continue
        genres = id_to_genres.get(mid, '')
        results.append({'movieId': int(mid), 'title': title, 'genres': genres, 'score': float(score)})

    # fallback to popular (as objects) if not enough
    if len(results) < n:
        for t in popular_movies:
            # popular_movies contains titles
            row = movies[movies['title'] == t]
            if row.empty:
                continue
            mid = int(row.iloc[0]['movieId'])
            if any(r['movieId'] == mid for r in results):
                continue
            results.append({'movieId': mid, 'title': t, 'genres': row.iloc[0]['genres'], 'score': 0.0})
            if len(results) >= n:
                break
    return results

# --- 3. CONFIGURACIÓN DE LA API CON FLASK ---

# Iniciar la aplicación Flask
app = Flask(__name__)
# Habilitar CORS para permitir que nuestra app de React se comunique con este servidor
CORS(app) 

# Definir el "endpoint" o la URL de nuestra API
@app.route('/recommend/<movie_title>')
def recommend(movie_title):
    recommendations = get_recommendations(movie_title)
    # Devolver las recomendaciones en formato JSON
    return jsonify(recommendations)

# lista de títulos
titles = movies['title'].tolist()

@app.route('/search/title/<q>')
def search_title(q):
    # obtiene las 10 mejores coincidencias con ratio mínimo 60
    matches = process.extract(q, titles, scorer=fuzz.WRatio, limit=10)
    # matches -> [(title, score, index), ...]
    results = [ {"title": m[0], "score": m[1]} for m in matches if m[1] >= 60 ]
    return jsonify(results)

@app.route('/search/autocomplete/<prefix>')
def autocomplete(prefix):
    vals = movies[movies['title'].str.lower().str.startswith(prefix.lower())]['title'].head(10).tolist()
    return jsonify(vals)

@app.route('/search/filter')
def filter_movies():
    genre = request.args.get('genre')  # e.g. 'Action'
    year = request.args.get('year')    # e.g. '1995'
    df = movies
    if genre:
        df = df[df['genres'].str.contains(genre, case=False, na=False)]
    if year:
        df = df[df['title'].str.contains(f'({year})')]  # o columna year si la tienes
    return jsonify(df[['movieId','title','genres']].to_dict(orient='records')[:100])


@app.route('/recommend_user/<int:user_id>')
def recommend_user(user_id):
    recs = recommend_for_user(user_id, n=10)
    return jsonify(recs)


@app.route('/debug_cf/<int:user_id>')
def debug_cf(user_id):
    # Devuelve shapes y primeras predicciones (movieId, title, score) para inspección.
    if cf_user_factors is None or cf_item_factors is None:
        return jsonify({'error':'cf not ready'})
    user_ids, user_map, user_factors = cf_user_factors
    movie_ids, movie_map, item_factors = cf_item_factors

    # coerce keys
    try:
        user_list = [int(x) for x in user_ids]
        movie_list = [int(x) for x in movie_ids]
    except Exception:
        user_list = list(user_ids)
        movie_list = list(movie_ids)

    if user_id not in user_map:
        return jsonify({'error':'user not found','user_id':user_id,'n_users':len(user_list),'n_items':len(movie_list)})

    uidx = user_map[user_id]
    uvec = user_factors[uidx]

    # prepare candidate scores
    scores = []
    for i, mid in enumerate(movie_ids):
        score = float(np.dot(uvec, item_factors[i]))
        scores.append((int(mid), score))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[:20]
    movies_map = movies.set_index('movieId')['title'].to_dict()
    results = [{'movieId':m,'title':movies_map.get(m,''),'score':s} for m,s in scores]
    return jsonify({'user_id':user_id,'n_users':len(user_list),'n_items':len(movie_list),'top':results})


@app.route('/user/<int:user_id>/rated')
def user_rated(user_id):
    # Devuelve las películas valoradas por user_id con movieId, title, genres, rating.
    if ratings is None:
        return jsonify([])
    df = ratings[ratings['userId'] == user_id]
    if df.empty:
        return jsonify([])
    # join with movies to get title and genres
    merged = df.merge(movies[['movieId','title','genres']], on='movieId', how='left')
    # if timestamp column exists, sort by it then by rating
    if 'timestamp' in merged.columns:
        merged = merged.sort_values(['rating','timestamp'], ascending=[False,False])
    else:
        merged = merged.sort_values('rating', ascending=False)
    out = merged[['movieId','title','genres','rating']].to_dict(orient='records')
    return jsonify(out)


@app.route('/user_exists/<int:user_id>')
def user_exists(user_id):
    """Devuelve {exists: true/false} dependiendo si el usuario aparece en ratings.csv"""
    if ratings is None:
        return jsonify({'exists': False})
    exists = user_id in set(ratings['userId'].unique())
    return jsonify({'exists': bool(exists)})


@app.route('/rate', methods=['POST'])
def rate_movie():
    # Recibe JSON {userId, movieId, rating} y actualiza/añade la valoración en ratings.csv, recalcula el CF y devuelve nuevo estado.
    global ratings
    data = request.get_json(force=True)
    if not data:
        return jsonify({'error':'no data provided'}), 400
    try:
        uid = int(data.get('userId'))
        mid = int(data.get('movieId'))
        rscore = float(data.get('rating'))
    except Exception:
        return jsonify({'error':'invalid payload'}), 400

    if ratings is None:
        # create new dataframe
        ratings = pd.DataFrame([{'userId':uid,'movieId':mid,'rating':rscore}])
    else:
        # check if existing rating exists
        mask = (ratings['userId']==uid) & (ratings['movieId']==mid)
        if mask.any():
            ratings.loc[mask, 'rating'] = rscore
            ratings.loc[mask, 'timestamp'] = int(time.time()) if 'timestamp' in ratings.columns else None
        else:
            newrow = {'userId':uid,'movieId':mid,'rating':rscore}
            if 'timestamp' in ratings.columns:
                newrow['timestamp'] = int(time.time())
            ratings = pd.concat([ratings, pd.DataFrame([newrow])], ignore_index=True)

    # persist ratings.csv
    try:
        ratings.to_csv('ml-latest-small/ratings.csv', index=False)
    except Exception as e:
        print(f"[WARN] Could not save ratings.csv: {e}")

    # retrain CF
    train_cf()

    # return updated rated movies and recommendations
    rated = ratings[ratings['userId']==uid]
    merged = rated.merge(movies[['movieId','title','genres']], on='movieId', how='left')
    out_rated = merged[['movieId','title','genres','rating']].to_dict(orient='records')
    recs = recommend_for_user(uid, n=10)
    return jsonify({'rated': out_rated, 'recommendations': recs})

# Iniciar el servidor cuando se ejecute el script
if __name__ == '__main__':
    app.run(port=5000, debug=True)