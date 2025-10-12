# Sistema de Recomendación de Películas (v1)

Resumen
-------
Este proyecto es un sistema de recomendación de películas con dos enfoques:

- Recomendación por contenido (content-based): utiliza TF‑IDF sobre la columna `genres` de MovieLens y similitud coseno para devolver películas similares a una película dada.
- Recomendación colaborativa (user-based / model-based): construye una matriz usuario×película a partir de `ratings.csv`, rellena los huecos con la media del usuario, aplica TruncatedSVD para obtener factores de usuario y de ítem, y predice afinidades por producto punto entre vectores.

El backend está desarrollado en Python (Flask) y el frontend es una aplicación React (Vite).

Qué se hizo
-----------
- Preprocesamiento de `movies.csv` (normalización de `genres`).
- Implementación de un vectorizador TF‑IDF sobre `genres` y cálculo de similitud coseno para recomendaciones por contenido.
- Implementación de un pipeline colaborativo simple con TruncatedSVD (scikit-learn) sobre la matriz usuario×película.
- Endpoints REST para búsqueda (autocomplete, fuzzy), recomendaciones por título y por usuario, consulta de valoraciones de usuario y envío de valoraciones.
- Frontend (React + Vite) con:
  - Autocomplete de búsqueda con debounce y navegación por teclado.
  - Login por `userId` (verifica que el usuario exista en `ratings.csv`).
  - Tabla de películas valoradas (scrollable para mostrar ~10 filas) y tabla de recomendaciones.
  - Control para valorar recomendaciones (1–5) que envía POST a `/rate` y actualiza la UI.
- Persistencia de factores CF en `models/cf_factors.npz` para acelerar arranques.

Tecnologías y librerías usadas
-----------------------------
- Python 3.10+
  - Flask
  - flask-cors
  - pandas
  - numpy
  - scikit-learn
  - rapidfuzz
- Frontend
  - Node.js + npm
  - React
  - Vite
  - axios
- Dataset
  - MovieLens (carpeta `ml-latest-small/` con `movies.csv`, `ratings.csv`, etc.)

Archivos clave
--------------
- `app.py` : servidor Flask con todos los endpoints del backend.
- `ml-latest-small/` : carpeta con los CSV (obligatorio: `movies.csv`, `ratings.csv`).
- `models/cf_factors.npz` : archivo opcional que guarda factores de CF (si existe, el backend lo carga; si no, se crea al entrenar).
- `frontend/` : carpeta con el cliente React (contiene `package.json`, `index.html`, `src/App.jsx`, `src/App.css`).
- `scripts/test_rate.py` : script opcional para probar flujo GET/POST de rating.

Requisitos
----------
- Python 3.10 o superior
- Node.js y npm

Dependencias Python (sugerido en virtualenv)

flask
flask-cors
pandas
numpy
scikit-learn
rapidfuzz


Instalación y ejecución
-----------------------
1) Preparar entorno Python (opcional pero recomendado):

powershell
# desde la raíz del proyecto
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt   # si creas este archivo
# o instala manualmente:
python -m pip install flask flask-cors pandas numpy scikit-learn rapidfuzz


2) Levantar backend (desde la raíz del repo, donde está `app.py`):

powershell
python .\app.py

El servidor correrá por defecto en `http://127.0.0.1:5000`. Revisa la consola para mensajes relacionados con `models/cf_factors.npz`.

3) Levantar frontend (en otro terminal):

powershell
cd .\frontend
npm install
npm run dev o npm.cmd run dev

Vite indicará la URL (ej. `http://localhost:5173`).

Cómo utilizar el software
-------------------------
Esta sección muestra el flujo típico de uso, tanto para el usuario final (frontend)
como para desarrolladores/QA que quieran probar endpoints directamente.

1) Usar la interfaz (flow usuario)
  - Abre la URL que te indique Vite (ej. http://localhost:5173).
  - En el campo "Ingresa tu userId" escribe un id existente (por ejemplo `1`) y pulsa "Iniciar sesión".
  - Verás la tabla de "Películas valoradas" por ese usuario y, debajo, la tabla de recomendaciones.
  - Para valorar una recomendación: selecciona la puntuación (1–5) y pulsa "Valorar". La tabla de valoradas se actualizará y la recomendación desaparece.
  - Para obtener recomendaciones por contenido: escribe el nombre de una película en el buscador, selecciona una sugerencia y pulsa "Obtener Recomendaciones".

2) Pruebas directas a la API (PowerShell)
  - Obtener recomendaciones personalizadas para user 1:
    ```powershell
    Invoke-RestMethod -Uri "http://127.0.0.1:5000/recommend_user/1"
    ```
  - Ver películas valoradas por user 1:
    ```powershell
    Invoke-RestMethod -Uri "http://127.0.0.1:5000/user/1/rated"
    ```
  - Enviar una valoración (ejemplo: user 1 da 5 a movieId 1):
    ```powershell
    $body = @{ userId=1; movieId=1; rating=5 } | ConvertTo-Json
    Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:5000/rate" -Body $body -ContentType "application/json"
    ```
  - Buscar sugerencias para un prefijo (autocomplete):
    ```powershell
    Invoke-RestMethod -Uri "http://127.0.0.1:5000/search/autocomplete/Toy"
    ```

3) Notas de QA / depuración
  - Si quieres ver shapes y predicciones internas del CF usa:
    ```powershell
    Invoke-RestMethod -Uri "http://127.0.0.1:5000/debug_cf/1"
    ```
  - Si el backend devuelve listas vacías para recomendaciones, revisa la consola de Flask: puede estar indicando que `movies.csv` no se encontró o que `ratings.csv` está vacío.


Cómo funciona (contrato de endpoints)
------------------------------------
- GET /recommend/<movie_title>
  - Entrada: título exacto (codificado en URL).
  - Salida: lista JSON de títulos similares (top-10).

- GET /search/autocomplete/<prefix>
  - Entrada: prefijo de búsqueda
  - Salida: array de títulos coincidentes (hasta 10)

- GET /recommend_user/<user_id>
  - Entrada: userId (int)
  - Salida: lista JSON de objetos `{ movieId, title, genres, score }` (top-10 por defecto)

- GET /user/<user_id>/rated
  - Entrada: userId
  - Salida: lista de películas valoradas por ese usuario `{ movieId, title, genres, rating }`

- GET /user_exists/<user_id>
  - Entrada: userId
  - Salida: `{ exists: true/false }` indicando si aparece en `ratings.csv`

- POST /rate
  - Entrada JSON: `{ userId, movieId, rating }`
  - Acción: añade/actualiza fila en `ratings.csv`, reentrena CF, guarda `models/cf_factors.npz` y devuelve `{ rated: [...], recommendations: [...] }` del usuario.

Notas y consideraciones
-----------------------
- Si `ratings.csv` no existe o está vacío, CF no estará disponible y se servirá una lista `popular_movies` basada en conteos de rating.
- `POST /rate` reentrena inmediatamente el CF; esto puede tardar según el tamaño del dataset y la máquina.
- El almacenamiento actual de ratings es un CSV: para producción o concurrencia fuerte deberías usar una base de datos.
- `models/cf_factors.npz` acelera reinicios pero debe regenerarse si cambias la forma de la matriz (por ejemplo si filtras movieIds).

Ideas de mejora
---------------
- Añadir endpoint `/retrain_cf` para reentrenar manualmente o por cron.
- Exponer parámetro `?n=` en `/recommend_user` para controlar cuántas recomendaciones devolver.
- Mapear el `score` del CF a una escala 1–5 (regresión) para mayor interpretabilidad.
- Reemplazar CSV por una base de datos para manejo concurrente y escalado.

Contacto / autor
----------------
- Proyecto entregado por: Espinoza Felix Fausto Gabriel

