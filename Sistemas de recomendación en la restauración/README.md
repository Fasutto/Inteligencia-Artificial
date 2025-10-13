README.md

Recomendador de Menú — Restaurante
=================================

Este repositorio contiene una pequeña aplicación web (FastAPI + SQLite + frontend estático) que ofrece un sistema de recomendación de platos para clientes de un restaurante.

Contenido de este documento
--------------------------
- Documentación técnica
  - Modelo de razonamiento implementado
  - Representación del conocimiento
- Manual de usuario
- Guía de instalación (local)


Documentación técnica
---------------------

1) Modelo de razonamiento implementado
--------------------------------------

El sistema utiliza un razonador determinista y basado en reglas simples que combina dos ejes principales para puntuar platos:

- Preferencia del cliente (Carnívoro, Vegetariano, Vegano).
- Restricciones alimentarias (por ejemplo, Sin Gluten) y alergias explícitas (lista de ingredientes).

El componente `backend/reasoner.py` calcula una puntuación (score) por cada plato tomando en cuenta:

- Coincidencia con preferencia: platos veganos/vegetarianos obtienen mayor score para clientes con esa preferencia.
- Penalización por restricciones: platos que contienen ingredientes incompatibles con la restricción (p. ej. gluten) reciben una reducción o se marcan como no disponibles.
- Disponibilidad de ingredientes: si un ingrediente está marcado como no disponible en la base de datos (`Ingredient.available = False`), el plato puede ser marcado como no disponible.

El resultado de la inferencia devuelve una lista ordenada de objetos con al menos las siguientes propiedades: `dish` (nombre), `score` (0..1), `available` (bool), `ingredients` (lista de strings).


2) Representación del conocimiento
---------------------------------

La base de conocimiento se representa en SQLite a través de SQLAlchemy (archivo `backend/db.py`). Las entidades relevantes son:

- Dish (platos): nombre, método de preparación (texto), banderas booleanas `is_vegetarian`, `is_vegan`, `is_gluten_free`, y relación many-to-many con ingredientes.
- Ingredient (ingredientes): nombre y `available` (bool).
- Client (clientes): `name`, `preference`, `restriction` y `allergies` como texto libre (coma-separado).
- Beverage (bebidas); no interviene en el razonamiento por ahora pero está modelado.

Las tablas y relaciones están definidas en `backend/db.py`. `init_db()` crea las tablas si no existen. Algunos datos de ejemplo pueden poblarse con `backend/seeder.py` (archivo auxiliar en `archive/` si lo moviste).


Manual de usuario
------------------

Interacción básica:

1. Abrir la aplicación en un navegador: http://127.0.0.1:8000/
2. Seleccionar un cliente existente desde el desplegable en la sección izquierda.
   - Al seleccionar un cliente, la UI autocompleta y bloquea la visualización de Preferencia/Restricción (se muestran en el panel de detalles). También se generan automáticamente las recomendaciones para ese cliente.
3. Para crear un cliente nuevo:
   - Rellena el formulario de la derecha (Nombre, Preferencia, Restricción, Alergias) y pulsa "Guardar Cliente".
   - La UI guardará el cliente en la base de datos y automáticamente seleccionará al nuevo cliente y mostrará las recomendaciones.
4. Resultados:
   - La sección "Resultados" muestra platos ordenados por score. Cada plato indica si está disponible (según ingredientes y alergias) y la lista de ingredientes.

Notas de uso:
- Si un cliente tiene alergias declaradas, los platos que contienen esos ingredientes se marcarán como "No disponible" en la presentación.
- Puedes simular que un ingrediente está agotado cambiando su `available` a False mediante la API (`POST /ingredient`) o usando el seeder/DB directamente.


Guía de instalación (local)
---------------------------

Requisitos previos:
- Python 3.10 o superior instalado.

Pasos mínimos para ejecutar localmente (Windows PowerShell):

1) Crear y activar entorno virtual (si no existe):

```powershell
python -m venv venv
.\n+```

2) Instalar dependencias:
```powershell
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

3) Inicializar la base de datos (las tablas se crean automáticamente con init_db):
```powershell
.\venv\Scripts\python.exe -c "from backend.db import init_db; init_db(); print('DB ok')"
```

4) Arrancar el servidor (ver opciones):
- Ejecutar en primer plano (muestra logs):
```powershell
.\venv\Scripts\python.exe -m uvicorn backend.api:app --host 127.0.0.1 --port 8000
```
- Ejecutar usando el script de conveniencia (PowerShell):
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -Command "& '.\scripts\run.ps1' -Background"
```
- Ejecutar en Windows (cmd) usando `scripts\run.bat` si prefieres no tocar ExecutionPolicy.

5) Abrir en el navegador: http://127.0.0.1:8000/

Problemas comunes y soluciones rápidas:
- Error de puerto ocupado: puede ocurrir si ya hay otra instancia en 127.0.0.1:8000. Mata el proceso que lo usa o cambia el puerto.
- PowerShell bloquea `run.ps1`: usar `-ExecutionPolicy Bypass` o usar `scripts\run.bat` o ejecutar uvicorn directamente.


Archivos esenciales
-------------------
- `backend/api.py` — servidor FastAPI (punto de entrada).
- `backend/db.py` — modelos y `init_db()`.
- `backend/reasoner.py` — lógica de recomendación.
- `backend/static/index.html` y `backend/static/main.js` — frontend.
- `backend/recommender.db` — base de datos SQLite utilizada en runtime (si existe).
- `requirements.txt` — dependencias.

- `scripts/run.ps1` y `scripts/run.bat` — scripts de arranque (moved a `scripts/`).


Contacto / autor
----------------
- Proyecto entregado por: Espinoza Felix Fausto Gabriel

