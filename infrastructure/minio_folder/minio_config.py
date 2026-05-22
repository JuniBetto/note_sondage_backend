# app/config.py
from minio import Minio
import os

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9002")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "note-sondage-user")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "password123")

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False  # True per HTTPS
)

# Crea il bucket se non esiste
BUCKET_NAME = "bucket1"
if not minio_client.bucket_exists(BUCKET_NAME):
    minio_client.make_bucket(BUCKET_NAME)