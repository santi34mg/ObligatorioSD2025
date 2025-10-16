# Usar imagen base de Python
FROM python:3.12-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar dependencias e instalarlas
COPY services/auth-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar la aplicación
COPY services/auth-service/main.py .
COPY services/auth-service/app/ ./app/
COPY shared/ ./shared/

# Exponer puerto
EXPOSE 8000

# Comando para levantar la app
CMD ["python", "main.py"]
