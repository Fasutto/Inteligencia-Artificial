Param(
    [switch]$Background,
    [int]$Port = 8000
)

if (-not (Test-Path -Path .\venv\Scripts\python.exe)) {
    python -m venv venv
}

.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt

.\venv\Scripts\python.exe -c "from backend.db import init_db; init_db(); print('DB ok')"

if ($Background) {
    Start-Process -FilePath .\venv\Scripts\python.exe -ArgumentList "-m","uvicorn","backend.api:app","--host","127.0.0.1","--port",$Port -WindowStyle Hidden
    Write-Output "Server started on http://127.0.0.1:$Port/"
} else {
    & .\venv\Scripts\python.exe -m uvicorn backend.api:app --host 127.0.0.1 --port $Port
}
