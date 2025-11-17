#!/usr/bin/env python3
"""
Initialize MinIO bucket with public read policy
This script runs on application startup to ensure bucket configuration
"""
from minio import Minio
import json
import os

def init_minio():
    """Initialize MinIO bucket with public read policy"""
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
    MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER", "minioadmin")
    MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
    BUCKET = "umshare"
    
    try:
        # Create MinIO client
        client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ROOT_USER,
            secret_key=MINIO_ROOT_PASSWORD,
            secure=False
        )
        
        # Ensure bucket exists
        if not client.bucket_exists(BUCKET):
            print(f"Creating bucket: {BUCKET}")
            client.make_bucket(BUCKET)
            print(f"Bucket {BUCKET} created")
        else:
            print(f"Bucket {BUCKET} already exists")
        
        # Set public read policy
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
        
        client.set_bucket_policy(BUCKET, json.dumps(policy))
        print(f"Public read policy set for bucket: {BUCKET}")
        
    except Exception as e:
        print(f"Warning: MinIO initialization error: {e}")
        print("The service will continue, but file access may be restricted")

if __name__ == "__main__":
    init_minio()
