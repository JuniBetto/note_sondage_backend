

from datetime import datetime


class EventEntity:
    def __init__(self, name: str, payload: dict, occurred_at: datetime):
        self.name = name
        self.payload = payload
        self.occurred_at = occurred_at

    def to_dict(self):
        return {
            "name": self.name,
            "payload": self.payload,
            "occurred_at": self.occurred_at.isoformat()
        }
