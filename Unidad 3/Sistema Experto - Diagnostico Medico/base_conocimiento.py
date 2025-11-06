# Base de Conocimiento (BC) del Sistema Experto - Diagnóstico Médico de Enfermedades Respiratorias.
#
# Este módulo define BASE_DE_CONOCIMIENTO, un diccionario que contiene reglas, recomendaciones de pruebas adicionales y tratamientos iniciales para cada enfermedad contemplada por el sistema.

#-----------------------------------------------------------------------
# Estructura general:
#-----------------------------------------------------------------------
#   "Nombre de la enfermedad": {
#       "reglas": [ (atributo, valor_esperado, peso), ... ],
#       "pruebas_adicionales": "Texto con pruebas sugeridas",
#       "tratamiento_inicial": "Texto con manejo inicial",
#       "prevencion": "Texto con medidas preventivas"
#   }
#-----------------------------------------------------------------------

# - Cada regla es una tupla (Atributo, Valor_esperado, Peso):
#   - Atributo: clave que se espera en `datos_paciente` (por ejemplo "fiebre", "edad", "tipo_tos").
#   - Valor esperado: puede ser booleano (True/False), un string ("seca", "productiva") o una condición con operador como "<92", ">65", ">90", "<7".
#     El motor de inferencia debe interpretar comparadores en strings (por ejemplo "<92" significa valor numérico < 92).
#   - Peso: representa la importancia/certeza de esa regla (0.0 - 1.0) en el cálculo de la certeza final.

BASE_DE_CONOCIMIENTO = {
    # Neumonía Bacteriana
    # Reglas enfocadas en hallazgos típicos (fiebre alta, tos productiva, crepitaciones, hipoxemia, edad avanzada). Factor de certeza alto en crepitaciones y fiebre.
    "Neumonía Bacteriana": {
        "reglas": [
            ("fiebre", True, 0.8),
            ("tipo_tos", "productiva", 0.7),
            ("dolor_pecho", True, 0.6),
            ("crepitaciones", True, 0.9),
            ("sat_oxigeno", "<92", 0.8),   
            ("edad", ">65", 0.5)           
        ],
        "pruebas_adicionales": "Solicitar radiografía de tórax (Rx), hemocultivo y recuento sanguíneo completo (CBC).",
        "tratamiento_inicial": "Iniciar antibióticos empíricos de amplio espectro inmediatamente."
    },

    # COVID-19
    # Reglas que combinan síntomas respiratorios con pruebas específicas (p. ej. PCR).
    "COVID-19": {
        "reglas": [
            ("fiebre", True, 0.7),
            ("tipo_tos", "seca", 0.6),
            ("fatiga", True, 0.8),
            ("disnea", True, 0.7),
            ("pcr_elevada", True, 0.7),
            ("duracion_tos", ">7", 0.5)
        ],
        "pruebas_adicionales": "Realizar prueba de antígenos o PCR. Monitoreo continuo de saturación.",
        "tratamiento_inicial": "Aislamiento estricto y manejo sintomático. Consultar manejo con antivirales si aplica."
    },

    # Asma
    # Enfocado en sibilancias, historia alérgica y respuesta a broncodilatadores.
    "Asma": {
        "reglas": [
            ("sibilancia", True, 0.9),
            ("disnea", True, 0.7),
            ("tos_presente", True, 0.5),
            ("antecedentes_alergicos", True, 0.8),
            ("contaminantes", True, 0.6)
        ],
        "pruebas_adicionales": "Solicitar Espirometría con prueba broncodilatadora.",
        "tratamiento_inicial": "Administrar broncodilatadores de acción corta (inhaladores) para aliviar síntomas."
    },

    # Bronquitis Aguda
    # Caracterizada por tos productiva de corta duración; fiebre no es obligatoria.
    "Bronquitis Aguda": {
        "reglas": [
            ("tos_presente", True, 0.6),
            ("tipo_tos", "productiva", 0.6),
            ("duracion_tos", "<21", 0.7),
            ("fiebre", False, 0.4),
            ("tabaquismo", True, 0.4)
        ],
        "pruebas_adicionales": "Generalmente no requiere estudios, solo en caso de sospecha de complicación (Rx de tórax).",
        "tratamiento_inicial": "Manejo sintomático: hidratación, antitusivos. Evitar antibióticos si la etiología es viral."
    },

    # EPOC
    # Enfocado en tabaquismo, tos crónica y limitación respiratoria en mayores de 40 años.
    "EPOC (Enfermedad Pulmonar Obstructiva Crónica)": {
        "reglas": [
            ("tabaquismo", True, 0.9),
            ("duracion_tos", ">90", 0.7),  # tos crónica > 90 días
            ("disnea", True, 0.8),
            ("tipo_tos", "productiva", 0.5),
            ("edad", ">40", 0.6)
        ],
        "pruebas_adicionales": "Solicitar Espirometría con prueba broncodilatadora (para confirmar la obstrucción).",
        "tratamiento_inicial": "Dejar de fumar inmediatamente. Uso de broncodilatadores de acción prolongada."
    },

    # Resfriado Común
    # Síntomas leves, tos corta, fiebre generalmente ausente o leve.
    "Resfriado Común": {
        "reglas": [
            ("tos_presente", True, 0.4),
            ("tipo_tos", "seca", 0.5),
            ("fiebre", False, 0.7),
            ("duracion_tos", "<7", 0.8),
            ("sibilancia", False, 0.6)
        ],
        "pruebas_adicionales": "Ninguna. El diagnóstico es clínico.",
        "tratamiento_inicial": "Descanso e hidratación. Tratamiento sintomático (analgésicos, descongestionantes)."
    },

    # Faringitis Viral
    # Dolor de garganta sin tos ni disnea importante; diferenciar de faringitis bacteriana si hay alta sospecha.
    "Faringitis (Viral)": {
        "reglas": [
            ("tos_presente", False, 0.7),
            ("fiebre", True, 0.5),
            ("disnea", False, 0.8),
            ("fatiga", False, 0.6)
        ],
        "pruebas_adicionales": "Prueba rápida de antígeno estreptocócico o cultivo faríngeo si hay alta sospecha bacteriana.",
        "tratamiento_inicial": "Reposo de voz e hidratación. Manejo del dolor."
    },

    # Laringitis Viral
    # Pérdida de la voz y tos seca de corta duración.
    "Laringitis (Viral)": {
        "reglas": [
            ("tos_presente", True, 0.6),
            ("tipo_tos", "seca", 0.7),
            ("fiebre", False, 0.5),
            ("duracion_tos", "<7", 0.6)
        ],
        "pruebas_adicionales": "Ninguna. El diagnóstico es clínico.",
        "tratamiento_inicial": "Reposo de voz absoluto. Evitar irritantes y humedecer el ambiente."
    },

    # Sinusitis Aguda
    # Dolor facial, congestión y tos que puede prolongarse más de una semana.
    "Sinusitis Aguda": {
        "reglas": [
            ("fiebre", True, 0.5),
            ("dolor_pecho", False, 0.7),
            ("duracion_tos", ">7", 0.4)
        ],
        "pruebas_adicionales": "Tomografía Computarizada (TC) solo si los síntomas son persistentes o graves, no es de rutina.",
        "tratamiento_inicial": "Analgésicos y descongestionantes. Se debe consultar si persiste más de 10 días."
    },

    # Alergia Respiratoria
    # Síntomas crónicos relacionados con exposición a alérgenos y antecedentes personales.
    "Alergia Respiratoria": {
        "reglas": [
            ("antecedentes_alergicos", True, 0.9),
            ("tos_presente", True, 0.5),
            ("fiebre", False, 0.8),
            ("contaminantes", True, 0.7)
        ],
        "pruebas_adicionales": "Pruebas cutáneas o análisis de IgE específicos para identificar alérgenos.",
        "tratamiento_inicial": "Identificar y evitar el alérgeno. Antihistamínicos o corticoides nasales."
    }
}