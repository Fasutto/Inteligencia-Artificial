from typing import List
from .db import SessionLocal, Dish, Ingredient, Beverage


class Reasoner:
    """Reasoner simple que usa atributos de platos y disponibilidad para puntuar recomendaciones.

    Las puntuaciones se calculan con una heurística ligera:
    - Partimos de una puntuación base (0.5).
    - Aplicamos un 'bonus' si el plato concuerda con la preferencia del cliente (vegetariano/vegano/carnívoro).
    - Aplicamos penalizaciones si el plato viola una restricción (p. ej. no es sin gluten cuando el cliente exige "Sin Gluten").
    - Si alguno de los ingredientes está marcado como no disponible, el plato recibe una penalización adicional y se marca como no disponible.
    """

    def __init__(self, db):
        # db puede ser la fábrica SessionLocal o una sesión ya creada
        if callable(db):
            self.db = db()
        else:
            self.db = db

    def recommend(self, preference: str, restriction: str):
        """Devuelve una lista de platos ordenada por score.

        Args:
            preference: 'Carnívoro'|'Vegetariano'|'Vegano'
            restriction: cadena con la restricción principal (ej. 'Ninguna' o 'Sin Gluten')

        Cada resultado es un dict con: 'dish', 'score', 'available', 'ingredients'.
        """

        # Recuperar platos e ingredientes y su disponibilidad
        dishes = self.db.query(Dish).all()
        ingredients = {i.name: i.available for i in self.db.query(Ingredient).all()}

        results = []
        for d in dishes:
            # puntuación base
            score = 0.5

            # Bonus por preferencia del cliente
            if preference == 'Vegetariano' and d.is_vegetarian:
                score += 0.3
            if preference == 'Vegano' and d.is_vegan:
                score += 0.35
            if preference == 'Carnívoro' and (not d.is_vegetarian):
                score += 0.2

            # Penalización por restricciones (p. ej. "Sin Gluten")
            if restriction == 'Sin Gluten' and not d.is_gluten_free:
                score -= 0.4

            # Comprobar si todos los ingredientes necesarios están disponibles
            ing_names = [ing.name for ing in d.ingredients]
            available = all(ingredients.get(n, False) for n in ing_names)
            if not available:
                # Si falta algún ingrediente, penalizamos y marcamos como no disponible
                score -= 0.5

            results.append({'dish': d.name, 'score': max(0, score), 'available': available, 'ingredients': ing_names})

        # Orden descendente por score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

