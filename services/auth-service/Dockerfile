# Use Python base image
FROM python:3.12-slim

# Create working directory
WORKDIR /app

# Copy dependencies and install them
COPY services/auth-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY services/auth-service/app/ ./app/

# CRITICAL: Copy shared module (located at project root)
COPY shared/ ./shared/

# Expose port
EXPOSE 8000

# Command to run the app
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]
