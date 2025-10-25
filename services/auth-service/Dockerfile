# Usar imagen base de Python
FROM python:3.12-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar dependencias e instalarlas
COPY services/auth-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar la aplicación
COPY services/auth-service/app/ ./app/

# CRITICAL: Copy shared module (located at project root)
COPY shared/ ./shared/

# Exponer puerto
EXPOSE 8000

# Comando para levantar la app
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]
