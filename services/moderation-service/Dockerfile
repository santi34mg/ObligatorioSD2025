FROM python:3.12-slim

WORKDIR /app

COPY services/moderation-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/moderation-service/app/ ./app/
COPY shared/ ./shared/

EXPOSE 8001
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
