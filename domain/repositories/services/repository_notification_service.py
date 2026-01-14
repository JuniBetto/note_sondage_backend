#app/domain/services/notification_service.py
from abc import abstractmethod

from infrastructure.websocket.event_publisher import EventPublisher
from domain.entities.event.event_entity import EventEntity
from domain.repositories.services.notification import Notification


class RepositoryNotificationService(Notification):
    @abstractmethod
    def __init__(self,publisher:EventPublisher) -> None:
        pass

    @abstractmethod
    async def notify(self, event:EventEntity)->None:
        pass

    