import uuid
from typing import Optional
from infrastructure.minio_folder.minio_storage_client import MinioStorageClient
from domain.repositories.team_member.team_member_repository import TeamMemberRepository


class ProfileImageService:
    """
    Servizio per la gestione delle immagini profilo.
    Usa MinioStorageClient direttamente per avere una sola configurazione
    che punta al file .env per tutte le variabili.
    """
    
    def __init__(
        self, 
        storage_client: MinioStorageClient = None,
        team_member_repository: TeamMemberRepository = None
    ):
        # Usa il client passato o crea una nuova istanza (singleton)
        self.storage_client = storage_client or MinioStorageClient()
        # Il bucket viene letto dal .env tramite MinioStorageClient
        self.bucket_name = self.storage_client.get_default_bucket()
        # Repository per aggiornare image_url nel DB
        self.team_member_repository = team_member_repository
    
    def _generate_file_path(self, entity_type: str, entity_id: str, file_extension: str = "jpg") -> str:
        """
        Genera un path univoco per il file.
        
        Args:
            entity_type: Tipo di entità (user, team_member, team)
            entity_id: ID dell'entità
            file_extension: Estensione del file
            
        Returns:
            Path del file: {entity_type}/{entity_id}/{uuid}.{extension}
        """
        unique_id = uuid.uuid4()
        return f"{entity_type}/{entity_id}/{unique_id}.{file_extension}"
    
    async def upload_profile_image(
        self,
        entity_type: str,
        entity_id: str,
        image_bytes: bytes,
        optimize: bool = True
    ) -> str:
        """
        Carica un'immagine profilo.
        Prima elimina le vecchie immagini, poi carica la nuova.
        
        Args:
            entity_type: Tipo di entità (user, team_member, team)
            entity_id: ID dell'entità
            image_bytes: Bytes dell'immagine
            optimize: Se True, ottimizza l'immagine
            
        Returns:
            URL o path dell'immagine caricata
        """
        # Elimina vecchie immagini
        prefix = f"{entity_type}/{entity_id}/"
        await self.storage_client.delete_files_by_prefix(self.bucket_name, prefix)
        
        # Genera nuovo path
        file_path = self._generate_file_path(entity_type, entity_id)
        
        # Carica la nuova immagine
        await self.storage_client.upload_image(
            bucket=self.bucket_name,
            file_path=file_path,
            image_bytes=image_bytes,
            optimize=optimize
        )
        try:
            # Se è un team_member, aggiorna image_url nel database
            if entity_type == "team_member" and self.team_member_repository:
                await self.team_member_repository.update_image_url(entity_id, file_path)
        except Exception as e:
            print(f"Error updating image URL for {entity_type}/{entity_id}: {e}")

        return file_path
    
    async def get_profile_image_url(
        self,
        entity_type: str,
        entity_id: str,
        expires_in: int = 3600
    ) -> Optional[str]:
        """
        Ottiene l'URL dell'immagine profilo.
        
        Args:
            entity_type: Tipo di entità
            entity_id: ID dell'entità
            expires_in: Durata validità URL in secondi
            
        Returns:
            URL presigned dell'immagine, None se non trovata
        """
        prefix = f"{entity_type}/{entity_id}/"
        latest_file = await self.storage_client.get_latest_file(self.bucket_name, prefix)
        
        if not latest_file:
            return None
        
        return await self.storage_client.get_file_url(
            self.bucket_name,
            latest_file,
            expires_in
        )
    
    async def get_profile_image(
        self,
        entity_type: str,
        entity_id: str
    ) -> Optional[bytes]:
        """
        Recupera i bytes dell'immagine profilo.
        
        Args:
            entity_type: Tipo di entità
            entity_id: ID dell'entità
            
        Returns:
            Bytes dell'immagine, None se non trovata
        """
        prefix = f"{entity_type}/{entity_id}/"
        latest_file = await self.storage_client.get_latest_file(self.bucket_name, prefix)
        
        if not latest_file:
            return None
        
        return await self.storage_client.get_file(self.bucket_name, latest_file)
    
    async def delete_profile_image(
        self,
        entity_type: str,
        entity_id: str
    ) -> bool:
        """
        Elimina l'immagine profilo.
        
        Args:
            entity_type: Tipo di entità
            entity_id: ID dell'entità
            
        Returns:
            True se eliminata con successo
        """
        prefix = f"{entity_type}/{entity_id}/"
        deleted_count = await self.storage_client.delete_files_by_prefix(self.bucket_name, prefix)
        return deleted_count > 0
    
    async def has_profile_image(
        self,
        entity_type: str,
        entity_id: str
    ) -> bool:
        """
        Verifica se esiste un'immagine profilo.
        
        Args:
            entity_type: Tipo di entità
            entity_id: ID dell'entità
            
        Returns:
            True se esiste un'immagine
        """
        prefix = f"{entity_type}/{entity_id}/"
        files = await self.storage_client.list_files(self.bucket_name, prefix)
        return len(files) > 0
