from abc import ABC, abstractmethod

from fastapi import WebSocket
from domain.repositories.websocket.repository_socket import RepositorySocket



class ConnectWithSocket(RepositorySocket):
    
    @abstractmethod
    def __init__(self) -> None:
        pass


    @abstractmethod
    async def connect(self, websocket: WebSocket) -> None:
        pass

    @abstractmethod
    async def disconnect(self, websocket: WebSocket) -> None:
        pass

    @abstractmethod
    async def broadcast(self, message: dict) -> None:
        pass