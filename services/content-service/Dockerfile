# Usar imagen base de Python
FROM python:3.12-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar dependencias e instalarlas
COPY services/content-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar la aplicación
COPY services/content-service/app/ ./app/

COPY shared/ ./shared/

# Exponer puerto
EXPOSE 8000
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]
