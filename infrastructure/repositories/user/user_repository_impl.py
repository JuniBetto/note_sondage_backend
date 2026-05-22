import asyncio
from datetime import datetime
from typing import Optional
import uuid
from domain.entities.user.user_enty import UserEntity, UserEntityUpdated
from domain.repositories.user.user_repository import UserRepository
from infrastructure.database.postgres_connection import PostgresConnection
from domain.repositories.redis.redis_repository import RedisRepository


class UserRepositoryImpl(UserRepository):
    def __init__(self, db_connection: PostgresConnection, cache_service: Optional[RedisRepository] = None):
        self.connection = db_connection
        self.cache_service = cache_service
        self.cache_prefix = "user"
        self.default_ttl = 3600

    async def find_by_id(self, user_id: str) -> Optional[UserEntity] | None:
        # Controlla cache
        if self.cache_service:
            cache_key = f"{self.cache_prefix}:id:{user_id}"
            cached = await self.cache_service.get(cache_key)
            if cached:
                return UserEntity(**cached)

        query = "SELECT id, full_name, email, created_at, is_active FROM users WHERE id = %s"
        params = (user_id,)
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_query(query, params)
        )
        
        if results:
            row = results[0]
            entity = UserEntity(
                id=row['id'],
                full_name=row['full_name'],
                email=row['email'],
                created_at=row['created_at'],
                is_active=row['is_active']
            )
            
            # Salva in cache
            if self.cache_service:
                await self.cache_service.set(
                    cache_key,
                    entity.to_dict(),
                    ttl=self.default_ttl
                )
            
            return entity
        return None

    async def find_by_email(self, email: str) -> Optional[UserEntity] | None:
        # Controlla cache
        if self.cache_service:
            cache_key = f"{self.cache_prefix}:email:{email}"
            cached = await self.cache_service.get(cache_key)
            if cached:
                return UserEntity(**cached)

        query = "SELECT id, full_name, email, created_at, is_active FROM users WHERE email = %s"
        params = (email,)
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_query(query, params)
        )
        
        if results:
            row = results[0]
            entity = UserEntity(
                id=row['id'],
                full_name=row['full_name'],
                email=row['email'],
                created_at=row['created_at'],
                is_active=row['is_active']
            )
            
            # Salva in cache
            if self.cache_service:
                await self.cache_service.set(
                    cache_key,
                    entity.to_dict(),
                    ttl=self.default_ttl
                )
            
            return entity
        return None

    async def find_by_email_if_not_exist_create(self, email: str) -> Optional[UserEntity] | None:
        user = await self.find_by_email(email)
        if user:
            return user

        # Se l'utente non esiste, creane uno nuovo
        new_user = UserEntity(
            id=str(uuid.uuid4()),
            full_name="",
            email=email,
            created_at=datetime.now(),
            is_active=False
        )
        await self.create(new_user)
        return new_user

    async def create(self, user: UserEntity) -> UserEntity:
        query = """
        INSERT INTO users (id, full_name, email, created_at, is_active) VALUES (%s, %s, %s, %s, %s)
        RETURNING id, full_name, email, created_at, is_active"""
        params = (user.id, user.full_name, user.email, user.created_at, user.is_active)
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_insert(query, params, return_columns=['id', 'full_name', 'email', 'created_at', 'is_active'])
        )
        
        new_data = result['new']
        entity = UserEntity(
            id=new_data['id'],
            full_name=new_data['full_name'],
            email=new_data['email'],
            created_at=new_data['created_at'],
            is_active=new_data['is_active']
        )
        
        # Invalida cache dopo creazione
        if self.cache_service:
            await self.cache_service.invalidate_cache(f"{self.cache_prefix}:*")
        
        return entity

    async def update(self, user: UserEntity) -> UserEntity:
        query = """
        UPDATE users SET full_name = %s, email = %s, is_active = %s WHERE id = %s
        RETURNING id, full_name, email, created_at, is_active"""
        old_values_query = "SELECT id, full_name, email, created_at, is_active FROM users WHERE id = %s"
        params = (user.full_name, user.email, user.is_active, user.id)
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_update(query, params, return_columns=['id', 'full_name', 'email', 'created_at', 'is_active'], get_old_values_query=old_values_query, get_old_params=(user.id,))
        )
        
        updated_data = result['new']
        entity = UserEntity(
            id=updated_data['id'],
            full_name=updated_data['full_name'],
            email=updated_data['email'],
            created_at=updated_data['created_at'],
            is_active=updated_data['is_active']
        )
        
        # Invalida cache dopo update
        if self.cache_service:
            await self.cache_service.invalidate_cache(f"{self.cache_prefix}:*")
        
        return entity

    async def delete(self, user_id: str) -> Optional[UserEntity]:
        query = "DELETE FROM users WHERE id = %s"
        old_values_query = "SELECT id, full_name, email, created_at, is_active FROM users WHERE id = %s"
        params = (user_id,)
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_delete(query, params, old_values_query, params)
        )
        
        if results:
            row = results['old']
            entity = UserEntity(
                id=row['id'],
                full_name=row['full_name'],
                email=row['email'],
                created_at=row['created_at'],
                is_active=row['is_active']
            )
            
            # Invalida cache dopo eliminazione
            if self.cache_service:
                await self.cache_service.invalidate_cache(f"{self.cache_prefix}:*")
            
            return entity
        
        return None

    async def get_all(self) -> list[UserEntity]:
        # Cache per lista completa
        if self.cache_service:
            cache_key = f"{self.cache_prefix}:all"
            cached = await self.cache_service.get(cache_key)
            if cached:
                return [UserEntity(**item) for item in cached]
        
        query = """SELECT id, full_name, email, created_at, is_active FROM users"""
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_query(query)
        )
        
        users = []
        for row in results:
            user = UserEntity(
                id=row['id'],
                full_name=row['full_name'],
                email=row['email'],
                created_at=row['created_at'],
                is_active=row['is_active']
            )
            users.append(user)
        
        # Salva in cache
        if self.cache_service and users:
            cache_key = f"{self.cache_prefix}:all"
            await self.cache_service.set(
                cache_key,
                [u.to_dict() for u in users],
                ttl=self.default_ttl
            )
        
        return users

    async def find_all_by_team_id(self, team_id: str) -> list[UserEntityUpdated] | None:
        query = """
        SELECT u.id, u.full_name, u.email, u.created_at, u.is_active, tm.id AS teamMember_id, tm.image_url, r.name as role, tm.status
        FROM users u
        JOIN team_members tm ON u.id = tm.user_id
        join roles r ON r.id = tm.role_id
        WHERE tm.team_id = %s
        """
        params = (team_id,)
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_query(query, params)
        )
        
        if results:
            users = []
            for row in results:
                user = UserEntityUpdated(
                    id=row['id'],
                    full_name=row['full_name'],
                    email=row['email'],
                    created_at=row['created_at'],
                    is_active=row['is_active'],
                    teamMember_id=row['teammember_id'],
                    image_url=row['image_url'],
                    role=row['role'],
                    status=row['status']
                )
                users.append(user)
            return users
        
        return None
