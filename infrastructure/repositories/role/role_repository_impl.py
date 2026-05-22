import asyncio
from typing import Optional
from uuid import UUID
from domain.entities.role.role_entity import RoleEntity
from domain.repositories.role.role_repository import RoleRepository
from infrastructure.database.postgres_connection import PostgresConnection
from domain.repositories.redis.redis_repository import RedisRepository


class RoleRepositoryImpl(RoleRepository):
    def __init__(self, db_connection: PostgresConnection, cache_service: Optional[RedisRepository] = None):
        self.connection = db_connection
        self.cache_service = cache_service
        self.cache_prefix = "role"
        self.default_ttl = 3600

    async def _find_by_id(self, role_id: UUID) -> Optional[RoleEntity] | None:
        # Controlla cache
        if self.cache_service:
            cache_key = f"{self.cache_prefix}:id:{role_id}"
            cached = await self.cache_service.get(cache_key)
            if cached:
                return RoleEntity(**cached)

        query = "SELECT id, team_id, name, description, permissions, is_deleted FROM roles WHERE id = %s AND is_deleted = FALSE"
        params = (str(role_id),)
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_query(query, params)
        )
        
        if results:
            row = results[0]
            entity = RoleEntity(
                id=row['id'],
                team_id=row['team_id'],
                name=row['name'],
                description=row['description'],
                permissions=row['permissions'],
                is_deleted=row['is_deleted']
            )
            
            # Salva in cache
            if self.cache_service:
                await self.cache_service.set(
                    cache_key,
                    {
                        'id': str(entity.id),
                        'team_id': str(entity.team_id),
                        'name': entity.name,
                        'description': entity.description,
                        'permissions': entity.permissions,
                        'is_deleted': entity.is_deleted
                    },
                    ttl=self.default_ttl
                )
            
            return entity
        return None

    async def create(self, role: RoleEntity) -> RoleEntity:
        query = """
        INSERT INTO roles (id, team_id, name, description, permissions, is_deleted) values (%s, %s, %s, %s, %s, %s)
        RETURNING id, team_id, name, description, permissions, is_deleted"""
        params = (str(role.id), str(role.team_id), role.name, role.description, role.permissions, False)
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_insert(query, params, return_columns=['id', 'team_id', 'name', 'description', 'permissions', 'is_deleted'])
        )
        
        newData = result['new']
        entity = RoleEntity(
            id=newData['id'],
            team_id=newData['team_id'],
            name=newData['name'],
            description=newData['description'],
            permissions=newData['permissions'],
            is_deleted=newData['is_deleted']
        )
        
        # Invalida cache dopo creazione
        if self.cache_service:
            await self.cache_service.invalidate_cache(f"{self.cache_prefix}:*")
        
        return entity

    async def find_by_name(self, name: str, team_id: str) -> Optional[RoleEntity] | None:
        # Controlla cache
        if self.cache_service:
            cache_key = f"{self.cache_prefix}:name:{name}:team:{team_id}"
            cached = await self.cache_service.get(cache_key)
            if cached:
                return RoleEntity(**cached)

        query = "SELECT id, team_id, name, description, permissions, is_deleted FROM roles WHERE name = %s and team_id = %s AND is_deleted = FALSE"
        params = (name, team_id)

        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_query(query, params)
        )
        
        if results:
            row = results[0]
            entity = RoleEntity(
                id=row['id'],
                team_id=row['team_id'],
                name=row['name'],
                description=row['description'],
                permissions=row['permissions'],
                is_deleted=row['is_deleted']
            )
            
            # Salva in cache
            if self.cache_service:
                cache_key = f"{self.cache_prefix}:name:{name}"
                await self.cache_service.set(
                    cache_key,
                    {
                        'id': str(entity.id),
                        'team_id': str(entity.team_id),
                        'name': entity.name,
                        'description': entity.description,
                        'permissions': entity.permissions,
                        'is_deleted': entity.is_deleted
                    },
                    ttl=self.default_ttl
                )
            
            return entity
        return None

    async def update(self, role: RoleEntity) -> RoleEntity:
        query = """
        UPDATE roles SET team_id = %s, name = %s, description = %s, permissions = %s WHERE id = %s AND is_deleted = FALSE
        RETURNING id, team_id, name, description, permissions, is_deleted"""

        get_old_values_query = "SELECT id, team_id, name, description, permissions, is_deleted FROM roles WHERE id = %s"
        params = (str(role.team_id), role.name, role.description, role.permissions, str(role.id))
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_update(query, params, return_columns=['team_id', 'name', 'description', 'permissions', 'id', 'is_deleted'], get_old_values_query=get_old_values_query, get_old_params=(str(role.id),))
        )
        

        
        updatedData = result['new']
        #if updatedData is None:
            #raise ValueError("Update failed, no data returned")
        
        entity = RoleEntity(
            id=updatedData['id'],
            team_id=updatedData['team_id'],
            name=updatedData['name'],
            description=updatedData['description'],
            permissions=updatedData['permissions'],
            is_deleted=updatedData['is_deleted']
        )
        
        # Invalida cache dopo update
        if self.cache_service:
            await self.cache_service.invalidate_cache(f"{self.cache_prefix}:*")
        
        return entity

    async def delete(self, role_id: str) -> Optional[RoleEntity]:
        """Soft delete: imposta is_deleted = TRUE invece di eliminare fisicamente"""
        # Prima verifica che esista e non sia già eliminato
        check_query = "SELECT id, team_id, name, description, permissions, is_deleted FROM roles WHERE id = %s AND is_deleted = FALSE"
        
        loop = asyncio.get_event_loop()
        existing = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_query(check_query, (role_id,))
        )
        
        if not existing:
            return None
        
        # Esegui soft delete
        query = """
        UPDATE roles SET is_deleted = TRUE WHERE id = %s AND is_deleted = FALSE
        RETURNING id, team_id, name, description, permissions, is_deleted"""
        params = (role_id,)
        
        result = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_query(query, params)
        )
        
        if result:
            row = result[0]
            entity = RoleEntity(
                id=row['id'],
                team_id=row['team_id'],
                name=row['name'],
                description=row['description'],
                permissions=row['permissions'],
                is_deleted=row['is_deleted']
            )
            
            # Invalida cache dopo eliminazione
            if self.cache_service:
                await self.cache_service.invalidate_cache(f"{self.cache_prefix}:*")
            
            return entity
        
        return None

    async def get_all(self) -> list[RoleEntity]:
        # Cache per lista completa
        if self.cache_service:
            cache_key = f"{self.cache_prefix}:all"
            cached = await self.cache_service.get(cache_key)
            if cached:
                return [RoleEntity(**item) for item in cached]
        
        query = """SELECT id, team_id, name, description, permissions, is_deleted FROM roles WHERE is_deleted = FALSE"""
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_query(query)
        )
        
        roles = []
        for row in results:
            role = RoleEntity(
                id=row['id'],
                team_id=row['team_id'],
                name=row['name'],
                description=row['description'],
                permissions=row['permissions'],
                is_deleted=row['is_deleted']
            )
            roles.append(role)
        
        # Salva in cache
        if self.cache_service and roles:
            cache_key = f"{self.cache_prefix}:all"
            await self.cache_service.set(
                cache_key,
                [
                    {
                        'id': str(r.id),
                        'team_id': str(r.team_id),
                        'name': r.name,
                        'description': r.description,
                        'permissions': r.permissions,
                        'is_deleted': r.is_deleted
                    } for r in roles
                ],
                ttl=self.default_ttl
            )
        
        return roles
    
    async def get_all_by_team(self, team_id: UUID) -> list[RoleEntity]:
        # Cache per lista per team
        if self.cache_service:
            cache_key = f"{self.cache_prefix}:team:{team_id}"
            cached = await self.cache_service.get(cache_key)
            if cached:
                return [RoleEntity(**item) for item in cached]
        
        query = """SELECT id, team_id, name, description, permissions, is_deleted FROM roles WHERE team_id = %s AND is_deleted = FALSE"""
        params = (str(team_id),)
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_query(query, params)
        )
        
        roles = []
        for row in results:
            role = RoleEntity(
                id=row['id'],
                team_id=row['team_id'],
                name=row['name'],
                description=row['description'],
                permissions=row['permissions'],
                is_deleted=row['is_deleted']
            )
            roles.append(role)
        
        # Salva in cache
        if self.cache_service and roles:
            cache_key = f"{self.cache_prefix}:team:{team_id}"
            await self.cache_service.set(
                cache_key,
                [
                    {
                        'id': str(r.id),
                        'team_id': str(r.team_id),
                        'name': r.name,
                        'description': r.description,
                        'permissions': r.permissions,
                        'is_deleted': r.is_deleted
                    } for r in roles
                ],
                ttl=self.default_ttl
            )
        
        return roles
    
    async def find_by_name_and_in_default_team_id(self, name: str, team_id: str,defautl_team_id:str) -> Optional[RoleEntity] | None:
        # Controlla cache
        if self.cache_service:
            cache_key = f"{self.cache_prefix}:name:{name}:team:{team_id}:default_team:{defautl_team_id}"
            cached = await self.cache_service.get(cache_key)
            if cached:
                return RoleEntity(**cached)

        query = "SELECT id, team_id, name, description, permissions, is_deleted FROM roles WHERE name = %s and team_id = %s AND is_deleted = FALSE"
        params = (name, team_id)

        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_query(query, params)
        )
        
        if results:
            row = results[0]
            entity = RoleEntity(
                id=row['id'],
                team_id=row['team_id'],
                name=row['name'],
                description=row['description'],
                permissions=row['permissions'],
                is_deleted=row['is_deleted']
            )
            
            # Salva in cache
            if self.cache_service:
                cache_key = f"{self.cache_prefix}:name:{name}:team:{team_id}:default_team:{defautl_team_id}"
                await self.cache_service.set(
                    cache_key,
                    {
                        'id': str(entity.id),
                        'team_id': str(entity.team_id),
                        'name': entity.name,
                        'description': entity.description,
                        'permissions': entity.permissions,
                        'is_deleted': entity.is_deleted
                    },
                    ttl=self.default_ttl
                )
            
            return entity
        elif name in ['Admin', 'Member', 'Manager']:
            query = "SELECT id, team_id, name, description, permissions, is_deleted FROM roles WHERE team_id = %s AND is_deleted = FALSE"
            params = (defautl_team_id,)

            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                lambda: self.connection.execute_query(query, params)
            )
            row = results[0]
            entity = RoleEntity(
                id=row['id'],
                team_id=row['team_id'],
                name=row['name'],
                description=row['description'],
                permissions=row['permissions'],
                is_deleted=row['is_deleted']
            )
            
            # Salva in cache
            if self.cache_service:
                cache_key = f"{self.cache_prefix}:name:{name}:team:{team_id}:default_team:{defautl_team_id}"
                await self.cache_service.set(
                    cache_key,
                    {
                        'id': str(entity.id),
                        'team_id': str(entity.team_id),
                        'name': entity.name,
                        'description': entity.description,
                        'permissions': entity.permissions,
                        'is_deleted': entity.is_deleted
                    },
                    ttl=self.default_ttl
                )
            
            return entity
        return None