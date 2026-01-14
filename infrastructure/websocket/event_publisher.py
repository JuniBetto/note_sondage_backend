## app/infrastructure/websocket/web_socket_publisher.py

from domain.entities.event.event_entity import EventEntity as EventCrud
from domain.repositories.websocket.repository_socket import RepositorySocket


class EventPublisher:
    def __init__(self, socket_repository: RepositorySocket):
        self.socket_repository = socket_repository

    async def publish(self, event: EventCrud) -> None:
        await self.socket_repository.broadcast(  {
            "event": event.name,
            "data": event.payload,
            "occurred_at": event.occurred_at.isoformat()
        })

        