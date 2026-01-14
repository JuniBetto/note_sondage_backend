from abc import abstractmethod
from typing import Optional
from domain.entities.event.event_entity import EventEntity
from domain.repositories.event.event_base_repository import EventBaseRepository


class EventRepository(EventBaseRepository):
    
    @abstractmethod
    def create_event(data_event:dict)->EventEntity:
        # Logic to create an event
        pass

    @abstractmethod
    def update_event(data_event:dict)->EventEntity:
        # Logic to create an event
        pass

    @abstractmethod
    def delete_event(entity_event:str,id:str)->Optional[EventEntity]| None:
        # Logic to create an event
        pass