import asyncio
import uuid
from typing import Optional
from domain.entities.team.team_entity import TeamEntity, TeamEntityUpdated
from domain.repositories.team.team_repository import TeamRepository
from infrastructure.database.postgres_connection import PostgresConnection
from domain.repositories.redis.redis_repository import RedisRepository
from domain.entities.team_member.team_member_entity import TeamMemberEntity
from domain.entities.user.user_enty import UserEntity, UserEntityUpdated
from domain.entities.role.role_entity import RoleEntity


class TeamRepositoryImpl(TeamRepository):
    def __init__(self, db_connection: PostgresConnection, cache_service: Optional[RedisRepository] = None):
        self.connection = db_connection
        self.cache_service = cache_service
        self.cache_prefix = "team"
        self.default_ttl = 3600

    async def find_by_id(self, team_id: str) -> Optional[TeamEntity] | None:
        # Controlla cache
        if self.cache_service:
            cache_key = f"{self.cache_prefix}:id:{team_id}"
            cached = await self.cache_service.get(cache_key)
            if cached:
                return TeamEntity(**cached)

        query = "SELECT id, name, description, created_at, color, created_by_user_id, is_deleted FROM teams WHERE id = %s AND is_deleted = FALSE"
        params = (team_id,)
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_query(query, params)
        )
        
        if results:
            row = results[0]
            entity = TeamEntity(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                color=row['color'],
                created_at=row['created_at'],
                created_by_user_id=row['created_by_user_id'],
                is_deleted=row['is_deleted']
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
    

    async def get_all_by_user_id(self, user_id: str) -> list[TeamEntity]|None:
        query = """
        SELECT id, name, description, created_at, color, created_by_user_id, is_deleted 
        FROM teams 
        WHERE created_by_user_id = %s AND is_deleted = FALSE
        """
        params = (user_id,)
       
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_query(query, params)
        )


        teams = []
        for row in results:
            team = TeamEntity(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                color=row['color'],
                created_at=row['created_at'],
                created_by_user_id=row['created_by_user_id'],
                is_deleted=row['is_deleted']
            )
            teams.append(team)
        
        return teams

    async def create(self, team: TeamEntity) -> TeamEntity:
        query = """
        INSERT INTO teams (id, name, description, created_at, color, created_by_user_id, is_deleted) VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id, name, description, created_at, color, created_by_user_id, is_deleted"""
        params = (team.id, team.name, team.description, team.created_at, team.color, team.created_by_user_id, False)

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_insert(query, params, return_columns=['id', 'name', 'description', 'created_at', 'color', 'created_by_user_id', 'is_deleted'])
        )
        
        new_data = result['new']
        entity = TeamEntity(
            id=new_data['id'],
            name=new_data['name'],
            color=new_data['color'],
            description=new_data['description'],
            created_at=new_data['created_at'],
            created_by_user_id=new_data['created_by_user_id'],
            is_deleted=new_data['is_deleted']
        )
        
        # Invalida cache dopo creazione
        if self.cache_service:
            await self.cache_service.invalidate_cache(f"{self.cache_prefix}:*")
        
        return entity

    async def update(self, team: TeamEntityUpdated) -> TeamEntity:
        queryTeam = """
        UPDATE teams SET name = %s, description = %s, color = %s WHERE id = %s AND is_deleted = FALSE
        RETURNING id, name, description, created_at, color, created_by_user_id, is_deleted"""
       
        
        old_values_queryTeam = "SELECT id, name, description, color, created_at, created_by_user_id, is_deleted FROM teams WHERE id = %s" 


        params = (team.name, team.description, team.color, team.id)

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_update(queryTeam, params, return_columns=['id', 'name', 'description', 'created_at', 'color', 'created_by_user_id', 'is_deleted'], get_old_values_query=old_values_queryTeam, get_old_params=(team.id,))
        )
        list_members= []
        updated_data = result['new']
        team1 = TeamEntity(
            id=updated_data['id'],
            name=updated_data['name'],
            description=updated_data['description'],
            created_at=updated_data['created_at'],
            created_by_user_id=updated_data['created_by_user_id'],
            is_deleted=updated_data['is_deleted'],
            color=updated_data['color']
        )


     
        for member in team.list_member:

            queryRole = """
            SELECT id, team_id, description, name, permissions, is_deleted FROM roles WHERE name = %s AND team_id = %s AND is_deleted = FALSE"""


        # old_values_queryRole = "SELECT id, team_id, description, name, permissions, is_deleted FROM roles WHERE id = %s" 


            params = (member.role, team1.id)

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.connection.execute_query(queryRole, params,)
            )

            if not result:
                queryRole = """SELECT id, team_id, description, name, permissions, is_deleted FROM roles WHERE name = %s AND is_deleted = FALSE"""


                paramsNew = (member.role,)

                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: self.connection.execute_query(queryRole, paramsNew)
                )

            

            selected_data = result[0]  # Assuming you want the first matching role
            role = RoleEntity(
                id=selected_data['id'],
                team_id=selected_data['team_id'],
                description=selected_data['description'],
                name=selected_data['name'],
                permissions=selected_data['permissions'],
                is_deleted=selected_data['is_deleted']
            )

            #user update
            queryUserSelect = """
            SELECT id,email, full_name, is_active, created_at FROM users WHERE id = %s
            """
            paramsUser = (member.userId,)
            loop = asyncio.get_event_loop()
            resultUserSelect = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_query(queryUserSelect, paramsUser)
            )
            new_dataUser: any

            if not resultUserSelect:
                # User not found, handle accordingly
                queryUserInsert = """
                INSERT INTO users (email, full_name, is_active) VALUES (%s, %s, %s)
                RETURNING id, email, full_name, is_active, created_at
                """
                paramsUserInsert = (member.email, '', True)
                loop = asyncio.get_event_loop()
                resultUserInsert = await loop.run_in_executor(
                    None,
                    lambda: self.connection.execute_insert(queryUserInsert, paramsUserInsert, return_columns=['id', 'email', 'full_name', 'is_active', 'created_at'])
                )
                new_dataUser = resultUserInsert['new']
                entityUser = UserEntity(
                    id=new_dataUser['id'],
                    email=new_dataUser['email'],
                    full_name=new_dataUser['full_name'],
                    is_active=new_dataUser['is_active'],
                    created_at=new_dataUser['created_at']
                )
            elif [resultUserSelect[0]['email'].lower()] != [member.email.lower()]:
                queryUser = """
                UPDATE users
                SET email = %s 
                WHERE id = %s
                """
                old_values_queryUser = "SELECT id,email, full_name, is_active, created_at FROM users WHERE id = %s"
                paramsUser = (member.email, member.userId)

                loop = asyncio.get_event_loop()
                resultTeamMember = await loop.run_in_executor(
                None,
                lambda: self.connection.execute_update(queryUser, paramsUser, return_columns=['id', 'email', 'full_name', 'is_active', 'created_at'], get_old_values_query=old_values_queryUser, get_old_params=(entityTeamMember.user_id,))
                )

                new_dataUser = resultTeamMember['new']
                entityUser = UserEntity(
                    id=new_dataUser['id'],
                    email=new_dataUser['email'],
                    full_name=new_dataUser['full_name'],
                    is_active=new_dataUser['is_active'],
                    created_at=new_dataUser['created_at']
                )
            else:
                entityUser = UserEntity(
                    id=resultUserSelect[0]['id'],
                    email=resultUserSelect[0]['email'],
                    full_name=resultUserSelect[0]['full_name'],
                    is_active=resultUserSelect[0]['is_active'],
                    created_at=resultUserSelect[0]['created_at']
                )

            #team_member check
            queryTeamMemberCheck = "SELECT id FROM team_members WHERE id = %s"
            paramsTeamMemberCheck = (member.teamMember_id,) 
            loop = asyncio.get_event_loop()
            resultTeamMember = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_query(queryTeamMemberCheck, paramsTeamMemberCheck)
            )
            insert_dataTeamMember: any
            if not resultTeamMember:
                queryTeamMemberInsert = """
                INSERT INTO team_members (team_id, user_id, status, image_url, role_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, user_id, team_id, status, image_url, initialname, joined_at, role_id
                """
                teammemberId = uuid.uuid4()
                paramsTeamMemberInsert = (team1.id, entityUser.id, member.status, member.image_url, role.id)
                try:
                    loop = asyncio.get_event_loop()
                    resultTeamMemberInsert = await loop.run_in_executor(
                        None,
                        lambda: self.connection.execute_insert(queryTeamMemberInsert, paramsTeamMemberInsert, return_columns=['id', 'user_id','status', 'image_url', 'initialname', 'joined_at','role_id'])
                    )
                except Exception as e:
                    # Handle the exception (e.g., log it)
                    print(f"Error occurred: {e}")
                insert_dataTeamMember = resultTeamMemberInsert['new']
                entityTeamMember = TeamMemberEntity(
                    id=insert_dataTeamMember['id'],
                    team_id=insert_dataTeamMember['team_id'],
                    user_id=insert_dataTeamMember['user_id'],
                    status=insert_dataTeamMember['status'],
                    image_url=insert_dataTeamMember['image_url'],
                    initialName=insert_dataTeamMember['initialname'],
                    joined_at=insert_dataTeamMember['joined_at'],
                    role_id=insert_dataTeamMember['role_id'],
                    file_name=""
                )
            else:

                queryTeamMember = """
                UPDATE team_members SET status = %s,image_url = %s,role_id = %s
                WHERE id = %s"""
                old_values_queryTeamMember = "SELECT status,role_id, image_url,initialname,joined_at FROM team_members WHERE id = %s"
                paramsTeamMember = (member.status, member.image_url, role.id, member.teamMember_id)

                loop = asyncio.get_event_loop()
                resultTeamMember = await loop.run_in_executor(
                None,
                lambda: self.connection.execute_update(queryTeamMember, paramsTeamMember, return_columns=['id', 'user_id','status', 'image_url', 'initialname', 'joined_at','role_id'], get_old_values_query=old_values_queryTeamMember, get_old_params=(member.teamMember_id,))
                )

                insert_dataTeamMember = resultTeamMember['new']
                entityTeamMember = TeamMemberEntity(
                    id=insert_dataTeamMember['id'],
                    team_id=team1.id,
                    user_id=insert_dataTeamMember['user_id'],
                    status=insert_dataTeamMember['status'],
                    image_url=insert_dataTeamMember['image_url'],
                    initialName=insert_dataTeamMember['initialname'],
                    joined_at=insert_dataTeamMember['joined_at'],
                    role_id=insert_dataTeamMember['role_id'],
                    file_name=""
                )
                


            userEntityUpdated=UserEntityUpdated(
                id=entityUser.id,
                email=entityUser.email,
                full_name=entityUser.full_name,
                is_active=entityUser.is_active,
                created_at=entityUser.created_at,
                teamMember_id=entityTeamMember.id,
                status=entityTeamMember.status,
                role=entityTeamMember.role_id,
                image_url=entityTeamMember.image_url
            )
            list_members.append(userEntityUpdated)


        
        
        teamEntityUpdated=TeamEntityUpdated(
            id=team1.id,
            name=team1.name,
            description=team1.description,
            created_at=team1.created_at,
            created_by_user_id=team1.created_by_user_id,
            is_deleted=team1.is_deleted,
            color=team1.color,
            list_member=list_members
        )

                # Invalida cache dopo update
        if self.cache_service:
            await self.cache_service.invalidate_cache(f"{self.cache_prefix}:*")

        return teamEntityUpdated

    async def delete(self, team_id: str) -> Optional[TeamEntity]:
        """Soft delete: imposta is_deleted = TRUE invece di eliminare fisicamente"""
        # Prima verifica che esista e non sia già eliminato
        check_query = "SELECT id, name, description, color, created_at, created_by_user_id, is_deleted FROM teams WHERE id = %s AND is_deleted = FALSE"
        
        loop = asyncio.get_event_loop()
        existing = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_query(check_query, (team_id,))
        )
        
        if not existing:
            return None
        
        # Esegui soft delete
        query = """
        UPDATE teams SET is_deleted = TRUE WHERE id = %s AND is_deleted = FALSE
        RETURNING id, name, description, color, created_at, created_by_user_id, is_deleted"""
        params = (team_id,)
        
        result = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_query(query, params)
        )
        
        if result:
            row = result[0]
            entity = TeamEntity(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                color=row['color'],
                created_at=row['created_at'],
                created_by_user_id=row['created_by_user_id'],
                is_deleted=row['is_deleted']
            )
            
            # Invalida cache dopo eliminazione
            if self.cache_service:
                await self.cache_service.invalidate_cache(f"{self.cache_prefix}:*")
            
            return entity
        
        return None

    async def get_all(self) -> list[TeamEntity]:
        # Cache per lista completa
        if self.cache_service:
            cache_key = f"{self.cache_prefix}:all"
            cached = await self.cache_service.get(cache_key)
            if cached:
                return [TeamEntity(**item) for item in cached]
        
        query = """SELECT id, name, description, created_at, color, created_by_user_id, is_deleted FROM teams WHERE is_deleted = FALSE"""
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_query(query)
        )
        
        teams = []
        for row in results:
            team = TeamEntity(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                color=row['color'],
                created_at=row['created_at'],
                created_by_user_id=row['created_by_user_id'],
                is_deleted=row['is_deleted']
            )
            teams.append(team)
        
        # Salva in cache
        if self.cache_service and teams:
            cache_key = f"{self.cache_prefix}:all"
            await self.cache_service.set(
                cache_key,
                [t.to_dict() for t in teams],
                ttl=self.default_ttl
            )
        
        return teams

    async def find_by_name_and_user_id(self, name: str, user_id: str) -> Optional[TeamEntity]:
        query = """
        SELECT id, name, description, created_at, color, created_by_user_id, is_deleted
        FROM teams
        WHERE name = %s AND created_by_user_id = %s AND is_deleted = FALSE
        """
        params = (name, user_id)

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.connection.execute_query(query, params)
        )

        if result:
            row = result[0]
            return TeamEntity(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                color=row['color'],
                created_at=row['created_at'],
                created_by_user_id=row['created_by_user_id'],
                is_deleted=row['is_deleted']
            )

        return None