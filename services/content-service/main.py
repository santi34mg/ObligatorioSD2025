from fastapi import FastAPI
from app.app import router as content_router

app = FastAPI(title="Content Service")

# Registrar las rutas del servicio
app.include_router(content_router, prefix="/content", tags=["content"])
