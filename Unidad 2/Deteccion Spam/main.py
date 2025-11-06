# Importar Tkinter para crear la ventana principal
import tkinter as tk

# Importar la vista y el controlador implementados en módulos separados.
from view import SpamDetectorView
from controller import SpamDetectorController

# En este modulo se realiza lo siguiente:
# - Instancia la ventana raíz de Tkinter.
# - Crea la vista (construye todos los widgets).

if __name__ == "__main__":
        # Crear la ventana raíz de la aplicación
        root = tk.Tk()

        # Instancia la vista (construye todos los widgets).
        view = SpamDetectorView(root)

        # Instancia el controlador, el cual cargará modelo y datos y enlazará la vista.
        controller = SpamDetectorController(root, view)

        # Inicia la GUI.
        root.mainloop()