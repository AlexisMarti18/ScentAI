#!/usr/bin/env bash
# Levanta ScentAI en http://localhost:8000  (crea el entorno virtual la primera vez)
set -e
cd "$(dirname "$0")"

if [ ! -x .venv/bin/python ]; then
  echo "Creando entorno virtual e instalando dependencias..."
  python3 -m venv .venv
  .venv/bin/python -m pip install -r requirements-app.txt
fi

echo
echo "Abri http://localhost:8000 en el navegador  (Ctrl+C para detener)"
exec .venv/bin/python -m uvicorn app.backend.main:app --host 127.0.0.1 --port 8000
