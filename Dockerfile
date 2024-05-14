FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

ARG MODE=production

# Si el modo es test, se ejecutan los tests, si no, se inicia el servidor gunicorn
ENTRYPOINT ["sh", "-c"]
CMD if [ "$MODE" = "test" ]; then pytest; else gunicorn --bind 0.0.0.0:8000 app:app; fi