# Interfaz gráfica del puzzle 8 usando Tkinter.
# Autor: Espinoza Felix Fausto Gabriel.
# Fecha: 2025-8-31.
import tkinter as tk

# Constantes de estilo.
FONT_FAMILY = "Segoe UI"
SOLVE_BUTTON_TEXT = "Resolver Puzzle"

class PuzzleView:
    
    # Inicializa la vista principal del puzzle con la ventana raíz y el controlador opcional.
    def __init__(self, root, controller=None):
        self.controller = controller
        self.root = root
        self.root.title("Puzzle 8 - Algoritmo A*")
        self.root.configure(bg='#f0f0f0')
        self.root.geometry("450x550")
        self.root.minsize(400, 500)
        
        # Configuración del layout principal (grid) para distribuir espacio entre secciones.
        self.root.grid_rowconfigure(0, weight=0)  # Título.
        self.root.grid_rowconfigure(1, weight=1)  # Tablero.
        self.root.grid_rowconfigure(2, weight=0)  # Controles.
        self.root.grid_columnconfigure(0, weight=1)
        
        self.buttons = []
        self._setup_ui()

    # Construye y organiza todos los elementos de la interfaz gráfica.
    def _setup_ui(self):
        
        # Título del puzzle.
        title_label = tk.Label(
            self.root,
            text="Puzzle 8",
            font=(FONT_FAMILY, 24, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        title_label.grid(row=0, column=0, pady=(20, 10), sticky="ew")
        
        # Contenedor del tablero.
        self.main_frame = tk.Frame(self.root, bg='#f0f0f0')
        self.main_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        # Configuración del grid interno del tablero (3x3).
        for i in range(3):
            self.main_frame.grid_rowconfigure(i, weight=1, uniform="row")
            self.main_frame.grid_columnconfigure(i, weight=1, uniform="col")

        # Creación de los 9 botones del tablero.
        for i in range(9):
            btn = tk.Button(
                self.main_frame,
                text="",
                font=(FONT_FAMILY, 20, "bold"),
                command=lambda i=i: self._on_tile_click(i),
                relief="flat",
                borderwidth=2,
                cursor="hand2",
                bg='#3498db',
                fg='white',
                activebackground='#2980b9',
                activeforeground='white'
            )
            btn.grid(
                row=i // 3, 
                column=i % 3, 
                padx=3, 
                pady=3, 
                sticky="nsew"
            )
            self.buttons.append(btn)
            
            # Efectos de hover para cada botón del tablero.
            btn.bind("<Enter>", lambda e, b=btn: self._on_hover_enter(b))
            btn.bind("<Leave>", lambda e, b=btn: self._on_hover_leave(b))

        # Contenedor de los controles inferiores.
        controls_frame = tk.Frame(self.root, bg='#f0f0f0')
        controls_frame.grid(row=2, column=0, pady=(10, 20), sticky="ew")
        controls_frame.grid_columnconfigure(0, weight=1)
        controls_frame.grid_columnconfigure(1, weight=1)
        
        # Botón resolver con estilo mejorado.
        self.solve_btn = tk.Button(
            controls_frame,
            text=SOLVE_BUTTON_TEXT,
            command=self._on_solve_click,
            font=(FONT_FAMILY, 14, "bold"),
            bg='#e74c3c',
            fg='white',
            activebackground='#c0392b',
            activeforeground='white',
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            padx=30,
            pady=12
        )
        self.solve_btn.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="ew")
        
        # Botón para reiniciar el puzzle.
        self.restart_btn = tk.Button(
            controls_frame,
            text="Reiniciar",
            command=self._on_restart_click,
            font=(FONT_FAMILY, 14, "bold"),
            bg='#f39c12',
            fg='white',
            activebackground='#e67e22',
            activeforeground='white',
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            padx=30,
            pady=12
        )
        self.restart_btn.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="ew")
        
        # Efectos de hover para los botones de control.
        self.solve_btn.bind("<Enter>", self._on_solve_hover_enter)
        self.solve_btn.bind("<Leave>", self._on_solve_hover_leave)
        self.restart_btn.bind("<Enter>", self._on_restart_hover_enter)
        self.restart_btn.bind("<Leave>", self._on_restart_hover_leave)
        
        # Mensaje de estado informativo.
        self.status_label = tk.Label(
            controls_frame,
            text="¡Haz clic en las fichas para moverlas o usa los botones!",
            font=(FONT_FAMILY, 10),
            bg='#f0f0f0',
            fg='#7f8c8d',
            wraplength=350
        )
        self.status_label.grid(row=1, column=0, columnspan=2, pady=(5, 0))
        
        # Contador de movimientos realizados.
        self.moves_label = tk.Label(
            controls_frame,
            text="Movimientos: 0",
            font=(FONT_FAMILY, 12, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        self.moves_label.grid(row=2, column=0, columnspan=2, pady=(10, 0))

    # Efecto visual al pasar el cursor sobre una ficha (si no está vacía).
    def _on_hover_enter(self, button):
        if button['text']:  # Solo si no es el espacio vacío.
            button.configure(bg='#2980b9', relief="raised")
    
    def _on_hover_leave(self, button):
        if button['text']:  # Solo si no es el espacio vacío.
            button.configure(bg='#3498db', relief="flat")
    
    def _on_solve_hover_enter(self, _event):
        if self.solve_btn['state'] != 'disabled':
            self.solve_btn.configure(bg='#c0392b')
    
    def _on_solve_hover_leave(self, _event):
        if self.solve_btn['state'] != 'disabled':
            self.solve_btn.configure(bg='#e74c3c')
    
    def _on_restart_hover_enter(self, _event):
        if self.restart_btn['state'] != 'disabled':
            self.restart_btn.configure(bg='#e67e22')
    
    def _on_restart_hover_leave(self, _event):
        if self.restart_btn['state'] != 'disabled':
            self.restart_btn.configure(bg='#f39c12')

    # Permite asignar o reasignar el controlador externo.
    def set_controller(self, controller):
        self.controller = controller

    # Callback al hacer clic en una ficha del tablero.
    def _on_tile_click(self, index):
        if self.controller:
            self.controller.move_tile(index)

    # Callback para iniciar la resolución automática del puzzle.
    def _on_solve_click(self):
        if self.controller:
            self.solve_btn.config(
                state=tk.DISABLED,
                text="Resolviendo...",
                bg='#95a5a6'
            )
            self.status_label.config(text="Ejecutando algoritmo A*...")
            self.controller.solve_puzzle()
    
    # Callback para reiniciar el puzzle manualmente.
    def _on_restart_click(self):
        if self.controller:
            # Detener cualquier animación en progreso.
            self.controller.stop_solving()
            # Generar nuevo puzzle.
            self.controller.restart_puzzle()
            # Reactivar botón resolver si estaba deshabilitado.
            self.solve_btn.config(
                state=tk.NORMAL,
                text=SOLVE_BUTTON_TEXT,
                bg='#e74c3c'
            )
            self.status_label.config(text="Nuevo puzzle generado. ¡A jugar!")

    # Actualiza visualmente el tablero según el estado actual.
    def update_board(self, board):
        for i, val in enumerate(board):
            button = self.buttons[i]
            if val == 0:
                # Espacio vacío - estilo especial.
                button.config(
                    text="",
                    bg='#ecf0f1',
                    activebackground='#ecf0f1',
                    relief="flat",
                    cursor="arrow"
                )
            else:
                # Ficha con número - estilo normal.
                button.config(
                    text=str(val),
                    bg='#3498db',
                    activebackground='#2980b9',
                    relief="flat",
                    cursor="hand2"
                )
    
    # Actualiza el contador de movimientos en pantalla.
    def update_moves_counter(self, moves):
        self.moves_label.config(text=f"Movimientos: {moves}")

    # Callback al finalizar la resolución automática.
    def on_solve_complete(self, success=True):
        if success:
            self.solve_btn.config(
                state=tk.NORMAL,
                text=SOLVE_BUTTON_TEXT,
                bg='#e74c3c'
            )
            self.status_label.config(text="¡Puzzle resuelto! Puedes hacer clic en 'Resolver' para otro intento.")
        else:
            self.solve_btn.config(
                state=tk.NORMAL,
                text=SOLVE_BUTTON_TEXT,
                bg='#e74c3c'
            )
            self.status_label.config(text="No se encontró solución. Intenta reorganizar manualmente.")