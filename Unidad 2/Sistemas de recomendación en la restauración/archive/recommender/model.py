from typing import Dict, Tuple, List
import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Table, ForeignKey, text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from backend.db import SessionLocal, init_db, Dish, Ingredient
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "recommender.db")
DB_URL = f"sqlite:///{DB_PATH}"

# allow multi-thread access in apps (important)
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# association table
dish_ingredient = Table(
    'dish_ingredient', Base.metadata,
    Column('dish_id', Integer, ForeignKey('dishes.id')),
    Column('ingredient_id', Integer, ForeignKey('ingredients.id'))
)

class Dish(Base):
    __tablename__ = 'dishes'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    method = Column(String)
    is_vegetarian = Column(Boolean, default=False)
    is_vegan = Column(Boolean, default=False)
    is_gluten_free = Column(Boolean, default=False)
    ingredients = relationship('Ingredient', secondary=dish_ingredient, back_populates='dishes')

class Ingredient(Base):
    __tablename__ = 'ingredients'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    available = Column(Boolean, default=True)
    dishes = relationship('Dish', secondary=dish_ingredient, back_populates='ingredients')

def init_db():
    Base.metadata.create_all(bind=engine)

def cargar_base_conocimiento() -> Tuple[Dict, Dict]:
    ingredientes_disponibles = {
        "Lechuga": True, "Tomate": True, "Queso": True, "Pollo": True,
        "Carne de res": True, "Tortilla de maíz": True, "Frijoles": True,
        "Aguacate": True, "Pan": True,
    }

    platos = {
        "Ensalada César": {
            "ingredientes": ["Lechuga", "Queso", "Pollo", "Pan"],
            "es_vegetariano": False, "sin_gluten": False,
        },
        "Tacos de Carne": {
            "ingredientes": ["Carne de res", "Tortilla de maíz", "Aguacate", "Tomate"],
            "es_vegetariano": False, "sin_gluten": True,
        },
        "Tazón de Burrito Vegetariano": {
            "ingredientes": ["Lechuga", "Tomate", "Frijoles", "Aguacate", "Queso"],
            "es_vegetariano": True, "sin_gluten": True,
        }
    }
    return platos, ingredientes_disponibles


class Recommender:
    def __init__(self, platos: Dict, ingredientes: Dict):
        self.platos = platos
        self.ingredientes = ingredientes
        self.prior_preferencia = {0: 0.5, 1: 0.5}
        self.prior_restriccion = {0: 0.8, 1: 0.2}

        self.condicionales = {
            "Ensalada César": [[0.6, 0.01], [0.7, 0.01]],
            "Tacos de Carne": [[0.9, 0.8], [0.01, 0.01]],
            "Tazón de Burrito Vegetariano": [[0.2, 0.5], [0.9, 0.95]],
        }

    def inferir_gustos(self, preferencia: int, restriccion: int) -> List[Dict]:
        resultados = []
        for nombre, info in self.platos.items():
            tabla = self.condicionales.get(nombre)
            prob_gusta = tabla[preferencia][restriccion]
            disponible = all(self.ingredientes.get(ing, False) for ing in info["ingredientes"])
            resultados.append({"Plato": nombre, "Probabilidad": prob_gusta, "Disponible": disponible})

        resultados.sort(key=lambda x: x["Probabilidad"], reverse=True)
        return resultados

    def actualizar_ingrediente(self, ingrediente: str, disponible: bool):
        if ingrediente not in self.ingredientes:
            raise KeyError(f"Ingrediente desconocido: {ingrediente}")
        self.ingredientes[ingrediente] = disponible

def seed():
    init_db()
    db = SessionLocal()
    # crear ingredientes si no existen, luego platos y bebidas
    # db.add(Ingredient(name='Tomate')) ...
    db.commit()

init_db()
db = SessionLocal()

# crear ingrediente
pollo = Ingredient(name='Pollo', available=True)
db.add(pollo)
db.commit()

# crear plato y vincular ingrediente
ensalada = Dish(name='Ensalada César', method='mezclar', is_vegetarian=False)
ensalada.ingredients.append(pollo)
db.add(ensalada)
db.commit()

# consultar
d = db.query(Dish).filter_by(name='Ensalada César').first()
print([i.name for i in d.ingredients])

db.close()

with engine.connect() as conn:
    conn.execute(text("PRAGMA journal_mode=WAL"))

# Python sqlite3 backup
src = sqlite3.connect('backend/recommender.db')
dst = sqlite3.connect('backup.db')
src.backup(dst)
dst.close()
src.close()
