#Implementación del algoritmo A* para resolver el Puzzle 8.
# Autor: Espinoza Felix Fausto Gabriel.
# Fecha: 2025-8-31.
import heapq

class PuzzleState:

    # Inicializa un estado del puzzle.
    def __init__(self, board, parent=None, move=None, cost=0):
        self.board = board[:]               # Copia defensiva del tablero.
        self.parent = parent                # Estado anterior.
        self.move = move                    # Movimiento que llevó a este estado.
        self.cost = cost                    # Costo acumulado (g).
        self.blank = self.board.index(0)    # Posición del espacio en blanco.

    # Verifica si el estado actual es el objetivo.
    def is_goal(self):
        return self.board == [1, 2, 3, 4, 5, 6, 7, 8, 0]

    # Genera todos los estados vecinos moviendo el espacio en blanco.
    def get_neighbors(self):
        
        neighbors = []
        moves = {"arriba": -3, "abajo": 3, "izquierda": -1, "derecha": 1}
        
        for move, step in moves.items():
            new_blank = self.blank + step
            
            # Validaciones de límites y bordes del tablero.
            if new_blank < 0 or new_blank >= 9:
                continue
            if self.blank % 3 == 0 and move == "izquierda":
                continue
            if self.blank % 3 == 2 and move == "derecha":
                continue
            
            new_board = self.board[:]                                                                   # Copia del tablero actual.
            new_board[self.blank], new_board[new_blank] = new_board[new_blank], new_board[self.blank]   # Intercambia el espacio en blanco con la ficha adyacente.
            neighbors.append(PuzzleState(new_board, self, move, self.cost + 1))                         # Crea un nuevo estado vecino y lo añade a la lista.

        return neighbors

    # Calcula la heurística usando distancia de Manhattan.
    def heuristic(self):
        distance = 0
        for i, value in enumerate(self.board):
            if value == 0:
                continue
            target_x, target_y = (value - 1) % 3, (value - 1) // 3  #Posición objetivo.
            current_x, current_y = i % 3, i // 3                    #Posición actual.
            distance += abs(target_x - current_x) + abs(target_y - current_y)
            
        return distance

    # Comparación basada en f = g + h para la cola de prioridad (f = CTE, g = CR, h = ECR).
    def __lt__(self, other): 
        return (self.cost + self.heuristic()) < (other.cost + other.heuristic())

# Algoritmo A* para encontrar la solución del puzzle.
def a_star(start_board):
    start_state = PuzzleState(start_board)
    frontier = []
    counter = 0
    start_f = start_state.cost + start_state.heuristic()
    heapq.heappush(frontier, (start_f, counter, start_state))
    best_cost = {tuple(start_state.board): 0}
        
    while frontier:
        _, _, current = heapq.heappop(frontier)

        if current.is_goal():
            return reconstruct_path(current)
            
        for neighbor in current.get_neighbors():
            key = tuple(neighbor.board)
            g = neighbor.cost
            if key not in best_cost or g < best_cost[key]:
                best_cost[key] = g
                counter += 1
                f = g + neighbor.heuristic()
                heapq.heappush(frontier, (f, counter, neighbor))

    return None

# Reconstruye la ruta desde el estado objetivo hasta el inicial.
def reconstruct_path(state):
    path = []
    while state.parent:
        path.append((state.move, state.board[:]))
        state = state.parent
    path.reverse()
    return path