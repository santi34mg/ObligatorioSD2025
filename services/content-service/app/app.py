from fastapi import APIRouter, UploadFile, File, Form
from app.storage import upload_to_minio
from app.db import insert_metadata

router = APIRouter()

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    uploader: str = Form(...)
):
    #Recibe un archivo y lo guarda en MinIO.
    #También registra la información en la base de datos
    
    file_url = await upload_to_minio(file)
    metadata = {
        "filename": file.filename,
        "uploader": uploader,
        "url": file_url,
        "content_type": file.content_type
    }
    insert_metadata(metadata)
    return {"message": "Archivo subido correctamente", "url": file_url}
