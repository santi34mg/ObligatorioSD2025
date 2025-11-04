# Usar imagen base de Python
FROM python:3.12-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar dependencias e instalarlas
COPY services/users-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar la aplicación
COPY services/users-service/app/ ./app/

# Exponer puerto
EXPOSE 8003

# Comando para levantar la app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
