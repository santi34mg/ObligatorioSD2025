from minio import Minio
import io, uuid, os

# Conexión al servidor MinIO (desde docker-compose)
client = Minio(
    os.getenv("MINIO_ENDPOINT", "minio:9000"),
    access_key=os.getenv("MINIO_ROOT_USER", "minioadmin"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD", "minioadmin"),
    secure=False
)

BUCKET = "umshare"

def ensure_bucket():
    if not client.bucket_exists(BUCKET):
        client.make_bucket(BUCKET)

async def upload_to_minio(file, content: bytes = None):
    """
    Upload file to MinIO.
    If content is provided, use it; otherwise read from file.
    """
    ensure_bucket()
    filename = f"{uuid.uuid4()}_{file.filename}"
    
    if content is None:
        content = await file.read()
    
    client.put_object(
        BUCKET,
        filename,
        io.BytesIO(content),
        len(content),
        content_type=file.content_type
    )
    return f"http://localhost:9000/{BUCKET}/{filename}", len(content)
