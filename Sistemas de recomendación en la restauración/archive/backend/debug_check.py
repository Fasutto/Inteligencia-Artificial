import urllib.request
import urllib.error
import time

def fetch(url, timeout=5):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            data = r.read().decode('utf-8')
            print(f"OK: {url}\n{data[:800]}\n---")
            return True
    except Exception as e:
        print(f"ERR: {url} -> {repr(e)}")
        return False

print('Testing HTTP endpoints...')
root_ok = fetch('http://127.0.0.1:8000/')
clients_ok = fetch('http://127.0.0.1:8000/clients')

if not clients_ok:
    print('\nAttempting direct DB query (SQLAlchemy)...')
    try:
        from backend.db import SessionLocal, Client
        s = SessionLocal()
        rows = s.query(Client).limit(20).all()
        print('DB query returned', len(rows), 'rows')
        for c in rows:
            print('-', c.id, c.name, getattr(c, 'preference', None), getattr(c, 'restriction', None))
        s.close()
    except Exception as e:
        print('DB query failed:', repr(e))
