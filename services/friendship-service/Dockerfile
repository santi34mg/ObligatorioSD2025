# Use Python base image
FROM python:3.12-slim

# Create working directory
WORKDIR /app

# Copy dependencies and install them
COPY services/friendship-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY services/friendship-service/app/ ./app/

# Copy shared module
COPY shared/ ./shared/

# Expose port
EXPOSE 8001

# Command to run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
