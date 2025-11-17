FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY services/websocket-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY services/websocket-service/main.py .
COPY shared/ ./shared/

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
