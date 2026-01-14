# app/api/ws/websocket_router.py

import logging
import traceback
from fastapi import WebSocket
from fastapi import APIRouter

from infrastructure.websocket.connection_manager import connection_manager
router = APIRouter()


""" 
@router.websocket("/ws/permissions")
async def ws_permissions(ws: WebSocket):
    await ConnectionManager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except:
        ConnectionManager.disconnect(ws)


""" 
logger = logging.getLogger(__name__)

@router.websocket("/ws/listen")
async def ws_permissions(ws: WebSocket):
   
   try:
       logger.info(f"WebSocket connection attempt from {ws.client}")

       # Accetta la connessione PRIMA di tutto
       await ws.accept()
       logger.info("WebSocket connection accepted")

       await connection_manager.connect(ws)
       logger.info("Connected to ConnectionManager")
       while True:
           try:
            data = await ws.receive_text()
            logger.info(f"Received message: {data}")

            await ws.send_text(f"Message received: {data}")
           except Exception as e:
               logger.error(f"Error in message handling: {e}")
               logger.error(traceback.format_exc())
               break


   except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        logger.error(traceback.format_exc())
        raise
   finally: 
       connection_manager.disconnect(ws)