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

def get_db_connection() -> PostgresConnection:
    return PostgresConnection()

def get_permission_repository(
    db_connection: PostgresConnection = Depends(get_db_connection)
) -> PermissionRepository:
    return PermissionRepositoryImpl(db_connection)

def get_role_repository(
    db_connection: PostgresConnection = Depends(get_db_connection)
) -> RoleRepository:
    return RoleRepositoryImpl(db_connection)


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