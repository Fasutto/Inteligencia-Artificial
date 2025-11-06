"""CLI runner para el recomendador.
Permite ejecutar recomendaciones desde la terminal sin Streamlit.
"""
import argparse
from recommender.model import cargar_base_conocimiento, Recommender


def parse_args():
    p = argparse.ArgumentParser(description="Recomendador CLI")
    p.add_argument('--preferencia', choices=['Carnívoro', 'Vegetariano'], default='Carnívoro')
    p.add_argument('--restriccion', choices=['Ninguna', 'Sin Gluten'], default='Ninguna')
    p.add_argument('--sim-pollo-agotado', action='store_true', help='Simular pollo agotado')
    return p.parse_args()


def main():
    args = parse_args()
    map_pref = {'Carnívoro': 0, 'Vegetariano': 1}
    map_res = {'Ninguna': 0, 'Sin Gluten': 1}

    platos, ingredientes = cargar_base_conocimiento()
    reco = Recommender(platos, ingredientes)
    if args.sim_pollo_agotado:
        reco.actualizar_ingrediente('Pollo', False)

    resultados = reco.inferir_gustos(map_pref[args.preferencia], map_res[args.restriccion])

    print('\nRecomendaciones:')
    for r in resultados:
        available = 'Disponible' if r['Disponible'] else 'No disponible'
        print(f"- {r['Plato']} : {r['Probabilidad']:.2%} - {available}")


if __name__ == '__main__':
    main()
