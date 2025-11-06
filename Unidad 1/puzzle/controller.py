# Importa el algoritmo A* y random para mezclar el puzzle.
# Autor: Espinoza Felix Fausto Gabriel.
# Fecha: 2025-8-31.
from model import a_star
import random

class PuzzleController:
    
    # Inicializa atributos para animación y estado del juego.
    def __init__(self, view):
        self.view = view
        self._solution_states = []
        self._animate_index = 0
        self._is_solving = False
        self._animation_id = None
        self._solution_length = 0
        self.moves_count = 0
        self.board = [] # Estado actual del tablero.
        self.restart_puzzle()

    # Detiene la animación si está activa.
    def stop_solving(self):
        if self._is_solving and self._animation_id:
            self.view.root.after_cancel(self._animation_id)
            self._is_solving = False
            self._animation_id = None

    # Reinicia el estado del puzzle con una mezcla aleatoria.
    def restart_puzzle(self):
        self.stop_solving()
        self.moves_count = 0
        self.board = [1, 2, 3, 4, 5, 6, 7, 8, 0]    # Estado resuelto.
        
        for _ in range(1000):
            blank = self.board.index(0) # Posición del espacio vacío.
            neighbors = []
            if blank - 3 >= 0:
                neighbors.append(blank - 3)
            if blank + 3 < 9:
                neighbors.append(blank + 3)
            if blank % 3 != 0:
                neighbors.append(blank - 1)
            if blank % 3 != 2:
                neighbors.append(blank + 1)
                
            if neighbors:
                move_pos = random.choice(neighbors)
                self.board[blank], self.board[move_pos] = self.board[move_pos], self.board[blank]   # Intercambia las fichas.
        
        self.view.update_board(self.board)
        self.view.update_moves_counter(self.moves_count)

    # Mueve una ficha si es adyacente al espacio vacío.
    def move_tile(self, index):
        blank = self.board.index(0)
        neighbors = []
        if blank - 3 >= 0:
            neighbors.append(blank - 3)
        if blank + 3 < 9:
            neighbors.append(blank + 3)
        if blank % 3 != 0:
            neighbors.append(blank - 1)
        if blank % 3 != 2:
            neighbors.append(blank + 1)
        if index in neighbors:
            self.board[blank], self.board[index] = self.board[index], self.board[blank]
            self.moves_count += 1
            self.view.update_board(self.board)
            self.view.update_moves_counter(self.moves_count)
            
            if self.board == [1, 2, 3, 4, 5, 6, 7, 8, 0]:
                self.view.status_label.config(text=f"¡Felicidades! Resolviste el puzzle en {self.moves_count} movimientos!")

    # Resuelve el puzzle automáticamente usando A*.
    def solve_puzzle(self):
        
        self._is_solving = True
        
        if self.board == [1, 2, 3, 4, 5, 6, 7, 8, 0]:
            self._is_solving = False
            self.view.on_solve_complete(True)
            return
    
        solution = a_star(self.board)
        if not solution:
            self._is_solving = False
            self.view.on_solve_complete(False)
            return

        self._solution_states = [s[:] for _, s in solution]
        self._animate_index = 0
        self._solution_length = len(solution)
        self._animate_step()

    # Ejecuta cada paso de la animación de la solución.
    def _animate_step(self):
        
        if not self._is_solving:
            return
        
        if self._animate_index >= len(self._solution_states):
            self._is_solving = False
            self._animation_id = None
            self.view.on_solve_complete(True)
            self.view.status_label.config(text=f"¡Puzzle resuelto automáticamente en {self._solution_length} pasos!")
            return

        state = self._solution_states[self._animate_index]
        self.board = state[:]
        self.view.update_board(self.board)
        self.moves_count += 1
        self.view.update_moves_counter(self.moves_count)
        self._animate_index += 1
        self._animation_id = self.view.root.after(300, self._animate_step)