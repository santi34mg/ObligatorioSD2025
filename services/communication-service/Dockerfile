# Base image
FROM python:3.12-slim

# Working directory
WORKDIR /app

# Copy dependencies and install them
COPY services/communication-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the code
COPY services/communication-service/app/ ./app/

# Copy shared libraries
COPY shared/ ./shared/

# Expose port
EXPOSE 8000

# Comando para ejecutar el servicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
