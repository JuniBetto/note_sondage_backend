# main.py
from fastapi import FastAPI

from api.v1.endpoints import permission_controller
from api.v1.endpoints import role_controller
from api.ws import websocket_router
from infrastructure.http import unexpected_exception_handler
from domain.exceptions.infrastructure_exception import InfrastructureException
from infrastructure.http import infrastructure_exception_handler
from domain.exceptions.domain_exception import DomainException
from infrastructure.http.error_handlers import domain_exception_handler


app = FastAPI(title="note sondaggio API")

app.add_exception_handler(DomainException, domain_exception_handler)
app.add_exception_handler(
    InfrastructureException,
    infrastructure_exception_handler
)
app.add_exception_handler(Exception, unexpected_exception_handler)


app.include_router(permission_controller.router, prefix="/permissions", tags=["permissions"])
app.include_router(role_controller.router, prefix="/roles", tags=["roles"])

# WebSocket
app.include_router(websocket_router.router)



@app.get("/health")
async def health():
    return {"status": "ok"}
