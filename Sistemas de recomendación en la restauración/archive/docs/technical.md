# Diseño técnico - Sistema de Recomendación (MOD II)

Resumen
------
Esta implementación es una versión educativa de un sistema de recomendación para restaurantes. Emplea tablas de probabilidades condicionales (similares a una red bayesiana simplificada) para estimar P(Cliente gusta | Preferencia, Restricción). Además incorpora un mecanismo de actualización de disponibilidad de ingredientes (razonamiento no monótono) que recalcula la disponibilidad de platos.

Arquitectura
------------
- `recommender/model.py`: Representación del conocimiento (platos, ingredientes) y la clase `Recommender` con:
  - Priors: `prior_preferencia`, `prior_restriccion`.
  - Condicionales: `condicionales[plato][pref][restr]` que contiene P(gusta | pref, restr).
  - `inferir_gustos(preferencia, restriccion)` que devuelve una lista de platos con su probabilidad y disponibilidad.
  - `actualizar_ingrediente(nombre, disponible)` que cambia el estado del ingrediente y afecta la disponibilidad inmediata.

Decisiones de diseño
--------------------
- Se eligió una implementación basada en tablas para mantener claridad y reproducibilidad sin depender de bibliotecas pesadas (p. ej. `pgmpy`).
- Se provee un runner CLI `reco_cli.py` y una interfaz Streamlit `app.py`. El CLI permite ejecutar el modelo incluso si la instalación de Streamlit falla.

Limitaciones
------------
- El modelo usa tablas fijas de probabilidades (valores didácticos). Para producción se deberían estimar estas tablas a partir de datos reales.
- Algunas dependencias (por ejemplo, `pyarrow`) pueden fallar al instalar si la versión de Python no tiene ruedas precompiladas. Recomendamos Python 3.11 para evitar compilaciones desde fuente en Windows.
