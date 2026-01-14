from datetime import datetime
from typing import Optional
from domain.repositories.event.event_base_repository import EventBaseRepository
from domain.entities.event.event_entity import EventEntity


class EventRepositoryImpl(EventBaseRepository):
    def create_event(self, data_event: dict) -> EventEntity:
        # Implementation logic to create an event
        event = EventEntity(
            name=data_event.get("name"),
            payload=data_event,
            occurred_at=datetime.now(datetime.timezone.utc)
        )
        # Here you would typically save the event to a database
        return event

    def update_event(self,  data_event: dict) -> EventEntity:
        # Implementation logic to update an event
        event = EventEntity(
            name=data_event.get("name"),
            payload=data_event,
            occurred_at=datetime.now(datetime.timezone.utc)
        )
        # Here you would typically update the event in a database
        return event

    def delete_event(self, entity_event: str, id: str) -> Optional[EventEntity] | None:
        # Implementation logic to delete an event
        event = EventEntity(
            name=f"{entity_event}.deleted",
            payload={"id": str(id)},
            occurred_at=datetime.now(datetime.timezone.utc)
        )
        # Here you would typically delete the event from a database
        return event
    

