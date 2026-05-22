from abc import ABC, abstractmethod
from typing import Optional, BinaryIO


class FileStorageRepository(ABC):
    """
    Interfaccia astratta per il servizio di storage file.
    Può essere implementata con MinIO, S3, Azure Blob, ecc.
    """
    
    @abstractmethod
    async def upload_file(
        self, 
        bucket: str, 
        file_path: str, 
        file_data: BinaryIO, 
        content_type: str,
        file_size: int
    ) -> str:
        """
        Carica un file nello storage.
        
        Args:
            bucket: Nome del bucket
            file_path: Percorso/nome del file nel bucket
            file_data: Dati del file come stream
            content_type: MIME type del file
            file_size: Dimensione del file in bytes
            
        Returns:
            URL o path del file caricato
        """
        ...
    
    @abstractmethod
    async def get_file(self, bucket: str, file_path: str) -> Optional[bytes]:
        """
        Recupera un file dallo storage.
        
        Args:
            bucket: Nome del bucket
            file_path: Percorso/nome del file nel bucket
            
        Returns:
            Contenuto del file come bytes, None se non trovato
        """
        ...
    
    @abstractmethod
    async def delete_file(self, bucket: str, file_path: str) -> bool:
        """
        Elimina un file dallo storage.
        
        Args:
            bucket: Nome del bucket
            file_path: Percorso/nome del file nel bucket
            
        Returns:
            True se eliminato con successo, False altrimenti
        """
        ...
    
    @abstractmethod
    async def delete_files_by_prefix(self, bucket: str, prefix: str) -> int:
        """
        Elimina tutti i file che iniziano con un determinato prefix.
        
        Args:
            bucket: Nome del bucket
            prefix: Prefisso dei file da eliminare
            
        Returns:
            Numero di file eliminati
        """
        ...
    
    @abstractmethod
    async def file_exists(self, bucket: str, file_path: str) -> bool:
        """
        Verifica se un file esiste.
        
        Args:
            bucket: Nome del bucket
            file_path: Percorso/nome del file nel bucket
            
        Returns:
            True se il file esiste, False altrimenti
        """
        ...
    
    @abstractmethod
    async def get_file_url(self, bucket: str, file_path: str, expires_in: int = 3600) -> Optional[str]:
        """
        Genera un URL temporaneo (presigned) per accedere al file.
        
        Args:
            bucket: Nome del bucket
            file_path: Percorso/nome del file nel bucket
            expires_in: Durata validità URL in secondi (default 1 ora)
            
        Returns:
            URL presigned per accedere al file
        """
        ...
    
    @abstractmethod
    async def list_files(self, bucket: str, prefix: str = "") -> list[str]:
        """
        Lista tutti i file in un bucket con un determinato prefix.
        
        Args:
            bucket: Nome del bucket
            prefix: Prefisso per filtrare i file
            
        Returns:
            Lista dei nomi dei file
        """
        ...
