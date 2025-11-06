from recommender.model import Recommender, cargar_base_conocimiento


def test_recommender_scenarios():
    platos, ingredientes = cargar_base_conocimiento()
    reco = Recommender(platos, ingredientes)

    # Escenario 1: Carnívoro, sin restricciones
    r1 = reco.inferir_gustos(0, 0)
    assert any(x['Plato'] == 'Tacos de Carne' and x['Probabilidad'] > 0.5 for x in r1)

    # Escenario 2: Vegetariano, sin gluten
    r2 = reco.inferir_gustos(1, 1)
    assert any(x['Plato'] == 'Tazón de Burrito Vegetariano' and x['Probabilidad'] > 0.5 for x in r2)

    # Escenario 3: Carnívoro con restricción sin gluten
    r3 = reco.inferir_gustos(0, 1)
    assert len(r3) == 3

    # Escenario 4: Simular ingrediente agotado (Pollo)
    reco.actualizar_ingrediente('Pollo', False)
    r4 = reco.inferir_gustos(0, 0)
    ensalada = [x for x in r4 if x['Plato'] == 'Ensalada César'][0]
    assert ensalada['Disponible'] is False

    # Escenario 5: Todos los ingredientes disponibles
    platos2, ingredientes2 = cargar_base_conocimiento()
    reco2 = Recommender(platos2, ingredientes2)
    r5 = reco2.inferir_gustos(1, 0)
    assert all('Disponible' in x for x in r5)
