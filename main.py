# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI

from api.v1.endpoints import permission_controller
from api.v1.endpoints import role_controller
from api.v1.endpoints import team_controller
from api.v1.endpoints import user_controller
from api.v1.endpoints import team_member_controller
from api.ws import websocket_router
from infrastructure.http import unexpected_exception_handler
from domain.exceptions.infrastructure_exception import InfrastructureException
from infrastructure.http import infrastructure_exception_handler
from domain.exceptions.domain_exception import DomainException
from infrastructure.http.error_handlers import domain_exception_handler
from api.depends.dependency import _redis_context, get_redis


@asynccontextmanager 
async def lifespan(app: FastAPI):
    print("Connecting to Redis...")
    
    # Crea e salva Redis
    async with _redis_context() as redis_client:
        app.state.redis = redis_client
        print("Redis connected!")
        
        yield
        
        print("Disconnecting from Redis...")
    
    print("Redis disconnected!")

app = FastAPI(lifespan=lifespan, title="note sondaggio API")

app.add_exception_handler(DomainException, domain_exception_handler)
app.add_exception_handler(
    InfrastructureException,
    infrastructure_exception_handler
)
app.add_exception_handler(Exception, unexpected_exception_handler)


app.include_router(permission_controller.router, prefix="/permissions", tags=["permissions"])
app.include_router(role_controller.router, prefix="/roles", tags=["roles"])
app.include_router(team_controller.router, prefix="/teams", tags=["teams"])
app.include_router(user_controller.router, prefix="/users", tags=["users"])
app.include_router(team_member_controller.router, prefix="/team-members", tags=["team-members"])

# WebSocket
app.include_router(websocket_router.router)



@app.get("/health")
async def health():
    try:
        # Test Redis
        await get_redis().set("health_check", "ok", ttl=10)
        value = await get_redis().get("health_check")
        return {
            "status": "healthy",
            "redis": value == "ok"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "redis": False,
            "error": str(e)
        }
