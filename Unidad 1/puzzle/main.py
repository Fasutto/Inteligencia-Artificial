#Importaciones para interfaces, vista y controlador.
# Autor: Espinoza Felix Fausto Gabriel.
# Fecha: 2025-8-31.
import tkinter as tk   
from view import PuzzleView
from controller import PuzzleController

def main():
    #Creacion de la ventana principal, Conectando vista y controlador.
    root = tk.Tk()
    view = PuzzleView(root)
    controller = PuzzleController(view)
    view.set_controller(controller)
    root.mainloop()

#Ejecuta la aplicacion si el archivo se ejecuta directamente.
if __name__ == "__main__":
    main()