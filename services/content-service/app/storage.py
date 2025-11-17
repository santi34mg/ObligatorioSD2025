from minio import Minio
import io, uuid, os
import json

# Connection to MinIO server (from docker-compose)
client = Minio(
    os.getenv("MINIO_ENDPOINT", "minio:9000"),
    access_key=os.getenv("MINIO_ROOT_USER", "minioadmin"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD", "minioadmin"),
    secure=False
)

BUCKET = "umshare"

def ensure_bucket():
    """
    Ensure the bucket exists and has public read policy.
    Note: This is also set during app startup (init_minio.py) to ensure
    the policy is always applied, even after Docker restarts or redeployments.
    This function serves as a fallback when uploading files.
    """
    if not client.bucket_exists(BUCKET):
        client.make_bucket(BUCKET)
    
    # Set public read policy for the bucket
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{BUCKET}/*"]
            }
        ]
    }
    
    try:
        client.set_bucket_policy(BUCKET, json.dumps(policy))
        print(f"Bucket policy set for {BUCKET}")
    except Exception as e:
        print(f"Warning: Could not set bucket policy: {e}")

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
