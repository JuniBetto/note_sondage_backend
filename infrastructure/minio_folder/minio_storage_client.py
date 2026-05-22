import asyncio
import io
import os
from datetime import timedelta
from typing import Optional, BinaryIO
from PIL import Image
from minio import Minio
from minio.error import S3Error

from domain.repositories.storage.file_storage_repository import FileStorageRepository


class MinioStorageClient(FileStorageRepository):
    """
    Implementazione del FileStorageRepository usando MinIO.
    Singleton pattern per riutilizzare la connessione.
    Tutte le configurazioni vengono lette dal file .env
    """
    _instance: Optional['MinioStorageClient'] = None
    _initialized: bool = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(
        self, 
        endpoint: str = None,
        access_key: str = None,
        secret_key: str = None,
        secure: bool = None,
        default_bucket: str = None
    ):
        if not self._initialized:
            import os
            self.endpoint = endpoint or os.getenv("MINIO_ENDPOINT", "localhost:9002")
            self.access_key = access_key or os.getenv("MINIO_ACCESS_KEY", "minioadmin")
            self.secret_key = secret_key or os.getenv("MINIO_SECRET_KEY", "minioadmin")
            self.secure = secure if secure is not None else os.getenv("MINIO_SECURE", "false").lower() == "true"
            self.default_bucket = default_bucket or os.getenv("MINIO_BUCKET_NAME", "bucket1")
            
            self.client = Minio(
                self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure
            )
            
            # Assicurati che il bucket di default esista
            self._ensure_bucket_exists(self.default_bucket)
            
            self._initialized = True
    
    def get_default_bucket(self) -> str:
        """Restituisce il bucket di default configurato nel .env"""
        return self.default_bucket
    
    def _ensure_bucket_exists(self, bucket: str) -> None:
        """Crea il bucket se non esiste"""
        try:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)
        except S3Error as e:
            print(f"Error creating bucket {bucket}: {e}")
            raise
    
    @staticmethod
    def optimize_image(image_bytes: bytes, max_size: int = 800, quality: int = 85) -> bytes:
        """
        Ridimensiona e ottimizza un'immagine.
        
        Args:
            image_bytes: Bytes dell'immagine originale
            max_size: Dimensione massima (larghezza/altezza)
            quality: Qualità JPEG (1-100)
            
        Returns:
            Bytes dell'immagine ottimizzata
        """
        img = Image.open(io.BytesIO(image_bytes))
        
        # Converti in RGB se necessario (per JPEG)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        # Ridimensiona mantenendo aspect ratio
        img.thumbnail((max_size, max_size))
        
        # Salva in formato JPEG ottimizzato
        output = io.BytesIO()
        img.save(output, format="JPEG", quality=quality, optimize=True)
        return output.getvalue()
    
    async def upload_file(
        self, 
        bucket: str, 
        file_path: str, 
        file_data: BinaryIO, 
        content_type: str,
        file_size: int
    ) -> str:
        """Carica un file su MinIO"""
        loop = asyncio.get_event_loop()
        
        def _upload():
            self._ensure_bucket_exists(bucket)
            self.client.put_object(
                bucket_name=bucket,
                object_name=file_path,
                data=file_data,
                length=file_size,
                content_type=content_type
            )
            return file_path
        
        return await loop.run_in_executor(None, _upload)
    
    async def upload_image(
        self,
        bucket: str,
        file_path: str,
        image_bytes: bytes,
        optimize: bool = True,
        max_size: int = 800
    ) -> str:
        """
        Carica un'immagine su MinIO con ottimizzazione opzionale.
        
        Args:
            bucket: Nome del bucket
            file_path: Percorso del file
            image_bytes: Bytes dell'immagine
            optimize: Se True, ottimizza l'immagine
            max_size: Dimensione massima per l'ottimizzazione
            
        Returns:
            Path del file caricato
        """
        if optimize:
            image_bytes = self.optimize_image(image_bytes, max_size)
        
        file_data = io.BytesIO(image_bytes)
        return await self.upload_file(
            bucket=bucket,
            file_path=file_path,
            file_data=file_data,
            content_type="image/jpeg",
            file_size=len(image_bytes)
        )
    
    async def get_file(self, bucket: str, file_path: str) -> Optional[bytes]:
        """Recupera un file da MinIO"""
        loop = asyncio.get_event_loop()
        
        def _get():
            try:
                response = self.client.get_object(bucket, file_path)
                data = response.read()
                response.close()
                response.release_conn()
                return data
            except S3Error as e:
                if e.code == "NoSuchKey":
                    return None
                raise
        
        return await loop.run_in_executor(None, _get)
    
    async def delete_file(self, bucket: str, file_path: str) -> bool:
        """Elimina un file da MinIO"""
        loop = asyncio.get_event_loop()
        
        def _delete():
            try:
                self.client.remove_object(bucket, file_path)
                return True
            except S3Error:
                return False
        
        return await loop.run_in_executor(None, _delete)
    
    async def delete_files_by_prefix(self, bucket: str, prefix: str) -> int:
        """Elimina tutti i file con un determinato prefix"""
        loop = asyncio.get_event_loop()
        
        def _delete_all():
            count = 0
            try:
                objects = self.client.list_objects(bucket, prefix=prefix, recursive=True)
                for obj in objects:
                    self.client.remove_object(bucket, obj.object_name)
                    count += 1
            except S3Error:
                pass
            return count
        
        return await loop.run_in_executor(None, _delete_all)
    
    async def file_exists(self, bucket: str, file_path: str) -> bool:
        """Verifica se un file esiste"""
        loop = asyncio.get_event_loop()
        
        def _exists():
            try:
                self.client.stat_object(bucket, file_path)
                return True
            except S3Error:
                return False
        
        return await loop.run_in_executor(None, _exists)
    
    async def get_file_url(self, bucket: str, file_path: str, expires_in: int = 3600) -> Optional[str]:
        """Genera un URL presigned per accedere al file"""
        loop = asyncio.get_event_loop()
        
        def _get_url():
            try:
                url = self.client.presigned_get_object(
                    bucket,
                    file_path,
                    expires=timedelta(seconds=expires_in)
                )
                return url
            except S3Error:
                return None
        
        return await loop.run_in_executor(None, _get_url)
    
    async def list_files(self, bucket: str, prefix: str = "") -> list[str]:
        """Lista tutti i file in un bucket con un prefix"""
        loop = asyncio.get_event_loop()
        
        def _list():
            try:
                objects = self.client.list_objects(bucket, prefix=prefix, recursive=True)
                return [obj.object_name for obj in objects]
            except S3Error:
                return []
        
        return await loop.run_in_executor(None, _list)
    
    async def get_latest_file(self, bucket: str, prefix: str) -> Optional[str]:
        """Recupera l'ultimo file caricato con un determinato prefix"""
        files = await self.list_files(bucket, prefix)
        return files[-1] if files else None
