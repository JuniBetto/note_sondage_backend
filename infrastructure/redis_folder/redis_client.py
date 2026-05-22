# app/redis/redis_client.py

import json
from typing import Optional, Any

from domain.repositories.redis.redis_repository import RedisRepository
from infrastructure.redis_folder.redis_config import settings
import redis.asyncio as redis

class AsyncRedisCache(RedisRepository):
    _instance: Optional['AsyncRedisCache'] = None  # <-- Aggiunto qui
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.client: Optional[redis.Redis] = None
            self._initialized = True


    async def ensure_connected(self):
        """Assicura che il client sia connesso"""
        if not self._instance or self.client is None:
            await self.connect()


    async def connect(self):
        """Connessione a Redis"""
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
            socket_connect_timeout=5
        )
        await self.client.ping()  # Test connessione

    
    async def disconnect(self):
        """Chiudi connessione"""
        if self.client:
            await self.client.close()
            self.client = None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Salva valore in cache"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)

            ttl = ttl or settings.CACHE_TTL
            return await self.client.setex(key, ttl, value)
        except Exception as e:
            print(f"Redis async set error: {e}")
            return False
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Recupera valore dalla cache"""
        try:
            value = await self.client.get(key)
            if value is None:
                return default
            
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception as e:
            print(f"Redis async get error: {e}")
            return default
    
    async def delete(self, *keys: str) -> int:
        """Elimina chiavi"""
        try:
            return await self.client.delete(*keys)
        except Exception as e:
            print(f"Redis async delete error: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """Controlla se una chiave esiste"""
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            print(f"Redis async exists error: {e}")
            return False

    async def invalidate_cache(self, pattern: str = "*") -> int:
        """
        Invalida tutte le chiavi che corrispondono al pattern.
        Pattern supporta * per match multiplo e ? per match singolo.
        """
        try:
            await self.ensure_connected()
            keys = []
            
            # Scansiona tutte le chiavi che corrispondono al pattern
            async for key in self.client.scan_iter(match=pattern):
                keys.append(key)
            
            # Elimina tutte le chiavi trovate
            if keys:
                deleted = await self.client.delete(*keys)
                return deleted
            return 0
        except Exception as e:
            print(f"Redis async invalidate_cache error: {e}")
            return 0
    # Istanza globale
    #async_redis = AsyncRedisCache()