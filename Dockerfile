FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

ARG MODE=production
# Define el entrypoint y el comando por defecto
CMD if [ "$MODE" = "test" ]; then python -m unittest discover; else gunicorn --bind 0.0.0.0:8000 app.spread:app; fi

