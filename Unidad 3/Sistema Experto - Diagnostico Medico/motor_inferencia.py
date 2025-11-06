#  Motor de inferencia del Sistema Experto:
#   - Implementa encadenamiento hacia adelante (forward chaining) para generar diagnósticos candidatos a partir de la BASE_DE_CONOCIMIENTO.
#   - Implementa encadenamiento hacia atrás (backward chaining) para validar una hipótesis concreta y retornar la certeza resultante y las reglas apoyadas.

# Importa la base de conocimiento definida en base_conocimiento.py
from base_conocimiento import BASE_DE_CONOCIMIENTO


# MANEJO DE CERTEZA Y LÓGICA DE REGLAS
#---------------------------------------

# Combina dos Factores de Certeza (FC) usando una fórmula simplificada inspirada en MYCIN.
def combinar_factores_certeza(fc1, fc2):

    # FC_combinado = FC1 + FC2 * (1 - FC1)
    # fc1, fc2: floats entre 0.0 y 1.0
    # Retorna float en [0.0, 1.0]
    # Casos limpios: si alguno es 1.0, el combinado es 1.0.

    if fc1 == 1.0 or fc2 == 1.0:
        return 1.0
    return fc1 + fc2 * (1 - fc1)

# Evalúa si el valor reportado por el paciente satisface la condición de la regla.
def evaluar_condicion(clave_dato, valor_paciente, valor_esperado):
    
    # - valor_esperado puede ser:
    #  * bool: comparación directa True/False
    #  * string comparativo: comienza con '>' o '<' seguido de número (ej. "<92")
    #  * string literal: comparación textual (ej. "seca", "productiva")
    
    # Caso booleano.
    if isinstance(valor_esperado, bool):
        return valor_paciente == valor_esperado
    
    # Caso string (comparativo o literal).
    elif isinstance(valor_esperado, str):
        # Comparación numérica expresada como string (ej. ">65", "<92")
        if valor_esperado[0] in ('>', '<'):
            try:
                operador = valor_esperado[0]
                umbral = float(valor_esperado[1:])
                # Intentamos convertir el valor actual a float; si falla, la condición no se cumple.
                valor_actual = float(valor_paciente)
                
                # Evaluación de la condición.
                if operador == '>' and valor_actual > umbral:
                    return True
                elif operador == '<' and valor_actual < umbral:
                    return True
                return False
            except (ValueError, TypeError):
                # Si no se puede convertir (p. ej. el paciente dio "no aplica"), no activar regla.
                return False 
        
        # Comparación textual (insensible a mayúsculas/minúsculas)
        else:
            return str(valor_paciente).lower() == valor_esperado.lower()
    
    # Otros tipos no contemplados: no cumple la condición
    return False


# MECANISMOS DE INFERENCIA
#--------------------------

# Encadenamiento hacia adelante: genera diagnósticos candidatos basados en los datos del paciente.
def motor_de_inferencia(datos_paciente):

    # Diccionarios para resultados finales de diagnósticos y explicaciones.
    diagnosticos = {}
    explicaciones = {}

    # Recorre cada enfermedad en la base de conocimiento.
    for enfermedad, info in BASE_DE_CONOCIMIENTO.items():
        # Inicializa el Factor de Certeza acumulado y lista de reglas activadas.
        fc_acumulado = 0.0
        reglas_activadas = []
        
        # Recorre las reglas asociadas a la enfermedad.
        for regla in info["reglas"]:
            # Desempaqueta la regla.
            clave_dato, valor_esperado, fc_individual = regla
            
            # Verifica si el dato del paciente está disponible.
            if clave_dato in datos_paciente:
                valor_paciente = datos_paciente[clave_dato]
                
                # Evalúa si la condición de la regla se cumple.
                if evaluar_condicion(clave_dato, valor_paciente, valor_esperado):
                    # Regla activada: actualiza explicaciones y FC acumulado.
                    reglas_activadas.append(f"{clave_dato.capitalize()} = {valor_paciente}")
                    # Actualiza el FC acumulado combinando con el FC individual de la regla.
                    fc_acumulado = combinar_factores_certeza(fc_acumulado, fc_individual)
        
        # Si el FC acumulado es significativo, registra el diagnóstico y explicación.
        if fc_acumulado > 0.1: # Solo si la certeza es significativa
            # Guarda el diagnóstico con su certeza en porcentaje.
            diagnosticos[enfermedad] = round(fc_acumulado * 100)
            # Guarda las reglas activadas como explicación.
            explicaciones[enfermedad] = reglas_activadas
            
    # Retorna los diagnósticos y explicaciones generadas.
    return diagnosticos, explicaciones

# Encadenamiento hacia atrás: valida una hipótesis concreta (enfermedad) basada en los datos del paciente.
def encadenamiento_hacia_atras(hipotesis, datos_paciente):
    
    print(f"\n--- Validando hipótesis: **{hipotesis}** ---")
    
    # Verifica si la hipótesis está en la base de conocimiento.
    if hipotesis not in BASE_DE_CONOCIMIENTO:
        print("La hipótesis no está en la base de conocimiento.")
        return 0, []
    
    # Inicializa FC acumulado y lista de reglas apoyadas.
    info_enfermedad = BASE_DE_CONOCIMIENTO[hipotesis]
    fc_acumulado = 0.0
    reglas_apoyadas = []
    
    # Recorre las reglas asociadas a la hipótesis.
    for regla in info_enfermedad["reglas"]:
        # Desempaqueta la regla.
        clave_dato, valor_esperado, fc_individual = regla
        
        # Verifica si el dato del paciente está disponible.
        if clave_dato in datos_paciente:
            # Obtiene el valor reportado por el paciente.
            valor_paciente = datos_paciente[clave_dato]
            
            # Evalúa si la condición de la regla se cumple.
            if evaluar_condicion(clave_dato, valor_paciente, valor_esperado):
                # Regla apoyada: actualiza lista y FC acumulado.
                reglas_apoyadas.append(f"Regla '{clave_dato}' apoyada: {valor_paciente}")
                fc_acumulado = combinar_factores_certeza(fc_acumulado, fc_individual)
        else:
            print(f"  - Dato clave '{clave_dato}' no disponible. (No contribuye a la certeza)")
            
    # Muestra resultados de la validación y retorna certeza y reglas apoyadas.
    certeza_final = round(fc_acumulado * 100)
    print(f"  > Certeza de validación para **{hipotesis}**: **{certeza_final}%**")
    print(f"  > Reglas específicas cumplidas: {len(reglas_apoyadas)}")
    
    # Retorna la certeza final y las reglas apoyadas.
    return certeza_final, reglas_apoyadas