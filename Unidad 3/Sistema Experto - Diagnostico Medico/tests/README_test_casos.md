# README — tests/test_casos.py
============================

# Archivo
-------
- tests/test_casos.py — Archivo de pruebas activo en la carpeta `tests/`.

# Propósito
---------
Proveer un conjunto de comprobaciones automatizadas (unittest/pytest) para validar comportamientos clave del proyecto sin modificar código existente. Las pruebas pueden verificar la estructura de la base de conocimiento, funciones del motor de inferencia y la correcta combinación de factores de certeza según cómo esté implementado el test.

# Requisitos
---------
- Python 3.x
- Ejecutar desde la raíz del proyecto:
  c:\Users\Hirai Momo\Documents\01 - Inteligencia Artificial\Unidad 3\Sistema Experto - Diagnostico Medico

# Comandos de ejecución (Windows)
-------------------------------
1) Usando pytest (si está instalado):
   py -3 -m pytest tests/test_casos.py -q

   o

   py -3 -m pytest -q -s tests/test_casos.py 

# Qué esperar
-----------
- Salida en consola con detalles de pruebas pasadas/fallidas.
- Las pruebas están diseñadas para ser no intrusivas: no modifican archivos del proyecto.
- Algunos tests pueden comprobar existencia de símbolos (p. ej. funciones en motor_inferencia.py) y comportamientos mínimos (evaluación de condiciones, combinación de FC, tipo de retorno de motor_de_inferencia).

# Interpretación de fallos comunes
-------------------------------
- ImportError / ModuleNotFoundError:
  - Ejecutar desde la raíz del proyecto o añadir la raíz al PYTHONPATH.
- AssertionError en estructura de BASE_DE_CONOCIMIENTO:
  - Revisar formato en base_conocimiento.py (clave "reglas" como lista, reglas con al menos atributo y valor, pesos entre 0.0 y 1.0 si aplican).
- TypeError por firma de función:
  - El test puede esperar firmas mínimas (por ejemplo: evaluar_condicion(datos, atributo, valor_esperado) o motor_de_inferencia(datos)). Ajustar la implementación o el test según el diseño deseado.
- Fallos en comparativos o parsing numérico:
  - Verificar que los valores de entrada en `datos_paciente` sean del tipo esperado o convertibles a número cuando el test emplea comparativos como ">65" o "<92".

# Autor
-----
Espinoza Felix Fausto Gabriel.



