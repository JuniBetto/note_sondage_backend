# app/infrastructure/notification/notification_service_impl.py
from infrastructure.websocket.event_publisher import EventPublisher
from domain.entities.event.event_entity import EventEntity
from domain.repositories.services.repository_notification_service import RepositoryNotificationService


class WebSocketNotificationServiceImpl(RepositoryNotificationService):
    def __init__(self, publisher:EventPublisher) -> None:        
        self.publisher = publisher

    async def notify(self, event: EventEntity) -> None:
        await self.publisher.publish(event)


