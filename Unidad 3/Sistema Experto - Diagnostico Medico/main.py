# Archivo principal que integra la interfaz gráfica con el motor de inferencia.
# Contiene la función de conexión (ejecutar_logica_se) que la GUI invoca para procesar los datos del paciente y devolver el texto final de resultados.

# Importa módulos estándar
import sys

# Asegura que las importaciones locales funcionen.
# Esto es útil cuando se ejecuta el script desde diferentes ubicaciones en Windows.
sys.path.append('.')


#-----------------------------------------------------------------------------------------------
#   Importa funciones desde módulos locales:
#   - iniciar_interfaz: Función que lanza la GUI y acepta un callback para ejecutar la lógica.
#   - resultados_Analisis: Función/utilidad que formatea el texto final mostrado en la GUI.
#   - motor_de_inferencia: Función que aplica encadenamiento hacia adelante (forward chaining).
#   - encadenamiento_hacia_atras: Función que valida la hipótesis con backward chaining.
#-----------------------------------------------------------------------------------------------
from interfaz import iniciar_interfaz, resultados_Analisis
from motor_inferencia import motor_de_inferencia, encadenamiento_hacia_atras


# Función que encapsula la lógica del motor de inferencia para ser llamada por la GUI.
def ejecutar_logica_se(datos_paciente):

    # 1. Encadenamiento Hacia Adelante (Forward Chaining):
    #    motor_de_inferencia debe devolver: {'EnfermedadA': 0.75, 'EnfermedadB': 0.42, ...} y {'EnfermedadA': ['regla1', 'regla3'], ...}
    diagnosticos_raw, explicaciones_raw = motor_de_inferencia(datos_paciente)
    
    # Si el motor no encuentra hipótesis con certeza significativa, informar a la GUI.
    if not diagnosticos_raw:
        return "--- RESULTADO FINAL ---\nEl sistema no pudo encontrar un diagnóstico con certeza significativa (>10%)."

    # Estructurar los resultados para identificar el principal.
    # Se combinan la certeza y las explicaciones en una sola estructura por enfermedad.
    diagnostico = {}
    for enf, cer in diagnosticos_raw.items():
        diagnostico[enf] = {'certeza': cer, 'explicaciones': explicaciones_raw[enf]}
        
    # Ordenar diagnósticos para identificar el principal
    diagnosticos_ordenados_list = sorted(diagnostico.items(), key=lambda item: item[1]['certeza'], reverse=True)
    
    # Tomar solo la hipótesis principal
    diagnostico_principal = diagnosticos_ordenados_list[0][0]
    info_principal = diagnosticos_ordenados_list[0][1]
    
    
    # 2. Encadenamiento Hacia Atrás (Backward Chaining) - Validación
    # encadenamiento_hacia_atras devuelve: certeza_validacion y reglas_validacion
    certeza_validacion, reglas_validacion = encadenamiento_hacia_atras(
        diagnostico_principal, 
        datos_paciente
    )
    
    
    # 3. Retorna los resultados para la GUI
    # resultado_Analisis debe recibir la hipótesis principal, su info del encadenamiento hacia adelante y los resultados del encadenamiento hacia atrás para componer el texto final informativo.
    resultado_final_texto = resultados_Analisis(
        diagnostico_principal, 
        info_principal,
        certeza_validacion, 
        reglas_validacion
    )
    
    return resultado_final_texto


# Inicia la aplicación GUI y le pasa ejecutar_logica_se como callback para procesar datos.
if __name__ == "__main__":
    # Inicia la aplicación GUI
    iniciar_interfaz(ejecutar_logica_se)