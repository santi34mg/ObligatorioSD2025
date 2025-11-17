FROM python:3.12-slim

WORKDIR /app

COPY services/collaboration-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/collaboration-service/app/ ./app/
COPY shared/ ./shared/

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
