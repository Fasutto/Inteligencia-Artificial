from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
from .db import init_db, SessionLocal, Ingredient, Dish, Beverage
from .reasoner import Reasoner
from .db import Client
from typing import Optional

app = FastAPI(title='Recommender API')

# Mount static frontend
# Monta la carpeta estática para servir el frontend (index.html + main.js)
app.mount('/static', StaticFiles(directory='backend/static'), name='static')


@app.get('/')
def root_index():
    return FileResponse('backend/static/index.html')


class RecommendationRequest(BaseModel):
    preference: str  # 'Carnívoro'|'Vegetariano'|'Vegano'
    restriction: str  # 'Ninguna'|'Sin Gluten' etc.


class ClientCreate(BaseModel):
    name: str
    preference: str
    restriction: str
    allergies: Optional[str] = ''


class IngredientUpdate(BaseModel):
    name: str
    available: bool


@app.on_event('startup')
def startup_event():
    # Inicializa la base de datos al arrancar la aplicación (crea tablas si faltan)
    init_db()


@app.get('/ingredients', response_model=List[str])
def list_ingredients():
    db = SessionLocal()
    items = db.query(Ingredient).all()
    # Devuelve una lista legible de ingredientes con su estado
    return [i.name + (" (disponible)" if i.available else " (agotado)") for i in items]


@app.post('/ingredient')
def update_ingredient(u: IngredientUpdate):
    db = SessionLocal()
    ing = db.query(Ingredient).filter(Ingredient.name == u.name).first()
    if not ing:
        raise HTTPException(status_code=404, detail='Ingrediente no encontrado')
    ing.available = u.available
    db.add(ing)
    db.commit()
    # Permite marcar un ingrediente como disponible/agotado
    return {'ok': True}


@app.post('/recommend')
def recommend(req: RecommendationRequest):
    db = SessionLocal()
    reasoner = Reasoner(db)
    results = reasoner.recommend(req.preference, req.restriction)
    return results


@app.get('/clients')
def list_clients():
    db = SessionLocal()
    # Devuelve clientes con los campos necesarios para la UI
    return [{'id': c.id, 'name': c.name, 'preference': c.preference, 'restriction': c.restriction, 'allergies': c.allergies} for c in db.query(Client).all()]


@app.get('/clients/{client_id}')
def get_client(client_id: int):
    db = SessionLocal()
    c = db.query(Client).filter(Client.id == client_id).first()
    if not c:
        raise HTTPException(status_code=404, detail='Cliente no encontrado')
    # Devuelve los datos del cliente solicitado
    return {'id': c.id, 'name': c.name, 'preference': c.preference, 'restriction': c.restriction, 'allergies': c.allergies}


@app.post('/recommend/client/{client_id}')
def recommend_for_client(client_id: int):
    db = SessionLocal()
    c = db.query(Client).filter(Client.id == client_id).first()
    if not c:
        raise HTTPException(status_code=404, detail='Cliente no encontrado')
    reasoner = Reasoner(db)
    results = reasoner.recommend(c.preference, c.restriction)
    # Aplicar filtro de alergias: si el cliente tiene alergias, marcamos como no disponibles los platos que las contienen
    allergies = [a.strip().lower() for a in (c.allergies or '').split(',') if a.strip()]
    if allergies:
        filtered = []
        for r in results:
            ing_lower = [i.lower() for i in r['ingredients']]
            if any(allg in ing_lower for allg in allergies):
                r['available'] = False
            filtered.append(r)
        results = filtered
    return results


@app.post('/clients')
def create_client(c: ClientCreate):
    db = SessionLocal()
    # check duplicate name
    existing = db.query(Client).filter(Client.name == c.name).first()
    if existing:
        raise HTTPException(status_code=400, detail='Cliente con ese nombre ya existe')
    newc = Client(name=c.name, preference=c.preference, restriction=c.restriction, allergies=c.allergies)
    db.add(newc)
    db.commit()
    db.refresh(newc)
    # Crea un cliente nuevo y devuelve el objeto para que la UI lo pueda seleccionar
    return {'id': newc.id, 'name': newc.name, 'preference': newc.preference, 'restriction': newc.restriction, 'allergies': newc.allergies}
