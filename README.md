# Documentación de la Aplicación Flask
Este documento explica cómo usar Docker para ejecutar una aplicación Flask en producción y cómo ejecutar tests automatizados utilizando el mismo entorno Docker.

## Pre-requisitos
Antes de comenzar, asegúrate de tener Docker instalado en tu sistema.

## Estructura de Archivos

```bash
.
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── test_main.py
├── Dockerfile
├── requirements.txt
├── .gitignore
├── README.md
```

## Dockerfile
Aquí está el contenido del archivo Dockerfile:
```Dockerfile
# Usa una imagen oficial de Python como imagen base
FROM python:3.10-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia el contenido del directorio actual en el contenedor en /app
COPY . /app

# Instala los paquetes necesarios especificados en requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto 8000 al mundo exterior
EXPOSE 8000

# Define una variable de entorno para controlar el modo de operación
ARG MODE=production

# Define el entrypoint y el comando por defecto
ENTRYPOINT ["sh", "-c"]
CMD if [ "$MODE" = "test" ]; then pytest; else gunicorn --bind 0.0.0.0:8000 app:app; fi
```

## Construcción y Ejecución de la Imagen Docker
Para ejecutar la aplicación:
```bash
docker build -t mi-app-flask .
docker run -p 8000:8000 mi-app-flask
```

Para ejecutar los tests:
```bash
docker build --build-arg MODE=test -t mi-app-flask-test .
docker run mi-app-flask-test
```

## Modo de Pruebas
Cuando se construye la imagen Docker para tests, asegúrate de especificar el argumento de construcción MODE como test. Esto cambiará el comando que se ejecuta al iniciar el contenedor para que ejecute pytest en lugar de iniciar la aplicación Flask.