# Manual de usuario

Uso rápido (CLI)
-----------------
1. Crear entorno virtual e instalar dependencias (desde la raíz del proyecto):

```powershell
python -m venv venv
& ".\venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\venv\Scripts\python.exe" -m pip install -r requirements.txt
```

2. Ejecutar el CLI (ejemplo):

```powershell
& ".\venv\Scripts\python.exe" reco_cli.py --preferencia Vegetariano --restriccion Ninguna
```

Uso (Streamlit)
----------------
Si prefieres una UI gráfica, ejecuta:

```powershell
& ".\venv\Scripts\python.exe" -m streamlit run app.py
```

Simulación de cambios en ingredientes
------------------------------------
- Marca `--sim-pollo-agotado` en el CLI o selecciona la checkbox en la UI para ver el efecto del razonamiento no monótono.

Casos de prueba incluidos
-------------------------
- Los tests en `tests/` cubren escenarios de disponibilidad, preferencias y restricciones.
