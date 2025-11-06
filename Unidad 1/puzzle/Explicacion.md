# Puzzle 8 con Algoritmo A*.

Proyecto Puzzle 8, Una aplicación interactiva desarrollada en Python,
la cual resuelve el clásico rompecabezas deslizante utilizando el algoritmo de búsqueda A*.

## Proposito.
Desarrollado como proyecto educativo para demostrar:

Crear una aplicacion interactica que combine conceptos de inteligencia artificial,
estructuras de datos y diseño de interfaces gráficas para ofrecer una experiencia educativa y funcional.

#### Características

- **Interfaz responsive y moderna.**: Diseño adaptable con colores atractivos y efectos hover.
- **Algoritmo A*.**: Implementación del algoritmo de búsqueda A* con heurística de Manhattan.
- **Animación fluida**: Visualización paso a paso de la solución encontrada.
- **Controles intuitivos**: Botones para resolver automáticamente y reiniciar el puzzle.
- **Experiencia de usuario mejorada**: Feedback visual y mensajes informativos.

#### Cómo usar la aplicacion:

#### Requisitos.

- Python 3.7 o superior.
- Tkinter (incluido por defecto en Python).

#### Ejecutar el juego.

En consola introducir el siguiente codigo: **py main.py** (Sin los *).

#### Controles.

- **Clic en fichas**: Mueve las fichas adyacentes al espacio vacío.
- **Resolver Puzzle**: Ejecuta el algoritmo A* y muestra la animación de la solución.
- **Reiniciar** : Genera un nuevo puzzle aleatorio (garantizado solucionable).

##### Arquitectura del proyecto.

El proyecto sigue el patrón **Modelo-Vista-Controlador (MVC)**.

##### Archivos principales.

- main.py       - Punto de entrada de la aplicación
- view.py       - Interfaz de usuario con Tkinter (Vista)
- controller.py - Lógica de control y coordinación (Controlador)
- model.py      - Algoritmo A* y lógica del puzzle (Modelo)

##### Características técnicas.

- **Responsive design**: Layout que se adapta al tamaño de la ventana.
- **Hover effects**: Efectos visuales al pasar el mouse.
- **Estado reactivo**: Los botones cambian de estado según el contexto.
- **Animación no bloqueante**: Usa *root.after()* para mantener la UI responsiva.
- **Generación solucionable**: El puzzle se genera haciendo movimientos válidos desde el estado resuelto.

##### Algoritmo A*.

El codigo implementado utiliza:

- **Heurística de Manhattan**: Suma de distancias de cada ficha a su posición objetivo.
- **Cola de prioridad**: Para explorar estados más prometedores primero.
- **Detección de estados repetidos**: Evita explorar el mismo estado múltiples veces.
- **Reconstrucción de camino**: Rastrea la secuencia de movimientos hasta la solución.

##### Mejoras visuales.

- **Colores modernos**: Paleta de colores atractiva y consistente.
- **Tipografía clara**: Usa la fuente Segoe UI para mejor legibilidad.
- **Espaciado equilibrado**: Márgenes y paddings cuidadosamente ajustados.
- **Feedback visual**: Estados de carga, hover effects y mensajes informativos.

##### Estructura del código.

puzzle/
├── main.py           # Entrada principal.
├── view.py           # Vista (UI con Tkinter).
├── controller.py     # Controlador (lógica de control).
├── model.py          # Modelo (A* y lógica del puzzle).
├── Explicacion.md    # Este archivo.

##### Créditos.

- Desarrollado por: *Espinoza Felix Fausto Gabriel*
- Fecha de entrega: *12 de septiembre de 2025*