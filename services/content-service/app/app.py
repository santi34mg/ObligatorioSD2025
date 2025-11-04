from fastapi import UploadFile, File, Form
from app.storage import upload_to_minio
from app.db import insert_metadata

from fastapi import FastAPI

app = FastAPI(title="Content Service")

@app.post("/content/upload")
async def upload_file(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(...),
    uploader: str = Form(default="anonymous")
):
    """
    Recibe un archivo y lo guarda en MinIO.
    También registra la información en la base de datos con título y descripción.
    """
    
    file_url = await upload_to_minio(file)
    metadata = {
        "filename": file.filename,
        "title": title,
        "description": description,
        "uploader": uploader,
        "url": file_url,
        "content_type": file.content_type
    }
    insert_metadata(metadata)
    return {
        "message": "Documento subido exitosamente", 
        "url": file_url,
        "title": title
    }
