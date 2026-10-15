@echo off
rem Levanta ScentAI en http://localhost:8000  (crea el entorno virtual la primera vez)
cd /d "%~dp0"

if not exist .venv\Scripts\python.exe (
    echo Creando entorno virtual e instalando dependencias...
    python -m venv .venv || goto :error
    .venv\Scripts\python.exe -m pip install -r requirements.txt || goto :error
)

echo.
echo Abri http://localhost:8000 en el navegador  (Ctrl+C para detener)
.venv\Scripts\python.exe -m uvicorn app.backend.main:app --host 127.0.0.1 --port 8000
goto :eof

:error
echo No se pudo preparar el entorno. Verifica que Python 3.12+ este instalado.
exit /b 1
