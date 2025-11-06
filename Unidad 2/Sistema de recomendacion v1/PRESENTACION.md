# Presentación: Sistema de Recomendación de Películas.

## Diapositiva 1 — Título.

Sistema de Recomendación de Películas

Presentador: Espinoza Felix Fausto Gabriel
Fecha: 12 de octubre de 2025

"Este proyecto implementa un sistema híbrido (contenido + colaborativo) para recomendar películas usando MovieLens (ml-latest-small)."

## Diapositiva 2 — Agenda.

1. Motivación
2. Arquitectura general
3. Técnicas implementadas
4. Ejemplos y demo
5. Retos y cómo se resolvieron
6. Resultados y mejoras futuras

## Diapositiva 3 — Motivación.

- Usuarios se pierden entre miles de películas.
- Recomendadores ayudan a filtrar contenido relevante basándose en gustos o similitud.
- Objetivo: construir un prototipo funcional que muestre recomendaciones personalizadas y por contenido.

## Diapositiva 4 — Arquitectura general.

- Frontend: React + Vite (interfaz para login por userId, búsqueda, ver valoradas, valorar recomendaciones).
- Backend: Flask (API REST) que expone endpoints para búsqueda, content-based y collaborative recommendations.
- Data: MovieLens `ml-latest-small/` (movies.csv, ratings.csv, tags.csv, links.csv).
- Persistencia: CSV para ratings (local) y `models/cf_factors.npz` para factores CF precomputados.

## Diapositiva 5 — Técnicas implementadas.

1. Recomendación por contenido
   - TF‑IDF sobre `genres` + similitud coseno (sklearn TfidfVectorizer + linear_kernel).
2. Recomendación colaborativa (modelo)
   - Construcción R = usuario × película (pivot table)
   - Rellenar valores faltantes con la media del usuario
   - TruncatedSVD (scikit-learn) para obtener factores latentes
   - Predicción: producto punto entre factor usuario y factor item

## Diapositiva 6 — Endpoints clave.

- `GET /recommend/<movie_title>` → recomendaciones por contenido
- `GET /recommend_user/<user_id>` → recomendaciones personalizadas (CF)
- `GET /user/<user_id>/rated` → películas valoradas por el usuario
- `POST /rate` → enviar una valoración `{userId, movieId, rating}` y retrain CF
- `GET /search/autocomplete/<prefix>` → sugerencias de títulos

## Diapositiva 7 — Demo / Flujo de usuario.

1. Abrir frontend (Vite)
2. Ingresar userId (por ejemplo 1) y 'Iniciar sesión'
3. Ver tabla de películas valoradas y lista de recomendaciones
4. Valorar una recomendación (1–5): la valoración se guarda y la tabla se actualiza
5. Buscar una película y obtener recomendaciones por contenido

## Diapositiva 8 — Retos enfrentados.

- Rutas y archivos: problemas iniciales con rutas relativas a `movies.csv`.
- TF‑IDF vacío por datos mal formateados (géneros con separador inesperado) — solucionado limpiando `genres`.
- Paquetes compilados en Windows (por ejemplo *Surprise*) que fallaban en instalación → se cambió a TruncatedSVD (scikit‑learn) que es puro Python/C y más portátil.
- Múltiples intérpretes Python en la máquina (paquetes instalados en otro intérprete) — solución: usar `python -m pip` del intérprete en PATH o crear venv.
- Concurrencia y persistencia: escribir `ratings.csv` directamente puede causar race conditions en producción.

## Diapositiva 9 — Cómo se superaron (soluciones).

- Normalización de datos: `clean_genres()` para evitar 'empty vocabulary' en TF‑IDF.
- Alternativa a librerías problemáticas: usar `TruncatedSVD` para CF.
- Persistencia ligera de modelos: `models/cf_factors.npz` para acelerar reinicios.
- Mejora de UX: Autocomplete con debounce, score de carga y actualizaciones optimistas de la UI.

## Diapositiva 10 — Resultados y métricas (cualitativo).

- Implementación funcional de recomendaciones por contenido y por usuario.
- Interfaz interactiva que permite valorar y ver cómo cambian las recomendaciones.
- Rendimiento: el reentrenamiento en `ml-latest-small` es rápido; en datasets grandes habría que optimizar o usar batch/online updates.

## Diapositiva 11 — Demo técnica: comandos útiles.

- Levantar backend:

python .\app.py

- Levantar frontend:

cd .\frontend
npm install o npm.cmd install
npm run dev o npm.cmd run dev

- Probar recomendación por usuario (PowerShell):

Invoke-RestMethod -Uri "http://127.0.0.1:5000/recommend_user/1"

- Enviar rating de prueba:

$body = @{ userId=1; movieId=1; rating=5 } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:5000/rate" -Body $body -ContentType "application/json"

## Diapositiva 13 — Conclusión.

- Proyecto funcional que demuestra principios claves de sistemas de recomendación: contenido vs colaborativo, procesamiento de datos, persistencia y diseño de API.
- Enfocado en ser portable y fácil de ejecutar localmente.

## Anexos (notas técnicas).

- Estructura de carpetas relevante:
  - `app.py`
  - `ml-latest-small/` (CSV)
  - `frontend/`
  - `models/` (cf_factors.npz)

- Archivos a revisar en el código:
  - `app.py`: `train_cf()`, `recommend_for_user()`, `/rate` endpoint
  - `frontend/src/App.jsx`: `RatingCell` y lógica de actualización de tablas