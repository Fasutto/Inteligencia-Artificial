# Interfaz gráfica (Tkinter) para el Sistema Experto de diagnóstico respiratorio.
# Este módulo construye la GUI, recoge entradas del usuario y genera la salida llamando a la función de lógica (pasada desde main.py).

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys

# Importamos la base de conocimiento para poder leer campos como 'pruebas_adicionales' y 'tratamiento_inicial' en el formateador de resultados.
try:
    from base_conocimiento import BASE_DE_CONOCIMIENTO
except ImportError:
    print("Error: No se pudo importar base_conocimiento.py. Asegúrese de ejecutar main.py")
    sys.exit(1)

# CLASE PRINCIPAL DE LA INTERFAZ GRÁFICA (GUI)

# La clase SistemaExpertoGUI construye los widgets, mantiene el estado de las variables (tk.Variable) y expone métodos para recopilar datos y ejecutar el diagnóstico (delegando la lógica externa).
class SistemaExpertoGUI:
    def __init__(self, master, ejecutar_logica_se):
        # ejecutar_logica_se: función inyectada desde main.py que recibe un dict con los datos del paciente y devuelve texto/resultado.
        self.master = master
        self.master.title("🩺 Sistema Experto: Diagnóstico Respiratorio (Evidence-03)")
        self.master.geometry("1200x800")
        
        # Guardamos la función de lógica para llamarla cuando el usuario pulse el botón.
        self.ejecutar_logica_se = ejecutar_logica_se

        # Diccionario donde almacenamos las tk.BooleanVar / tk.StringVar usadas por widgets.
        # Permite recorrer todas las variables de manera uniforme al recopilar datos.
        self.variables = {}

        # Construcción de la interfaz dividida (panel izquierdo: entrada, derecho: resultados)
        self.crear_paneles_divisibles()
        
    # Crea el PanedWindow con el panel de entrada (izquierda) y resultados (derecha).
    def crear_paneles_divisibles(self):
        
        # Pane horizontal para permitir redimensionar paneles por el usuario.
        self.paned_window = ttk.PanedWindow(self.master, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Panel Izquierdo (Entrada de Datos) ---
        # Se usa un frame padre con canvas y scrollbar para permitir formularios largos.
        self.frame_entrada_padre = ttk.Frame(self.paned_window, padding="10")
        self.paned_window.add(self.frame_entrada_padre, weight=1) 
        
        # Canvas para contenido desplazable + scrollbar vertical
        self.canvas = tk.Canvas(self.frame_entrada_padre, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self.scrollbar = ttk.Scrollbar(self.frame_entrada_padre, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Marco deslizable que contendrá las preguntas y el botón
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.inner_frame = ttk.Frame(self.scrollable_frame, padding=(12,12))  # margen interior consistente

        # Guardamos el id de la ventana dentro del canvas para poder ajustar su ancho:
        self.canvas_window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Ajustamos la scrollregion cada vez que cambia el tamaño del contenido
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.config(scrollregion=self.canvas.bbox("all")))
        
        # Función para adaptar el ancho del contenido al cambiar el tamaño del frame padre.
        def _ajustar_ancho_canvas(event):
            try:
                sbw = self.scrollbar.winfo_width() or 20
            except Exception:
                sbw = 20
            margen_total = 24  # padding interno + margen extra
            nuevo_ancho = max(event.width - sbw - margen_total, 200)
            # Cambiamos el ancho del elemento ventana en el canvas para evitar overflow horizontal.
            self.canvas.itemconfigure(self.canvas_window_id, width=nuevo_ancho)

        self.frame_entrada_padre.bind('<Configure>', _ajustar_ancho_canvas)

        # Empaquetamos el inner_frame que contiene los widgets reales y lo llenamos
        self.inner_frame.pack(fill='both', expand=True)
        self.crear_secciones_entrada(self.inner_frame) 
        
        
        # --- Botón de Diagnóstico (Dentro del marco deslizable, al final del formulario) ---
        style = ttk.Style()
        style.configure('Diagnosis.TButton', font=('Arial', 12, 'bold'), 
                        background='#4CAF50', foreground='black')
                        
        # botón dentro del inner_frame para respetar el padding; llama a ejecutar_diagnostico_gui.
        ttk.Button(self.inner_frame, text="Ejecutar Diagnóstico", command=self.ejecutar_diagnostico_gui, 
        style='Diagnosis.TButton').grid(row=99, column=0, columnspan=3, pady=18, padx=6, sticky='ew')
        
        # --- Panel Derecho (Resultados) ---
        self.frame_resultados = ttk.Frame(self.paned_window, padding="10")
        self.paned_window.add(self.frame_resultados, weight=1) 
        self.crear_seccion_resultados(self.frame_resultados)

        # Establecer la posición inicial del divisor (sash) en la mitad de la ventana.
        self.master.update()
        self.paned_window.sashpos(0, self.master.winfo_width() // 2)

    # ... (El resto de la clase, incluyendo los métodos de agregar widgets y recopilar datos, permanece igual) ...

    # Organiza las preguntas en secciones usando LabelFrames para claridad visual.
    def crear_secciones_entrada(self, parent_frame):
        
        current_row = 0

        # --- SECCIÓN 1: DATOS BÁSICOS (Obligatorio) ---
        lf1 = ttk.LabelFrame(parent_frame, text="1. Datos Demográficos y Básicos", padding="10")
        lf1.grid(row=current_row, column=0, sticky='ew', padx=5, pady=5)
        current_row += 1
        # Agrega widgets de edad y sexo
        current_row = self._agregar_widgets_basicos(lf1, current_row=0)

        # --- SECCIÓN 2: SÍNTOMAS PRINCIPALES ---
        lf2 = ttk.LabelFrame(parent_frame, text="2. Síntomas Respiratorios y Sistémicos", padding="10")
        lf2.grid(row=current_row, column=0, sticky='ew', padx=5, pady=5)
        current_row += 1
        current_row = self._agregar_widgets_sintomas(lf2, current_row=0)
        
        # --- SECCIÓN 4: HALLAZGOS FÍSICOS/LABORATORIO ---
        lf4 = ttk.LabelFrame(parent_frame, text="4. Hallazgos (Auscultación / Bioquímica)", padding="10")
        lf4.grid(row=current_row, column=0, sticky='ew', padx=5, pady=5)
        current_row += 1
        current_row = self._agregar_widgets_hallazgos(lf4, current_row=0)
        
        # --- SECCIÓN 3: FACTORES DE RIESGO ---
        lf3 = ttk.LabelFrame(parent_frame, text="3. Factores de Riesgo (Antecedentes)", padding="10")
        lf3.grid(row=current_row, column=0, sticky='ew', padx=5, pady=5)
        current_row += 1
        current_row = self._agregar_widgets_riesgos(lf3, current_row=0)

        parent_frame.grid_columnconfigure(0, weight=1)

    def _agregar_widgets_basicos(self, frame, current_row):
        # Edad (Entry - Obligatorio)
        ttk.Label(frame, text="Edad (años):").grid(row=current_row, column=0, padx=5, pady=5, sticky='w')
        self.entry_edad = ttk.Entry(frame)
        self.entry_edad.grid(row=current_row, column=1, columnspan=2, padx=5, pady=5, sticky='ew')
        current_row += 1
        
        # Sexo (Combobox) - se guarda en self.variables para un acceso uniforme
        ttk.Label(frame, text="Sexo:").grid(row=current_row, column=0, padx=5, pady=5, sticky='w')
        self.variables['sexo'] = tk.StringVar(value="M")
        ttk.Combobox(frame, textvariable=self.variables['sexo'], values=["M", "F"]).grid(row=current_row, column=1, columnspan=2, padx=5, pady=5, sticky='ew')
        current_row += 1
        
        frame.columnconfigure(1, weight=1)
        return current_row

    def _agregar_widgets_sintomas(self, frame, current_row):
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)
        
        # Síntomas Binarios (usando RadioButton Sí/No)
        sintomas_binarios = {
            'tos_presente': "1. Presencia de tos:", 
            'disnea': "2. Dificultad para respirar (Disnea):", 
            'sibilancia': "3. Pitido al respirar (Sibilancia):", 
            'dolor_pecho': "4. Dolor en el pecho:", 
            'fiebre': "5. Fiebre (Temperatura elevada):", 
            'fatiga': "6. Fatiga/Cansancio excesivo:",
            'dolor_garganta': "7. Dolor de garganta:", 
            'secrecion_nasal': "8. Secreción o congestión nasal:", 
            'dolor_cabeza': "9. Dolor de cabeza (Cefalea):"
        }
        
        # Para cada síntoma creamos una tk.BooleanVar y dos Radiobuttons (Sí/No).
        for key, label_text in sintomas_binarios.items():
            ttk.Label(frame, text=label_text).grid(row=current_row, column=0, padx=5, pady=2, sticky='w')
            self.variables[key] = tk.BooleanVar(value=False)
            
            # RadioButton SÍ
            ttk.Radiobutton(frame, text="Sí", variable=self.variables[key], value=True).grid(row=current_row, column=1, padx=5, pady=2, sticky='w')
            # RadioButton NO
            ttk.Radiobutton(frame, text="No", variable=self.variables[key], value=False).grid(row=current_row, column=2, padx=5, pady=2, sticky='w')
            current_row += 1

        # Tipo de Tos (Combobox) - opción vacía por defecto
        ttk.Label(frame, text="10. Tipo de tos:").grid(row=current_row, column=0, padx=5, pady=5, sticky='w')
        self.variables['tipo_tos'] = tk.StringVar(value="")
        ttk.Combobox(frame, textvariable=self.variables['tipo_tos'], values=["", "seca", "productiva"]).grid(row=current_row, column=1, columnspan=2, padx=5, pady=5, sticky='ew')
        current_row += 1

        # Duración de Tos (Entry) - se recogerá como entero
        ttk.Label(frame, text="11. Duración de la tos (días):").grid(row=current_row, column=0, padx=5, pady=5, sticky='w')
        self.entry_duracion_tos = ttk.Entry(frame)
        self.entry_duracion_tos.grid(row=current_row, column=1, columnspan=2, padx=5, pady=5, sticky='ew')
        current_row += 1
        
        return current_row

    def _agregar_widgets_riesgos(self, frame, current_row):
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)
        
        riesgos_binarios = {
            'tabaquismo': "1. Antecedentes de tabaquismo:", 
            'contaminantes': "2. Exposición a contaminantes:", 
            'antecedentes_alergicos': "3. Antecedentes alérgicos/familiares:"
        }
        
        # Igual que en síntomas: BooleanVar + Radiobuttons
        for key, label_text in riesgos_binarios.items():
            ttk.Label(frame, text=label_text).grid(row=current_row, column=0, padx=5, pady=2, sticky='w')
            self.variables[key] = tk.BooleanVar(value=False)
            ttk.Radiobutton(frame, text="Sí", variable=self.variables[key], value=True).grid(row=current_row, column=1, padx=5, pady=2, sticky='w')
            ttk.Radiobutton(frame, text="No", variable=self.variables[key], value=False).grid(row=current_row, column=2, padx=5, pady=2, sticky='w')
            current_row += 1
            
        return current_row

    def _agregar_widgets_hallazgos(self, frame, current_row):
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)

        # Crepitaciones (RadioButtons)
        ttk.Label(frame, text="1. Crepitaciones/Ronquidos (Ausc.):").grid(row=current_row, column=0, padx=5, pady=2, sticky='w')
        self.variables['crepitaciones'] = tk.BooleanVar(value=False)
        ttk.Radiobutton(frame, text="Sí", variable=self.variables['crepitaciones'], value=True).grid(row=current_row, column=1, padx=5, pady=2, sticky='w')
        ttk.Radiobutton(frame, text="No", variable=self.variables['crepitaciones'], value=False).grid(row=current_row, column=2, padx=5, pady=2, sticky='w')
        current_row += 1
        
        # Saturación de Oxígeno (Entry) - campo numérico, se transforma a float al recopilar
        ttk.Label(frame, text="2. Saturación de Oxígeno (%):").grid(row=current_row, column=0, padx=5, pady=5, sticky='w')
        self.entry_sat_oxigeno = ttk.Entry(frame)
        self.entry_sat_oxigeno.grid(row=current_row, column=1, columnspan=2, padx=5, pady=5, sticky='ew')
        current_row += 1
        
        # PCR Elevada (RadioButtons) - marcador de laboratorio binario
        ttk.Label(frame, text="3. PCR Elevada (Laboratorio):").grid(row=current_row, column=0, padx=5, pady=2, sticky='w')
        self.variables['pcr_elevada'] = tk.BooleanVar(value=False)
        ttk.Radiobutton(frame, text="Sí", variable=self.variables['pcr_elevada'], value=True).grid(row=current_row, column=1, padx=5, pady=2, sticky='w')
        ttk.Radiobutton(frame, text="No", variable=self.variables['pcr_elevada'], value=False).grid(row=current_row, column=2, padx=5, pady=2, sticky='w')
        current_row += 1
        
        return current_row

    # Construye el panel derecho para la presentación de resultados.
    def crear_seccion_resultados(self, frame):

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        ttk.Label(frame, text="Resultados del Diagnóstico:", font=('Arial', 14, 'bold'), foreground="#3366CC").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        
        # Área de texto desplazable para mostrar el resultado. Se utiliza ScrolledText
        # para permitir salida extensa (explicaciones, recomendaciones, etc.).
        self.text_resultados = scrolledtext.ScrolledText(frame, wrap="word", width=60, height=40, font=('Consolas', 10), bg="#F8F8FF", fg="#333333")
        self.text_resultados.grid(row=1, column=0, padx=10, pady=5, sticky='nsew')
        
    # --- Lógica de Recolección y Ejecución ---

    # Recolecta todos los datos de los widgets en un dict homogéneo.
    def recopilar_datos_gui(self):
        # Convierte campos numéricos (edad, duración, saturación) y obtiene valores de las tk.Variable almacenadas en self.variables.
        # Devuelve None y muestra error si hay problema en conversiones.
        
        datos = {}
        
        try:
            # Recolección de Entrys y Variables Booleanas/Strings
            for key, var in self.variables.items():
                datos[key] = var.get()

            # Datos Básicos (Edad): si vacío -> 0 (se valida en ejecutar_diagnostico_gui)
            edad_str = self.entry_edad.get()
            datos['edad'] = int(edad_str) if edad_str else 0
            
            # Duración de Tos
            duracion_str = self.entry_duracion_tos.get()
            datos['duracion_tos'] = int(duracion_str) if duracion_str else 0
            
            # Saturación de Oxígeno: si vacío por defecto 100.0
            sat_ox_str = self.entry_sat_oxigeno.get()
            datos['sat_oxigeno'] = float(sat_ox_str) if sat_ox_str else 100.0

            return datos
            
        except ValueError as e:
            # Mostrar diálogo de error si algún campo numérico no es convertible
            messagebox.showerror("Error de Entrada", f"Por favor, revise los campos numéricos. Error: {e}")
            return None

    # Acción al pulsar el botón de diagnóstico, con validación de campos obligatorios.
    def ejecutar_diagnostico_gui(self):

        # 1) Valida campo Edad (obligatorio, entero positivo).
        # 2) Llama a recopilar_datos_gui() para obtener el dict de entrada.
        # 3) Llama a la función de lógica inyectada y muestra el resultado en el panel derecho.
        
        # 1. Validación de Datos Obligatorios (Edad)
        try:
            edad = self.entry_edad.get()
            if not edad or int(edad) <= 0:
                messagebox.showerror("Error de Validación", "El campo Edad es obligatorio y debe ser un número positivo.")
                return
        except ValueError:
            messagebox.showerror("Error de Validación", "El campo Edad debe ser un número entero válido.")
            return

        # 2. Ejecución de la Lógica
        datos = self.recopilar_datos_gui()
        
        if datos:
            # Limpiamos la salida previa y presentamos la nueva
            self.text_resultados.delete('1.0', tk.END)
            
            # Ejecutar la lógica del motor de inferencia (llamada al main.py)
            # Ejecutar_logica_se debe devolver un string ya formateado para mostrar.
            resultado_texto = self.ejecutar_logica_se(datos)
            
            # Mostrar el resultado en el ScrolledText del panel derecho.
            self.text_resultados.insert(tk.END, resultado_texto)
            
# ====================================================================
# Funciones de Salida y Formato para main.py
# ====================================================================

# Inicia la aplicación Tkinter con la función de lógica inyectada.
def iniciar_interfaz(ejecutar_logica_se):
    root = tk.Tk()
    SistemaExpertoGUI(root, ejecutar_logica_se)
    root.mainloop()

# Genera los resultados para la GUI enfocándose en una ÚNICA Hipótesis, separando Pruebas Adicionales y Tratamiento Inicial.
def resultados_Analisis(diagnostico_principal, info_principal, certeza_validacion, reglas_validacion):

    # Parámetros:
    #   - diagnostico_principal: clave de la hipótesis (string)
    #   - info_principal: dict con claves 'certeza' y 'explicaciones' entre otras
    #   - certeza_validacion: porcentaje final tras validación (número)
    #   - reglas_validacion: lista de reglas usadas en la validación

    # Retorna:
    #   - string con el contenido formateado para mostrar en la GUI.

    output = []
    
    # Obtener datos de la hipótesis principal y las nuevas secciones
    certeza_forward = info_principal['certeza']
    explicaciones = info_principal['explicaciones']
    
    # Acceder a las nuevas claves de la Base de Conocimiento para recomendaciones
    info_bc = BASE_DE_CONOCIMIENTO.get(diagnostico_principal, {})
    pruebas_adicionales = info_bc.get("pruebas_adicionales", "No se requieren pruebas específicas de rutina.")
    tratamiento_inicial = info_bc.get("tratamiento_inicial", "Manejo sintomático general.")
    
    # --- Título del Diagnóstico ÚNICA ---
    output.append("=" * 60)
    output.append(f" DIAGNÓSTICO HIPÓTESIS ÚNICA:")
    output.append(f"   **{diagnostico_principal}**")
    output.append(f"   Factor de Certeza Inicial (FC): {certeza_forward}%")
    output.append("=" * 60)
    
    # --- MÓDULO DE EXPLICACIÓN (Forward Chaining) ---
    output.append("\n MÓDULO DE EXPLICACIÓN: ¿Cómo se llegó a esta hipótesis?")
    output.append(f"   El diagnóstico fue derivado por la activación de {len(explicaciones)} reglas:")
    for regla in explicaciones:
        output.append(f"     * Regla activada: {regla}")
        
    # --- SECCIÓN DE VALIDACIÓN (Backward Chaining) ---
    output.append("\n" + "#" * 60)
    output.append(f" VALIDACIÓN DE LA HIPÓTESIS")
    output.append("#" * 60)
    
    # 1. Resultado de la Validación
    output.append(f"   > Certeza confirmada por el Motor de Validación: {certeza_validacion}%")
    output.append(f"   > Reglas de {diagnostico_principal} cumplidas: {len(reglas_validacion)}")

    # 2. SUGERENCIAS DETALLADAS (Pruebas + Recomendaciones)
    output.append("\n SUGERENCIAS PARA CONCLUSIÓN MÁS EXACTA:")
    output.append("---")
    
    output.append("\n   **A. Análisis y Estudios Adicionales (Pruebas de Confirmación):**")
    output.append(f"     > {pruebas_adicionales}")
    
    output.append("\n   **B. Recomendaciones y Tratamiento Inicial (Acciones Inmediatas):**")
    output.append(f"     > {tratamiento_inicial}")
    
    output.append("\n   CONSIDERACIÓN ADICIONAL:")
    if certeza_forward < 70:
        output.append("     El FC es moderado. Se recomienda ENCARECIDAMENTE la realización de las pruebas sugeridas antes de confirmar el diagnóstico.")
    else:
        output.append("     El FC es alto. La confianza en esta hipótesis es elevada, pero las pruebas sugeridas ayudan a descartar diferenciales.")
        
    return "\n".join(output)