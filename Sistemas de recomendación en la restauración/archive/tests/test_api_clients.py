from fastapi.testclient import TestClient
from backend.api import app
from backend.db import SessionLocal, Client
import time


def test_create_client_and_recommend():
    client = TestClient(app)
    # unique name to avoid collisions
    name = f"pytest_user_{int(time.time())}"
    payload = {"name": name, "preference": "Carnívoro", "restriction": "Ninguna", "allergies": ""}

    # create client
    r = client.post('/clients', json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data['name'] == name
    cid = data['id']

    # request recommendations for this client
    r2 = client.post(f'/recommend/client/{cid}', json={})
    assert r2.status_code == 200, r2.text
    results = r2.json()
    assert isinstance(results, list)
    assert len(results) > 0

    # cleanup: remove the created client from DB
    db = SessionLocal()
    c = db.query(Client).filter(Client.id == cid).first()
    if c:
        db.delete(c)
        db.commit()
    db.close()
