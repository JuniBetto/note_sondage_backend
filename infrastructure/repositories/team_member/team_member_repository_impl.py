import asyncio
from typing import Optional
from domain.entities.team_member.team_member_entity import TeamMemberEntity
from domain.repositories.team_member.team_member_repository import TeamMemberRepository
from infrastructure.database.postgres_connection import PostgresConnection
from domain.repositories.redis.redis_repository import RedisRepository


class TeamMemberRepositoryImpl(TeamMemberRepository):
    def __init__(self, db_connection: PostgresConnection, cache_service: Optional[RedisRepository] = None):
        self.connection = db_connection
        self.cache_service = cache_service
        self.cache_prefix = "team_member"
        self.default_ttl = 3600

    async def add_team_member(self, team_member: TeamMemberEntity) -> TeamMemberEntity:
        query = """
        INSERT INTO team_members (id, initialName, team_id, user_id, status, role_id, image_url, joined_at) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, initialName, team_id, user_id, status, role_id, image_url, joined_at"""

        params = (
            team_member.id, 
            team_member.initialName,
            team_member.team_id, 
            team_member.user_id, 
            team_member.status, 
            team_member.role_id, 
            team_member.image_url, 
            team_member.joined_at
        )

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.connection.execute_insert(
                    query, params, 
                    return_columns=['id', 'initialName', 'team_id', 'user_id', 'status', 'role_id', 'image_url', 'joined_at']
                )
            )
        except Exception as e:
            raise ValueError(f"Error inserting team member into database: {str(e)}")
        
        new_data = result['new']
        try:
            entity = TeamMemberEntity(
                id=new_data['id'],
                team_id=new_data['team_id'],
                user_id=new_data['user_id'],
                status=new_data['status'],
                role_id=new_data['role_id'],
                image_url=new_data['image_url'],
                file_name="",  # Placeholder, as file_name is not stored in DB
                joined_at=new_data['joined_at'],
                initialName=new_data['initialname']
            )
        except Exception as e:
            raise ValueError(f"Error creating team member entity from database result: {str(e)}")
        
        # Invalida cache dopo creazione
        if self.cache_service:
            await self.cache_service.invalidate_cache(f"{self.cache_prefix}:*")
        
        return entity

    async def get_team_member_by_email(self, email: str) -> Optional[TeamMemberEntity]:
        # Controlla cache
        if self.cache_service:
            cache_key = f"{self.cache_prefix}:email:{email}"
            cached = await self.cache_service.get(cache_key)
            if cached:
                return TeamMemberEntity(**cached)

        query = """
        SELECT tm.id, tm.team_id, tm.user_id, tm.status, tm.role_id, tm.image_url, tm.joined_at 
        FROM team_members tm
        JOIN users u ON tm.user_id = u.id
        WHERE u.email = %s
        """
        params = (email,)
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_query(query, params)
        )
        
        if results:
            row = results[0]
            entity = TeamMemberEntity(
                id=row['id'],
                team_id=row['team_id'],
                user_id=row['user_id'],
                status=row['status'],
                role_id=row['role_id'],
                image_url=row['image_url'],
                joined_at=row['joined_at']
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

    async def get_all_team_members_by_team_id(self, team_id: str) -> list[TeamMemberEntity]:
        # Cache per lista per team
        if self.cache_service:
            cache_key = f"{self.cache_prefix}:team:{team_id}"
            cached = await self.cache_service.get(cache_key)
            if cached:
                return [TeamMemberEntity(**item) for item in cached]
        
        query = """
        SELECT id, initialName, team_id, user_id, status, role_id, image_url, joined_at 
        FROM team_members WHERE team_id = %s
        """
        params = (team_id,)
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_query(query, params)
        )
        
        members = []
        for row in results:
            member = TeamMemberEntity(
                id=row['id'],
                team_id=row['team_id'],
                user_id=row['user_id'],
                status=row['status'],
                role_id=row['role_id'],
                image_url=row['image_url'],
                joined_at=row['joined_at'],
                file_name="",  # Placeholder, as file_name is not stored in DB
                initialName=row['initialname']
            )
            members.append(member)
        
        # Salva in cache
        if self.cache_service and members:
            cache_key = f"{self.cache_prefix}:team:{team_id}"
            await self.cache_service.set(
                cache_key,
                [m.to_dict() for m in members],
                ttl=self.default_ttl
            )
        
        return members

    async def update_team_member(self, team_member: TeamMemberEntity) -> TeamMemberEntity:
        query = """
        UPDATE team_members 
        SET status = %s, role_id = %s, image_url = %s 
        WHERE id = %s
        RETURNING id, team_id, user_id, status, role_id, image_url, joined_at"""

        old_values_query = """
        SELECT id, team_id, user_id, status, role_id, image_url, joined_at 
        FROM team_members WHERE id = %s
        """

        params = (team_member.status, team_member.role_id, team_member.image_url, team_member.id)
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_update(
                query, params, 
                return_columns=['id', 'initialName', 'team_id', 'user_id', 'status', 'role_id', 'image_url', 'joined_at']
                , get_old_values_query=old_values_query, get_old_params=(team_member.id,)
            )
        )

        updated_data = result['new']
        entity = TeamMemberEntity(
            id=updated_data['id'],
            team_id=updated_data['team_id'],
            user_id=updated_data['user_id'],
            status=updated_data['status'],
            role_id=updated_data['role_id'],
            image_url=updated_data['image_url'],
            joined_at=updated_data['joined_at'],
            file_name="",  # Placeholder, as file_name is not stored in DB
            initialName=updated_data['initialname']
        )
        
        # Invalida cache dopo update
        if self.cache_service:
            await self.cache_service.invalidate_cache(f"{self.cache_prefix}:*")
        
        return entity

    async def update_image_url(self, team_member_id: str, image_url: str) -> None:
        """Aggiorna solo l'image_url di un team member"""
        query = """
        UPDATE team_members 
        SET image_url = %s 
        WHERE id = %s
        """
        params = (image_url, team_member_id)
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.connection.execute_all_modify(query, params)
        )
        
        # Invalida cache dopo update
        if self.cache_service:
            await self.cache_service.invalidate_cache(f"{self.cache_prefix}:*")

    async def delete_team_member(self, member_id: str) -> Optional[TeamMemberEntity]:
        query = "DELETE FROM team_members WHERE id = %s"
        old_values_query = """
        SELECT id, initialName, team_id, user_id, status, role_id, image_url, joined_at 
        FROM team_members WHERE id = %s
        """
        params = (member_id,)
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_delete(query, params, old_values_query, params)
        )
        
        if results:
            row = results['old']
            entity = TeamMemberEntity(
                id=row['id'],
                team_id=row['team_id'],
                user_id=row['user_id'],
                status=row['status'],
                role_id=row['role_id'],
                image_url=row['image_url'],
                joined_at=row['joined_at'],
                file_name="",  # Placeholder, as file_name is not stored in DB
                initialName=row['initialname']
            )
            
            # Invalida cache dopo eliminazione
            if self.cache_service:
                await self.cache_service.invalidate_cache(f"{self.cache_prefix}:*")
            
            return entity
        
        return None

    async def find_by_name_and_user_id(self, team_id: str, user_id: str) -> Optional[TeamMemberEntity]:
        query = """
        SELECT tm.id, tm.initialName, tm.team_id, tm.user_id, tm.status, tm.role_id, tm.image_url, tm.joined_at 
        FROM team_members tm
        JOIN teams t ON tm.team_id = t.id
        WHERE t.id = %s AND tm.user_id = %s
        """
        params = (team_id, user_id)

        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_query(query, params)
        )

        if results:
            row = results[0]
            entity = TeamMemberEntity(
                id=row['id'],
                team_id=row['team_id'],
                user_id=row['user_id'],
                status=row['status'],
                role_id=row['role_id'],
                image_url=row['image_url'],
                joined_at=row['joined_at'],
                file_name="",  # Placeholder, as file_name is not stored in DB
                initialName=row['initialname']
            )
            return entity
        return None
