TESTS.md

Pruebas funcionales — Recomendador de Menú
=========================================

Este documento describe casos de prueba funcionales y simulaciones para verificar el correcto funcionamiento del sistema: endpoints, creación de clientes, bloqueo/autocompletado de la UI y comportamiento del razonador ante restricciones/alergias/ingredientes agotados.

Cómo ejecutar las pruebas rápidas
--------------------------------

1) Asegúrate de que el servidor está en ejecución (por ejemplo usando el comando uvicorn en la carpeta raíz):

```powershell
.\venv\Scripts\python.exe -m uvicorn backend.api:app --host 127.0.0.1 --port 8000
```

2) Usaremos `curl` o `Invoke-WebRequest` (PowerShell) para simular las interacciones. Los pasos siguientes asumen que el servidor corre en http://127.0.0.1:8000.


Casos de prueba funcionales
---------------------------

Caso 1 — Listado de clientes (GET /clients)
------------------------------------------
Objetivo: Comprobar que la API devuelve la lista de clientes.
Pasos:
1. GET http://127.0.0.1:8000/clients
Resultado esperado: Código 200 y un array JSON con objetos que contengan `id`, `name`, `preference`, `restriction`, `allergies`.

Ejemplo (PowerShell):
```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/clients'
```


Caso 2 — Crear cliente y ver autofill en la UI (POST /clients + UI)
----------------------------------------------------------------
Objetivo: Verificar que crear un cliente a través de la API se refleja en la UI y que la creación devuelve el objeto creado.
Pasos:
1. POST /clients con body JSON: { "name": "PruebaUI", "preference": "Vegetariano", "restriction": "Ninguna", "allergies": "" }.
2. Esperar respuesta 200 y que devuelva `id`.
3. En la UI, recargar o usar el desplegable — el nuevo cliente debe aparecer; al seleccionarlo la UI debe autocompletar los detalles.

Ejemplo (PowerShell):
```powershell
# Construye el JSON y publica
$json = '{"name":"PruebaUI","preference":"Vegetariano","restriction":"Ninguna","allergies":""}'
Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8000/clients' -Body $json -ContentType 'application/json'
```


Caso 3 — Recomendaciones para cliente sin alergias (POST /recommend/client/{id})
-------------------------------------------------------------------------------
Objetivo: Verificar que el endpoint de recomendaciones devuelve una lista ordenada por score y marca `available` según ingredientes.
Pasos:
1. Seleccionar un cliente existente (por ejemplo id=1)
2. POST http://127.0.0.1:8000/recommend/client/1
Resultado esperado: Código 200 y una lista de platos con fields `dish`, `score`, `available`, `ingredients`.


Caso 4 — Alergias bloqueando platos
-----------------------------------
Objetivo: Verificar que si un cliente declara alergias, los platos que contienen esos ingredientes se marcan como no disponibles.
Pasos:
1. Crear un cliente con `allergies`='Queso' (o editar cliente existente con alergias).
2. POST /recommend/client/{new_id}
Resultado esperado: Los platos que contienen 'Queso' deben tener `available: false`.


Caso 5 — Ingrediente agotado (simulación)
-----------------------------------------
Objetivo: Probar que cuando un ingrediente cambia su `available` a False, los platos que lo contienen se ven afectados.
Pasos:
1. Cambia el ingrediente (por ejemplo 'Pollo') a `available=false` mediante `POST /ingredient` con payload { "name": "Pollo", "available": false }.
2. Ejecuta `POST /recommend/client/{id}` para un cliente carnívoro.
Resultado esperado: Platos que requieren 'Pollo' tendrán `available:false`.


Simulación automatizada (script rápido)
--------------------------------------

Ejemplo rápido (PowerShell):
```powershell
# Crear cliente de prueba
$json = '{"name":"AutoTest","preference":"Carnívoro","restriction":"Ninguna","allergies":""}'
$res = Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8000/clients' -Body $json -ContentType 'application/json'
$id = $res.id
# Pedir recomendaciones para el cliente creado
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/recommend/client/$id"
```


Notas finales
-------------
- Estas pruebas son funcionales y esperan que los endpoints implementados estén activos. Para pruebas más formales integradas en CI, recomendamos convertirlos a pytest e incluir fixtures que inicialicen y limpien la base de datos antes/después de cada test (hay tests en `archive/tests/` si deseas reutilizarlos).