@echo off
if not exist venv\Scripts\python.exe (
    python -m venv venv
)
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install -r requirements.txt
venv\Scripts\python.exe -c "from backend.db import init_db; init_db()"
start "Recommender" venv\Scripts\python.exe -m uvicorn backend.api:app --host 127.0.0.1 --port 8000
echo Server started on http://127.0.0.1:8000/
pause
