import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Table, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Archivo SQLite que almacena la base de conocimiento
DB_URL = f"sqlite:///" + os.path.join(os.path.dirname(__file__), "recommender.db")
# Engine SQLAlchemy (check_same_thread=False para permitir uso desde threads diferentes en FastAPI)
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
# Fábrica de sesiones
SessionLocal = sessionmaker(bind=engine)
# Base declarativa para los modelos
Base = declarative_base()


# Tabla intermedia many-to-many entre platos e ingredientes
dish_ingredient = Table(
    'dish_ingredient', Base.metadata,
    Column('dish_id', Integer, ForeignKey('dishes.id')),
    Column('ingredient_id', Integer, ForeignKey('ingredients.id')),
)


class Dish(Base):
    """Modelo de Plato (Dish).

    Campos relevantes:
    - name: nombre del plato
    - method: descripción corta del método de preparación
    - is_vegetarian/is_vegan/is_gluten_free: banderas que ayudan en el razonador
    - ingredients: relación many-to-many con Ingredient
    """
    __tablename__ = 'dishes'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    method = Column(String)
    is_vegetarian = Column(Boolean, default=False)
    is_vegan = Column(Boolean, default=False)
    is_gluten_free = Column(Boolean, default=False)
    ingredients = relationship('Ingredient', secondary=dish_ingredient, back_populates='dishes')


class Ingredient(Base):
    """Modelo de Ingrediente.

    - name: nombre del ingrediente
    - available: booleana que indica si el ingrediente está disponible en cocina
    """
    __tablename__ = 'ingredients'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    available = Column(Boolean, default=True)
    dishes = relationship('Dish', secondary=dish_ingredient, back_populates='ingredients')


class Beverage(Base):
    """Modelo de Bebida (no usado por el razonador principal, pero presente en la KB)."""
    __tablename__ = 'beverages'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    alcoholic = Column(Boolean, default=False)


class Client(Base):
    """Modelo de Cliente.

    - preference: 'Carnívoro'|'Vegetariano'|'Vegano'
    - restriction: texto de restricción principal (ej. 'Sin Gluten')
    - allergies: lista como string separada por comas
    """
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    # preference: 'Carnívoro' | 'Vegetariano' | 'Vegano'
    preference = Column(String, default='Carnívoro')
    # restriction: e.g., 'Ninguna', 'Sin Gluten'
    restriction = Column(String, default='Ninguna')
    # allergies or extra restrictions as comma-separated ingredient names
    allergies = Column(String, default='')


def init_db():
    """Crear tablas en la base de datos si no existen."""
    Base.metadata.create_all(bind=engine)
