from contextlib import asynccontextmanager
from fastapi import Depends
from domain.repositories.websocket.repository_socket import RepositorySocket
from infrastructure.websocket.connection_manager import connection_manager
from domain.repositories.services.notification import Notification
from infrastructure.notification.web_socket_notification_service_impl import WebSocketNotificationServiceImpl
from infrastructure.websocket.event_publisher import EventPublisher
from domain.repositories.role.role_repository import RoleRepository
from infrastructure.repositories.role.role_repository_impl import RoleRepositoryImpl
from infrastructure.database.postgres_connection import PostgresConnection
from domain.repositories.permission.permission_repository import PermissionRepository
from infrastructure.repositories.permission.permission_repository_impl import PermissionRepositoryImpl
from domain.repositories.redis.redis_repository import RedisRepository
from infrastructure.redis_folder.redis_client import AsyncRedisCache
from domain.repositories.team.team_repository import TeamRepository
from infrastructure.repositories.team.team_repository_impl import TeamRepositoryImpl
from domain.repositories.user.user_repository import UserRepository
from infrastructure.repositories.user.user_repository_impl import UserRepositoryImpl
from domain.repositories.team_member.team_member_repository import TeamMemberRepository
from infrastructure.repositories.team_member.team_member_repository_impl import TeamMemberRepositoryImpl
from infrastructure.minio_folder.minio_storage_client import MinioStorageClient
from domain.services.profile_image_service import ProfileImageService

# Dependency per ottenere la connessione al database

def get_db_connection() -> PostgresConnection:
    return PostgresConnection()

# Context manager per gestire la connessione a Redis
@asynccontextmanager
async def _redis_context():
    """Context manager interno per gestire la connessione"""
    redis_cache = AsyncRedisCache()
    try:
        await redis_cache.ensure_connected()
        yield redis_cache
    finally:
        await redis_cache.disconnect()


# Dependency per ottenere il client Redis connesso
async def get_redis() -> AsyncRedisCache:
    """
    Dependency che ritorna sempre la stessa istanza di Redis.
    Deve essere inizializzata nel lifespan.
    """
    # Se hai salvato Redis in app.state
    try:
        from main import app  # Import circolare? Meglio passare come arg
        return app.state.redis
    except (AttributeError, ImportError):
        # Fallback: crea una nuova istanza
        redis_cache = AsyncRedisCache()
        await redis_cache.ensure_connected()
        return redis_cache

# Dependency per ottenere il repository delle permission
async def get_permission_repository(
    db_connection: PostgresConnection = Depends(get_db_connection),
    cache_service: RedisRepository = Depends(get_redis)
) -> PermissionRepository:
    return PermissionRepositoryImpl(db_connection, cache_service)

# Dependency per ottenere il repository dei ruoli
async def get_role_repository(
    db_connection: PostgresConnection = Depends(get_db_connection),
    cache_service: RedisRepository = Depends(get_redis)
) -> RoleRepository:
    return RoleRepositoryImpl(db_connection, cache_service=cache_service)


# Dependency per ottenere il repository dei team
async def get_team_repository(
    db_connection: PostgresConnection = Depends(get_db_connection),
    cache_service: RedisRepository = Depends(get_redis)
) -> TeamRepository:
    return TeamRepositoryImpl(db_connection, cache_service=cache_service)


# Dependency per ottenere il repository degli utenti
async def get_user_repository(
    db_connection: PostgresConnection = Depends(get_db_connection),
    cache_service: RedisRepository = Depends(get_redis)
) -> UserRepository:
    return UserRepositoryImpl(db_connection, cache_service=cache_service)


# Dependency per ottenere il repository dei team member
async def get_team_member_repository(
    db_connection: PostgresConnection = Depends(get_db_connection),
    cache_service: RedisRepository = Depends(get_redis)
) -> TeamMemberRepository:
    return TeamMemberRepositoryImpl(db_connection, cache_service=cache_service)


# Dependency per ottenere il servizio di notifica
def get_notification_service() -> Notification:
    return WebSocketNotificationServiceImpl(publisher=EventPublisher.get_instance())



# Factory per creare le istanze
def get_notification_service() -> Notification:
    # Crea il repository socket (singleton)
    socket_repo: RepositorySocket = connection_manager
    print(f"🔧 Factory: usando connection_manager singleton (id: {id(socket_repo)})")
    # Crea il publisher
    publisher = EventPublisher(socket_repository=socket_repo)
    
    # Crea il servizio di notifica
    return WebSocketNotificationServiceImpl(publisher=publisher)


# Dependency per ottenere il client storage (MinIO)
def get_storage_client() -> MinioStorageClient:
    """
    Dependency che ritorna il client MinIO per la gestione dei file.
    Utilizza il pattern Singleton per riutilizzare la stessa istanza.
    Tutte le configurazioni vengono lette dal .env
    """
    return MinioStorageClient()


# Dependency per ottenere il servizio di gestione delle immagini profilo
def get_profile_image_service(
    team_member_repo: TeamMemberRepository = Depends(get_team_member_repository)
) -> ProfileImageService:
    """
    Dependency per ottenere il servizio di gestione delle immagini profilo.
    Usa MinioStorageClient direttamente con config dal .env
    Può essere usato per team_member, user, team, ecc.
    Include team_member_repository per aggiornare image_url nel DB.
    """
    return ProfileImageService(team_member_repository=team_member_repo)


# Dependency per ottenere il client Redis
# async def get_redis() -> RedisRepository:
#     """Dependency per ottenere il client Redis"""
#     redis_cache = AsyncRedisCache()
#     return redis_cache