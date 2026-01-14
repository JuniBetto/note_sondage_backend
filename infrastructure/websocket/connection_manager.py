
# app/infrastructure/websocket/connection_manager.py
from typing import Optional
from fastapi.websockets import WebSocket
from domain.repositories.websocket.connect_with_socket import ConnectWithSocket


# infrastructure/websocket/connection_manager.py
from fastapi import WebSocket
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    _instance: Optional['ConnectionManager'] = None
    
    @classmethod
    def get_instance(cls):
        """Metodo per ottenere l'istanza singleton"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """Costruttore - viene chiamato solo una volta"""
        if not hasattr(self, 'active_connections'):
            self.active_connections: List[WebSocket] = []
            logger.info("✅ ConnectionManager inizializzato")
    
    async def connect(self, websocket: WebSocket):
        """Aggiungi una connessione alla lista"""
        # NOTA: NON chiamare websocket.accept() qui
        self.active_connections.append(websocket)
        logger.info(f"✅ Client connesso. Totale: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Rimuovi una connessione"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"✅ Client disconnesso. Totale: {len(self.active_connections)}")
        else:
            logger.warning("⚠️  Tentativo di disconnettere client non presente")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Invia messaggio a un client specifico"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"❌ Errore invio messaggio: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """Invia messaggio a tutti i client"""
        disconnected = []
        
        logger.info(f"📢 Broadcast a {len(self.active_connections)} client")
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"❌ Errore broadcast: {e}")
                disconnected.append(connection)
        
        for connection in disconnected:
            self.disconnect(connection)

# Crea l'istanza singleton globale
connection_manager = ConnectionManager.get_instance()


'''class ConnectionManager(ConnectWithSocket):
    _instance: Optional['ConnectionManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Inizializzazione nell'__new__ per garantire singleton
            cls._instance.active_connections = []  # type: List[WebSocket]
            print("✅ ConnectionManager singleton creato")
        return cls._instance
    
    def __init__(self):
        # __init__ viene chiamato ogni volta, ma controlliamo se è già inizializzato
        if not hasattr(self, '_initialized'):
            super().__init__()
            self._initialized = True
            print("✅ ConnectionManager inizializzato")

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)'''

