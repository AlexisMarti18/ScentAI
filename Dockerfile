# Imagen para usar la app (no incluye dataset ni pipeline).
#   docker build -t scentai .
#   docker run --rm -p 8000:8000 scentai      ->  http://localhost:8000
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements-app.txt .
RUN pip install --no-cache-dir -r requirements-app.txt

COPY perfume_gender ./perfume_gender
COPY app ./app
COPY models ./models
COPY reports ./reports

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
