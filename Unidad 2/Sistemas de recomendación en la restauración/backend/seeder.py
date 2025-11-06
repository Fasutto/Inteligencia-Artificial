from .db import init_db, SessionLocal, Dish, Ingredient, Beverage, Client


def seed():
    # Inicializa la base de datos.
    init_db()
    db = SessionLocal()

    # --- Ingredients (sample set) ---
    # Lista de ingredientes que usaremos para poblar la KB de ejemplo
    ing_names = [
        'Lechuga', 'Tomate', 'Queso', 'Pollo', 'Carne de res', 'Tortilla de maíz', 'Frijoles', 'Aguacate', 'Pan',
        'Arroz', 'Pasta', 'Cebolla', 'Ajo', 'Champiñones', 'Leche', 'Huevos', 'Tofu', 'Salmón', 'Limón', 'Azúcar',
        'Patata', 'Aceitunas', 'Garbanzos', 'Quinoa', 'Fideos', 'Mariscos', 'Berenjena', 'Zanahoria', 'Fruta', 'Aceite'
    ]

    ingredients = {}
    for name in ing_names:
        ing = db.query(Ingredient).filter(Ingredient.name == name).first()
        if not ing:
            ing = Ingredient(name=name, available=True)
            db.add(ing)
        ingredients[name] = ing

    db.commit()

    # --- Dishes (platos) ---
    # Cada tupla: (nombre, metodo, [ingredientes], is_vegetarian, is_vegan, is_gluten_free)
    dishes = [
        ('Ensalada César', 'mezclar y servir', ['Lechuga', 'Queso', 'Pollo', 'Pan'], False, False, False),
        ('Tacos de Carne', 'armar tacos', ['Carne de res', 'Tortilla de maíz', 'Aguacate', 'Tomate'], False, False, True),
        ('Tazón de Burrito Vegetariano', 'armar tazón', ['Lechuga', 'Tomate', 'Frijoles', 'Aguacate', 'Queso'], True, False, True),
        ('Pasta Alfredo', 'hervir y mezclar', ['Pasta', 'Queso', 'Leche', 'Ajo'], False, False, False),
        ('Arroz con Pollo', 'cocinar guiso', ['Arroz', 'Pollo', 'Cebolla', 'Ajo'], False, False, True),
        ('Salmón a la plancha', 'asar al punto', ['Salmón', 'Limón', 'Ajo'], False, False, True),
        ('Tortilla Española', 'freír', ['Huevos', 'Cebolla', 'Patata'], False, False, False),
        ('Ensalada Mediterránea', 'mezclar', ['Lechuga', 'Tomate', 'Aceitunas', 'Queso'], True, False, True),
        ('Sopa de Champiñones', 'hervir', ['Champiñones', 'Cebolla', 'Ajo', 'Leche'], True, False, True),
        ('Burrito de Carne', 'armar', ['Tortilla de maíz', 'Carne de res', 'Frijoles', 'Arroz'], False, False, False),
        ('Hamburguesa clásica', 'asar y montar', ['Pan', 'Carne de res', 'Queso', 'Tomate'], False, False, False),
        ('Wrap de Pollo', 'montar', ['Pan', 'Pollo', 'Lechuga', 'Tomate'], False, False, False),
        ('Enchiladas', 'hornear', ['Tortilla de maíz', 'Carne de res', 'Queso', 'Salsa'], False, False, False),
        ('Curry de Garbanzos', 'cocinar', ['Garbanzos', 'Tomate', 'Cebolla', 'Ajo'], True, False, True),
        ('Poke Bowl', 'montar', ['Arroz', 'Salmón', 'Aguacate', 'Tomate'], False, False, True),
        ('Pizza Margarita', 'hornear', ['Pan', 'Queso', 'Tomate', 'Ajo'], True, False, False),
        ('Falafel', 'freír', ['Garbanzos', 'Cebolla', 'Ajo', 'Aceite'], True, False, True),
        ('Guiso de Res', 'cocinar lento', ['Carne de res', 'Cebolla', 'Ajo', 'Zanahoria'], False, False, True),
        ('Tofu salteado', 'saltear', ['Tofu', 'Champiñones', 'Ajo', 'Cebolla'], True, True, True),
        ('Ensalada de Quinoa', 'mezclar', ['Quinoa', 'Tomate', 'Aguacate', 'Lechuga'], True, True, True),
        ('Sopa de Pollo', 'hervir', ['Pollo', 'Zanahoria', 'Cebolla', 'Fideos'], False, False, False),
        ('Tostadas de Aguacate', 'montar', ['Pan', 'Aguacate', 'Tomate', 'Limón'], True, True, True),
        ('Quesadillas', 'freír', ['Tortilla de maíz', 'Queso', 'Pollo'], False, False, False),
        ('Ramen', 'cocinar', ['Fideos', 'Pollo', 'Cebolla', 'Huevo'], False, False, False),
        ('Ensalada de Frutas', 'mezclar', ['Limón', 'Azúcar', 'Fruta'], True, True, True),
        ('Pollo al Ajillo', 'saltear', ['Pollo', 'Ajo', 'Aceite'], False, False, True),
        ('Berenjenas al Horno', 'hornear', ['Berenjena', 'Queso', 'Tomate'], True, False, True),
        ('Cazuela de Mariscos', 'cocinar', ['Salmón', 'Mariscos', 'Tomate', 'Ajo'], False, False, True),
        ('Ensalada César Vegana', 'mezclar', ['Lechuga', 'Tofu', 'Aguacate'], True, True, True),
        ('Chili con Carne', 'cocinar', ['Carne de res', 'Frijoles', 'Tomate', 'Cebolla'], False, False, True),
    ]

    for name, method, ings, is_veg, is_vegan, is_gf in dishes:
        d = db.query(Dish).filter(Dish.name == name).first()
        if not d:
            d = Dish(name=name, method=method, is_vegetarian=is_veg, is_vegan=is_vegan, is_gluten_free=is_gf)
            db.add(d)
            for ing_name in ings:
                ing = db.query(Ingredient).filter(Ingredient.name == ing_name).first()
                if ing:
                    d.ingredients.append(ing)

    # Beverages (10)
    # Lista de bebidas de ejemplo (alcohólicas indicadas mediante bandera)
    bev_names = ['Agua', 'Jugo de Naranja', 'Limonada', 'Cerveza', 'Vino tinto', 'Vino blanco', 'Café', 'Té', 'Refresco', 'Agua con gas']
    for b in bev_names:
        bev = db.query(Beverage).filter(Beverage.name == b).first()
        if not bev:
            bev = Beverage(name=b, alcoholic=(b in ['Cerveza', 'Vino tinto', 'Vino blanco']))
            db.add(bev)

    # Clients
    # Clientes de ejemplo para probar la UI y las recomendaciones
    clients = [
        ('Ana', 'Vegetariano', 'Ninguna', ''),
        ('Luis', 'Carnívoro', 'Ninguna', ''),
        ('María', 'Vegano', 'Sin Gluten', ''),
        ('Carlos', 'Carnívoro', 'Sin Gluten', 'Queso'),
        ('Sofía', 'Vegetariano', 'Ninguna', 'Aguacate')
    ]
    for name, pref, restr, allergies in clients:
        c = db.query(Client).filter(Client.name == name).first()
        if not c:
            c = Client(name=name, preference=pref, restriction=restr, allergies=allergies)
            db.add(c)

    db.commit()
    # Commit final (asegura que todos los inserts se guarden)
    db.commit()
