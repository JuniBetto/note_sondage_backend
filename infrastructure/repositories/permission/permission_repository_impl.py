import asyncio
from typing import Optional
from uuid import UUID
from domain.entities.permission.permission_entity import PermissionEntity
from domain.repositories.permission.permission_repository import PermissionRepository
from infrastructure.database.postgres_connection import PostgresConnection
from domain.repositories.redis.redis_repository import RedisRepository


class PermissionRepositoryImpl(PermissionRepository):
    def __init__(self, db_connection: PostgresConnection, cache_service: Optional[RedisRepository] = None):
        self.connection = db_connection
        self.cache_service = cache_service
        self.cache_prefix = "permission"
        self.default_ttl = 3600 



    async def save(self, permission: PermissionEntity) -> PermissionEntity:
        query = """
        INSERT INTO permissions (id, code, description)
        VALUES (%s, %s, %s)
        RETURNING id, code, description
        """
        params = (str(permission.id), permission.code, permission.description)
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_insert(
                query, params, return_columns=['id', 'code', 'description']
            )
        )
        
        new_data = result['new']
        entity = PermissionEntity(
            id=new_data['id'],
            code=new_data['code'],
            description=new_data['description']
        )
        
        # Invalida cache dopo eliminazione
        if self.cache_service:
            await self.cache_service.invalidate_cache(f"{self.cache_prefix}:*")
        
        return entity
    
    async def find_by_id(self, permission_id: UUID) -> Optional[PermissionEntity]:
        if self.cache_service:
            cache_key = f"{self.cache_prefix}:id:{permission_id}"
            cached = await self.cache_service.get(cache_key)
            if cached:
                return PermissionEntity(**cached)
        
        query = "SELECT id, code, description FROM permissions WHERE id = %s"
        params = (str(permission_id),)
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_query(query, params)
        )
        
        if not results:
            return None
        
        row = results[0]
        entity = PermissionEntity(
            id=row['id'],
            code=row['code'],
            description=row['description']
        )
        
        if self.cache_service:
            cache_key = f"{self.cache_prefix}:id:{permission_id}"
            await self.cache_service.set(
                cache_key,
                {
                    'id': str(entity.id),
                    'code': entity.code,
                    'description': entity.description
                },
                ttl=self.default_ttl
            )
        
        return entity
    
    async def find_by_code(self, code: str) -> Optional[PermissionEntity]:
        # 1. Controlla cache se disponibile
        if self.cache_service:
            cache_key = f"{self.cache_prefix}:code:{code}"
            cached = await self.cache_service.get(cache_key)
            if cached:
                # Se trovato in cache, deserializza
                return PermissionEntity(**cached)
        
        # 2. Query al database (sync, ma eseguita in thread separato)
        query = "SELECT id, code, description FROM permissions WHERE code = %s"
        params = (code,)
        
        # Esegui query sync in thread separato per non bloccare
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None, 
            lambda: self.connection.execute_query(query, params)
        )
        
        if not results:
            return None
        
        # 3. Crea entità
        row = results[0]
        entity = PermissionEntity(
            id=row['id'],
            code=row['code'],
            description=row['description']
        )
        
        # 4. Salva in cache se disponibile
        if self.cache_service:
            cache_key = f"{self.cache_prefix}:code:{code}"
            await self.cache_service.set(
                cache_key,
                {
                    'id': str(entity.id),
                    'code': entity.code,
                    'description': entity.description
                },
                ttl=self.default_ttl
            )
        
        return entity
    
    async def get_all(self) -> list[PermissionEntity]:
        # Cache per lista completa
        if self.cache_service:
            cache_key = f"{self.cache_prefix}:all"
            cached = await self.cache_service.get(cache_key)
            if cached:
                return [PermissionEntity(**item) for item in cached]
        
        query = """SELECT id, code, description FROM permissions"""
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_query(query)
        )
        
        permissions = []
        for row in results:
            permission = PermissionEntity(
                id=row['id'],
                code=row['code'],
                description=row['description']
            )
            permissions.append(permission)
        
        # Salva in cache
        if self.cache_service and permissions:
            cache_key = f"{self.cache_prefix}:all"
            await self.cache_service.set(
                cache_key,
                [
                    {
                        'id': str(p.id),
                        'code': p.code,
                        'description': p.description
                    } for p in permissions
                ],
                ttl=self.default_ttl
            )
        
        return permissions
    
    async def delete(self, permission_id: UUID) -> Optional[PermissionEntity]:
        query = "DELETE FROM permissions WHERE id = %s"
        old_values_query = "SELECT id, code, description FROM permissions WHERE id = %s"
        params = (str(permission_id),)
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_delete(
                query, params, old_values_query, params
            )
        )
        
        if results:
            row = results['old']
            entity = PermissionEntity(
                id=row['id'],
                code=row['code'],
                description=row['description']
            )
            
            # Invalida cache dopo eliminazione
            if self.cache_service:
                await self.cache_service.invalidate_cache(f"{self.cache_prefix}:*")
            
            return entity
        
        return None
    
    def exists_by_code(self, code: str, exclude_id: Optional[UUID] = None) -> bool:
        if exclude_id:
            query = "SELECT 1 FROM permissions WHERE code = %s AND id != %s"
            params = (code, str(exclude_id))
        else:
            query = "SELECT 1 FROM permissions WHERE code = %s"
            params = (code,)
        
        results = self.connection.execute_query(query, params)
        return len(results) > 0