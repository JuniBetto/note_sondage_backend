from datetime import datetime
from domain.entities.event.event_entity import EventEntity


class EventMapper:
    @staticmethod
    def to_dict(event: EventEntity) -> dict:
        return {
            "name": event.name,
            "payload": event.payload,
            "occurred_at": event.occurred_at.isoformat()
        }

    @staticmethod
    def from_dict(data: dict) -> EventEntity:
        return EventEntity(
            name=data["name"],
            payload=data["payload"],
            occurred_at=datetime.fromisoformat(data["occurred_at"])
        )