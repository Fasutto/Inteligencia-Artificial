# Trabajo: BinarySearchTreeProject
# Estudiante: Espinoza Felix Fausto Gabriel
# Fecha: Septiembre 08, 2025

class Node:
    """
    Clase que representa un nodo en el Árbol de Búsqueda Binaria (BST).
    Cada nodo contiene un valor y referencias a sus hijos izquierdo y derecho.
    """
    def __init__(self, value):
        self.value = value  # Valor almacenado en el nodo
        self.left = None    # Hijo izquierdo
        self.right = None   # Hijo derecho

class BinarySearchTree:
    """
    Clase que representa el Árbol de Búsqueda Binaria (BST).
    Permite insertar valores y mostrar el árbol en orden.
    """
    def __init__(self):
        self.root = None  # Nodo raíz del árbol

    def insert(self, value):
        """
        Inserta un nuevo nodo con el valor dado en el BST.
        Si el árbol está vacío, el nuevo nodo se convierte en la raíz.
        Si no, se busca la posición correcta de forma recursiva.
        No se permiten valores duplicados.
        Args:
            value (int): Valor a insertar en el árbol.
        """
        if self.root is None:
            self.root = Node(value)
        else:
            self._insert_recursive(self.root, value)

    def _insert_recursive(self, current, value):
        """
        Método auxiliar recursivo para insertar un valor en el árbol.
        Args:
            current (Node): Nodo actual en el recorrido.
            value (int): Valor a insertar.
        """
        if value < current.value:
            if current.left is None:
                current.left = Node(value)
            else:
                self._insert_recursive(current.left, value)
        elif value > current.value:
            if current.right is None:
                current.right = Node(value)
            else:
                self._insert_recursive(current.right, value)
        # Si el valor es igual, no se inserta (no se permiten duplicados)

    def print_tree(self):
        """
        Imprime el árbol en orden (in-order), mostrando los valores de menor a mayor.
        Utiliza recorrido in-order para mostrar la estructura ordenada.
        """
        self._print_in_order(self.root)
        print()

    def _print_in_order(self, node):
        """
        Método auxiliar para imprimir el árbol en orden.
        Args:
            node (Node): Nodo actual en el recorrido.
        """
        if node:
            self._print_in_order(node.left)
            print(node.value, end=' ')
            self._print_in_order(node.right)

if __name__ == "__main__":
    # Ejemplo de uso del Árbol de Búsqueda Binaria
    bst = BinarySearchTree()
    
    # Datos de muestra para probar el BST
    sample_values = [50, 30, 70, 20, 40, 60, 80]
    for val in sample_values:
        bst.insert(val)
    print("Recorrido in-order del BST:")
    bst.print_tree()
