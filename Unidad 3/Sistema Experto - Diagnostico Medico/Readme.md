# Sistema Experto: Diagnóstico Respiratorio

Descripción breve
-----------------
Proyecto que implementa un sistema experto simple para el diagnóstico diferencial de enfermedades respiratorias. Incluye una interfaz gráfica (Tkinter), una base de conocimiento con reglas, un motor de inferencia (encadenamiento hacia adelante) y un módulo de validación (encadenamiento hacia atrás).

Propósito
---------
Permitir introducir datos clínicos básicos de un paciente y obtener:
- Hipótesis de diagnóstico con un factor de certeza (FC) calculado por el motor de inferencia.
- Explicaciones de qué reglas activaron la hipótesis.
- Validación posterior de la hipótesis (backward chaining).
- Recomendaciones de pruebas y manejo inicial extraídas de la base de conocimiento.

Estructura del proyecto
-----------------------
- [base_conocimiento.py](base_conocimiento.py) — Contiene la base de conocimiento y las reglas.
- [motor_inferencia.py](motor_inferencia.py) — Motor que realiza forward y backward chaining.
- [interfaz.py](interfaz.py) — GUI en Tkinter y formateador de resultados.
- [main.py](main.py) — Punto de entrada; conecta la GUI con la lógica.
- [tests/](tests/) — Carpeta con pruebas automatizadas; actualmente contiene: test_casos.py — Archivo de pruebas existente que se utiliza para validar aspectos del proyecto.

Archivos y símbolos principales
-------------------------------
- Base de conocimiento:
  - [`base_conocimiento.BASE_DE_CONOCIMIENTO`](base_conocimiento.py) — Diccionario con enfermedades, sus reglas, pruebas y tratamientos.
  - Archivo: [base_conocimiento.py](base_conocimiento.py)

- Motor de inferencia:
  - [`motor_inferencia.motor_de_inferencia`](motor_inferencia.py) — Realiza encadenamiento hacia adelante y devuelve diagnósticos y explicaciones.
  - [`motor_inferencia.encadenamiento_hacia_atras`](motor_inferencia.py) — Valida una hipótesis concreta y devuelve la certeza y reglas apoyadas.
  - [`motor_inferencia.combinar_factores_certeza`](motor_inferencia.py) — Función que combina factores de certeza (FC).
  - [`motor_inferencia.evaluar_condicion`](motor_inferencia.py) — Evalúa si el dato del paciente cumple la condición de la regla.
  - Archivo: [motor_inferencia.py](motor_inferencia.py)

- Interfaz y salida:
  - [`interfaz.SistemaExpertoGUI`](interfaz.py) — Clase que construye la GUI, recoge datos y muestra resultados.
  - [`interfaz.iniciar_interfaz`](interfaz.py) — Función para iniciar la aplicación.
  - [`interfaz.resultados_Analisis`](interfaz.py) — Genera el texto final mostrado en la GUI.
  - Archivo: [interfaz.py](interfaz.py)

- Integración:
  - [`main.ejecutar_logica_se`](main.py) — Función que orquesta forward + backward chaining y usa el formateador para retornar texto a la GUI.
  - Archivo: [main.py](main.py)

Reglas y formato de la Base de Conocimiento
-------------------------------------------
Cada entrada en [`base_conocimiento.BASE_DE_CONOCIMIENTO`](base_conocimiento.py) tiene la forma:

- "Nombre de la enfermedad": {
    - "reglas": [ (atributo, valor_esperado, peso), ... ],
    - "pruebas_adicionales": "Texto...",
    - "tratamiento_inicial": "Texto...",
    - "prevencion": "Texto..." (opcional)
  }

Detalles:
- Atributo: clave que debe aparecer en el dict `datos_paciente` (p. ej. "fiebre", "edad", "tipo_tos").
- Valor esperado:
  - Booleano: True / False.
  - Texto literal: p. ej. "seca", "productiva" (comparación case-insensitive).
  - Comparativo como string: comienza con '>' o '<' seguido de número (ej. ">65", "<92"). El motor intentará convertir el dato del paciente a número y comparar.
- Peso (fc_individual): float entre 0.0 y 1.0 que representa la importancia/certeza de la regla.

Lógica de inferencia y combinación de certeza
---------------------------------------------
- El motor recorre las reglas de cada enfermedad y activa aquellas que se verifican en `datos_paciente` (ver [`motor_inferencia.evaluar_condicion`](motor_inferencia.py)).
- El factor de certeza acumulado se combina regla por regla mediante la función [`motor_inferencia.combinar_factores_certeza`](motor_inferencia.py).
- La fórmula usada es:
    $$ FC_{combinado} = FC_1 + FC_2 \cdot (1 - FC_1) $$ (Los $ son solo para el estilo, No se implementan en la formula)

- Los diagnósticos con certeza acumulada > 10% (0.1) se devuelven en porcentaje entero (p. ej. 75).

Flujo de ejecución
------------------
1. Ejecutar la aplicación:
   - Requisito: Python 3.x con Tkinter disponible.
   - Desde la raíz del proyecto:
        python main.py o py -3 main.py
   - Archivo de lanzamiento: [main.py](main.py)

2. Interacción:
   - La GUI construida por [`interfaz.SistemaExpertoGUI`](interfaz.py) recopila datos y llama a [`main.ejecutar_logica_se`](main.py).
   - [`main.ejecutar_logica_se`](main.py) llama a [`motor_inferencia.motor_de_inferencia`](motor_inferencia.py) para obtener diagnósticos y explicaciones.
   - Se valida la hipótesis principal con [`motor_inferencia.encadenamiento_hacia_atras`](motor_inferencia.py).
   - La salida formateada la produce [`interfaz.resultados_Analisis`](interfaz.py) y se muestra en la GUI.

Datos de entrada esperados (claves)
-----------------------------------
Algunas claves usadas por las reglas en la base de conocimiento (estas se crean/recogen en la GUI implementada en [`interfaz.SistemaExpertoGUI`](interfaz.py)):
- `edad`, `sexo`
- `tos_presente`, `tipo_tos`, `duracion_tos`
- `disnea`, `sibilancia`, `dolor_pecho`, `fiebre`, `fatiga`
- `crepitaciones`, `sat_oxigeno`, `pcr_elevada`
- `tabaquismo`, `contaminantes`, `antecedentes_alergicos`

Salida esperada
---------------
- Texto formateado con:
  - Hipótesis principal y FC (forward).
  - Reglas activadas (explicación).
  - Resultado de validación (backward) y reglas que apoyaron la validación.
  - Pruebas sugeridas y manejo inicial extraído de la base de conocimiento.

Consejos y resolución de problemas
----------------------------------
- Ejecutar `main.py` desde la carpeta raíz del proyecto para que las importaciones relativas funcionen correctamente.
- Si falta Tkinter en la instalación de Python, instalarlo o usar una distribución que lo incluya.
- Para depuración rápida, ejecutar [`motor_inferencia.motor_de_inferencia`](motor_inferencia.py) en un REPL/Django de pruebas con un dict de ejemplo para ver activación de reglas.

Tests disponibles y ejecución
----------------------------
- Archivo de pruebas utilizado: tests/test_casos.py (único archivo de tests en la carpeta `tests/`).
- Propósito: ejecutar las comprobaciones ya implementadas en `test_casos.py` para validar partes del motor y/o la base de conocimiento según cómo esté escrito el test.

Cómo ejecutar (Windows, desde la raíz del proyecto):
1) Usando pytest (si está instalado):
   py -3 -m pytest tests/test_casos.py -q

   o

   py -3 -m pytest -q -s tests/test_casos.py 

Notas:
- Ejecutar desde la raíz del proyecto para evitar errores de importación.
- Si el test falla por firmas distintas de funciones, revisar `test_casos.py` y las implementaciones en `motor_inferencia.py` / `base_conocimiento.py` para alinear firmas o adaptar el test según el diseño esperado.

Referencias en el código (en el proyecto)
-----------------------------------------
- [base_conocimiento.py](base_conocimiento.py) — [`base_conocimiento.BASE_DE_CONOCIMIENTO`](base_conocimiento.py)
- [motor_inferencia.py](motor_inferencia.py) — [`motor_inferencia.motor_de_inferencia`](motor_inferencia.py), [`motor_inferencia.encadenamiento_hacia_atras`](motor_inferencia.py), [`motor_inferencia.combinar_factores_certeza`](motor_inferencia.py), [`motor_inferencia.evaluar_condicion`](motor_inferencia.py)
- [interfaz.py](interfaz.py) — [`interfaz.SistemaExpertoGUI`](interfaz.py), [`interfaz.iniciar_interfaz`](interfaz.py), [`interfaz.resultados_Analisis`](interfaz.py)
- [main.py](main.py) — [`main.ejecutar_logica_se`](main.py)
- [tests/test_casos.py](tests/test_casos.py) — Archivo de pruebas activo; ejecutar según la sección "Tests disponibles y ejecución".

Desarrollador:
--------------
Espinoza Felix Fausto Gabriel
