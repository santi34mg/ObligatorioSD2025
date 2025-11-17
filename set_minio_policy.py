#!/usr/bin/env python3
"""
Script to set public read policy on MinIO bucket
"""
from minio import Minio
import json
import os

# MinIO configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER", "minioadmin")
MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
BUCKET = "umshare"

# Create MinIO client
client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=False
)

# Check if bucket exists
if not client.bucket_exists(BUCKET):
    print(f"Bucket {BUCKET} does not exist. Creating it...")
    client.make_bucket(BUCKET)
    print(f"Bucket {BUCKET} created.")

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

try:
    client.set_bucket_policy(BUCKET, json.dumps(policy))
    print(f"✅ Public read policy set successfully for bucket: {BUCKET}")
    print(f"Files in {BUCKET} are now publicly accessible")
except Exception as e:
    print(f"❌ Error setting bucket policy: {e}")
    exit(1)

# Verify the policy
try:
    current_policy = client.get_bucket_policy(BUCKET)
    print(f"\n📋 Current bucket policy:")
    print(json.dumps(json.loads(current_policy), indent=2))
except Exception as e:
    print(f"Warning: Could not retrieve bucket policy: {e}")
