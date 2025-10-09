import tkinter as tk                    # Importa Tkinter para crear la ventana principal.
from tkinter import ttk, scrolledtext   # Widgets avanzados de Tkinter (ttk) y área de texto con scroll.


# En este modulo se realiza lo siguiente:
# - Definir la clase de la vista (interfaz gráfica) usando Tkinter.
# - Construir todos los widgets (botones, entradas, etiquetas, tabla).
# - Proveer métodos públicos para que el controlador pueda interactuar con la vista.

class SpamDetectorView:
    # 
    def __init__(self, root):
        # root: ventana principal de Tk.
        self.root = root
        root.title("Detector de Spam mediante ML")
        root.geometry("1000x700")
        root.minsize(800, 600)
        
        # Configuracion del grid principal para que escale.
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # Configuracion del padding del frame principal.
        self.frame_main = ttk.Frame(root, padding="10")
        self.frame_main.grid(row=0, column=0, sticky="nsew")
        self.frame_main.columnconfigure(0, weight=1)
        self.frame_main.columnconfigure(1, weight=1)
        self.frame_main.rowconfigure(1, weight=1)

        # Sección de entrada (analizador).
        frame_input = ttk.LabelFrame(self.frame_main, text=" Analizador de Correo ", padding="15")
        frame_input.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # Remitente (opcional).
        ttk.Label(frame_input, text="Remitente (Opcional):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.entry_correo = ttk.Entry(frame_input, width=50)
        self.entry_correo.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        # Asunto.
        ttk.Label(frame_input, text="Asunto:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.entry_asunto = ttk.Entry(frame_input, width=50)
        self.entry_asunto.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        # Mensaje (área grande con scroll).
        ttk.Label(frame_input, text="Mensaje:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.entry_mensaje = scrolledtext.ScrolledText(frame_input, wrap=tk.WORD, height=5, width=50)
        self.entry_mensaje.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        style = ttk.Style()
        style.configure('Analyze.TButton', font=('Helvetica', 14, 'bold'), padding=(10, 8))

        # Aumenta texto, padding y ancho; sticky='ew' para que se expanda horizontalmente
        self.btn_analizar = ttk.Button(frame_input, text="🔍 Analizar Correo", style='Analyze.TButton', width=36)
        self.btn_analizar.grid(row=3, column=0, columnspan=2, pady=30, sticky='ew')

        # Asegúrate también de que la segunda columna del frame_input sea expandible:
        frame_input.columnconfigure(0, weight=0)
        frame_input.columnconfigure(1, weight=1)

        # Etiqueta para mostrar el resultado del análisis (spam/ham u otro).
        self.label_resultado = ttk.Label(frame_input, text="Esperando análisis...", font=("Helvetica", 16, "bold"))
        self.label_resultado.grid(row=4, column=0, columnspan=2, pady=5)
        frame_input.columnconfigure(1, weight=1)

        # Sección de visualización de datos (tabla).
        frame_data_viewer = ttk.LabelFrame(self.frame_main, text=" Datos del Archivo (Emails.csv) ", padding="10")
        frame_data_viewer.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        frame_data_viewer.columnconfigure(0, weight=1)
        frame_data_viewer.rowconfigure(0, weight=1)

        # Treeview con columnas para las columnas del CSV.
        self.tree = ttk.Treeview(frame_data_viewer, columns=("Categoría", "Correo", "Asunto", "Message"), show="headings")
        self.tree.grid(row=0, column=0, sticky='nsew')

        # Scrollbar vertical.
        vsb = ttk.Scrollbar(frame_data_viewer, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky='ns')
        self.tree.configure(yscrollcommand=vsb.set)

        # Scrollbar horizontal.
        hsb = ttk.Scrollbar(frame_data_viewer, orient="horizontal", command=self.tree.xview)
        hsb.grid(row=1, column=0, sticky='ew')
        self.tree.configure(xscrollcommand=hsb.set)

        # Encabezados de columnas (texto que se muestra).
        self.tree.heading("Categoría", text="Categoría", anchor=tk.W)
        self.tree.heading("Correo", text="Remitente", anchor=tk.W)
        self.tree.heading("Asunto", text="Asunto", anchor=tk.W)
        self.tree.heading("Message", text="Mensaje (Extracto)", anchor=tk.W)

        # Ancho y comportamiento de redimensionado de columnas.
        self.tree.column("Categoría", width=80, stretch=tk.NO)
        self.tree.column("Correo", width=150, stretch=tk.NO)
        self.tree.column("Asunto", width=250, stretch=tk.NO)
        self.tree.column("Message", width=400, stretch=tk.YES)


    # Métodos públicos (API para el controlador)

    def set_analyze_command(self, callback):
        # Conecta la acción del botón 'Analizar' con una función del controlador.
        self.btn_analizar.config(command=callback)

    def bind_tree_select(self, callback):
        # Conecta la selección de una fila en la tabla con un handler (controlador).
        self.tree.bind("<<TreeviewSelect>>", callback)

    # Llena la tabla con los datos del DataFrame.
    def populate_tree(self, df):
        # Limpia filas anteriores.
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Inserta filas (mostrar solo un extracto del mensaje).
        for index, row in df.head(200).iterrows():
            msg_snippet = row['Message'][:70] + '...' if len(row['Message']) > 70 else row['Message']
            # iid = str(index) permite al controlador localizar la fila en el DataFrame.
            self.tree.insert("", tk.END, iid=str(index), values=(row['Categoría'], row['Correo'], row['Asunto'], msg_snippet))

    # Obtiene los textos de entrada del usuario.
    def get_input_texts(self):
        # Leer los textos que puso el usuario en los campos (asunto y mensaje).
        asunto = self.entry_asunto.get()
        mensaje = self.entry_mensaje.get("1.0", tk.END).strip()
        return asunto, mensaje

    # Actualiza la etiqueta grande con el resultado (texto y color opcional).
    def set_result_text(self, text, color='black'):
        self.label_resultado.config(text=text, foreground=color)

    # Rellena los campos de remitente/asunto/mensaje (usado cuando se selecciona una fila).
    def fill_fields(self, remitente='', asunto='', mensaje=''):
        self.entry_correo.delete(0, tk.END)
        self.entry_correo.insert(0, remitente)
        self.entry_asunto.delete(0, tk.END)
        self.entry_asunto.insert(0, asunto)
        self.entry_mensaje.delete('1.0', tk.END)
        self.entry_mensaje.insert('1.0', mensaje)
