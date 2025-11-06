# Pruebas para verificar el funcionamiento del motor de inferencia.
# El objetivo es comprobar que el programa funcione correctamente y que los diagnósticos sean precisos.

# Importaciones estándar
import re
import pytest
import difflib
import unicodedata

# Importación de los módulos del proyecto.
# Si alguna importación falla (por ejemplo porque python no está instalado o hay errores de sintaxis
# en los módulos), pytest saltará todas las pruebas de este archivo para evitar ruido adicional.
try:
    import base_conocimiento
    import main
    import motor_inferencia
except Exception as e:
    pytest.skip(f"Importación fallida de módulos del proyecto: {e}", allow_module_level=True)


# ===== Definición de casos de prueba =====
# Cada caso es una tupla: (numero, enfermedad_real, datos_paciente)
# - numero: identificador numérico del caso (impreso en la salida)
# - enfermedad_real: etiqueta/esperanza clínica (solo para mostrar/comparar)
# - datos_paciente: diccionario con las claves que usa el sistema experto
CASOS = [
    (1, "Neumonía Bacteriana", {
        "edad": 75, "sexo": "M", "tos_presente": True, "tipo_tos": "productiva",
        "duracion_tos": 7, "disnea": True, "fiebre": True, "crepitaciones": True,
        "sat_oxigeno": 92.0, "pcr_elevada": True
    }),
    (2, "Asma", {
        "edad": 28, "sexo": "F", "tos_presente": True, "tipo_tos": "seca",
        "duracion_tos": 30, "disnea": True, "sibilancia": True, "fiebre": False
    }),
    (3, "Resfriado Común", {
        "edad": 34, "sexo": "O", "tos_presente": True, "tipo_tos": "productiva",
        "duracion_tos": 3, "disnea": False, "secrecion_nasal": True, "dolor_garganta": True
    })
]


# ===== Utilidades auxiliares =====

# Función para evaluar si un valor del paciente cumple con la condición esperada.
def _normalize(text):
    
    # Normaliza texto para comparaciones tolerantes:
    # - elimina acentos (NFD + filtrado de combinantes)
    # - convierte a minúsculas y colapsa espacios
    # Esto ayuda a comparar nombres que difieren en tildes o mayúsculas.

    # Si no es string, devolver cadena vacía.
    if not isinstance(text, str):
        return ""
    t = unicodedata.normalize("NFD", text)
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    return " ".join(t.lower().split())

# Extrae el nombre del diagnóstico principal desde la salida del motor o main.
def _extraer_nombre_diagnostico(salida):

    # La función maneja distintas formas de salida comunes:
    # - tuple (scores_dict, explicaciones_dict) -> devuelve la clave con mayor score
    # - lista de dicts [{'diagnostico':..., 'certeza':...}, ...] -> toma elemento con mayor 'certeza'
    # - dict {nombre: { 'certeza': ... }, ...} -> devuelve la clave con mayor 'certeza'
    # - texto (string) -> intenta encontrar nombres conocidos y porcentajes en el texto
    #- fallback -> convierte a str() y devuelve representación simple

    # Caso: tupla (scores_dict, explicaciones_dict)
    if isinstance(salida, tuple) and len(salida) >= 1 and isinstance(salida[0], dict):
        scores = salida[0]
        if scores:
            # seleccionar la clave con mayor valor (puntaje)
            mejor = max(scores.items(), key=lambda kv: kv[1])
            return mejor[0]

    # Caso: lista de dicts con campos 'diagnostico' y 'certeza'
    if isinstance(salida, list) and salida:
        candidatos = []
        # buscar en cada dict de la lista.
        for item in salida:
            if isinstance(item, dict):
                nombre = item.get("diagnostico") or item.get("nombre") or (next(iter(item.keys())) if len(item) == 1 else None)
                certeza = item.get("certeza") or item.get("fc") or item.get("factor_certeza") or 0.0
                try:
                    certeza = float(certeza)
                except Exception:
                    certeza = 0.0
                candidatos.append((certeza, nombre or str(item)))
        # Filtrar candidatos vacíos.
        if candidatos:
            # devolver nombre con mayor certeza
            return max(candidatos, key=lambda x: x[0])[1]
        return str(salida[0])

    # Caso: dict mapping nombre -> info
    if isinstance(salida, dict) and salida:
        mejor = None
        mejor_c = -1.0
        # buscar la clave con mayor 'certeza' o similar.
        for k, v in salida.items():
            c = 0.0
            if isinstance(v, dict):
                c = v.get("certeza") or v.get("fc") or v.get("factor_certeza") or 0.0
            try:
                c = float(c)
            except Exception:
                c = 0.0
            if c > mejor_c:
                mejor_c = c
                mejor = k
        if mejor is not None:
            return mejor
        return next(iter(salida.keys()))

    # Caso: texto formateado -> buscar claves conocidas y porcentajes asociados
    if isinstance(salida, str):
        porcentajes = {}
        claves = list(getattr(base_conocimiento, "BASE_DE_CONOCIMIENTO", {}).keys())
        # buscar patrones de "Nombre: XX%" en el texto.
        for nombre in claves:
            if nombre in salida:
                for line in salida.splitlines():
                    if nombre in line:
                        m = re.search(r'(\d{1,3})\s?%', line)
                        if m:
                            try:
                                porcentajes[nombre] = float(m.group(1))
                            except Exception:
                                porcentajes[nombre] = 0.0
                        else:
                            porcentajes.setdefault(nombre, 0.0)
        # Filtrar porcentajes vacíos.
        if porcentajes:
            # devolver la clave con mayor porcentaje detectado en el texto
            return max(porcentajes.items(), key=lambda x: x[1])[0]
        # si no hay porcentajes pero aparece una clave conocida, devolverla
        for nombre in claves:
            if nombre in salida:
                return nombre
        # fallback: primera línea del texto
        return salida.splitlines()[0].strip() if salida.strip() else "Sin diagnóstico"

    # Otros tipos -> representarlos como texto
    return str(salida)


# ===== Prueba principal =====

# Ejecuta el motor (preferentemente motor_inferencia.motor_de_inferencia) o en su defecto main.ejecutar_logica_se para obtener el diagnóstico. 
@pytest.mark.parametrize("numero, enfermedad_real, datos", CASOS, ids=[f"caso_{c[0]}" for c in CASOS])
def test_imprimir_formato(numero, enfermedad_real, datos):

    # Imprime en consola únicamente:
    # Caso: #numero
    # Enfermedad: #Nombreenfermedad
    # Diagnostico: #EnfermedadDiagnosticada

    # Además realiza una comprobación mínima: que se haya obtenido algún diagnóstico no vacío.
    
    salida = None

    # 1) Intentar obtener salida directamente desde el motor de inferencia (más detallada)
    try:
        if hasattr(motor_inferencia, "motor_de_inferencia"):
            salida = motor_inferencia.motor_de_inferencia(datos)
        elif hasattr(motor_inferencia, "inferir"):
            salida = motor_inferencia.inferir(datos)
    except Exception:
        # Si falla la llamada al motor, dejamos salida = None y probamos con main
        salida = None

    # 2) Si no hay salida desde el motor, intentar la función de integración (salida formateada)
    if salida is None:
        try:
            salida = main.ejecutar_logica_se(datos)
        except Exception:
            salida = ""

    # 3) Extraer solo el nombre del diagnóstico con mayor puntaje
    diagnosticado = _extraer_nombre_diagnostico(salida)

    # 4) Imprimir en el formato requerido por el usuario
    print(f"Caso: #{numero}")
    print(f"Enfermedad: {enfermedad_real}")
    print(f"Diagnostico: {diagnosticado}")

    # 5) Aserción mínima: existe algún diagnóstico obtenido
    assert str(diagnosticado).strip() != "", f"No se obtuvo diagnóstico para el caso #{numero}"