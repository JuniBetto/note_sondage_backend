from typing import Optional
from uuid import UUID
from domain.entities.role.role_entity import RoleEntity
from domain.repositories.role.role_repository import RoleRepository
from infrastructure.database.postgres_connection import PostgresConnection


class RoleRepositoryImpl(RoleRepository):
    def __init__(self, db_connection: PostgresConnection):
        self.connection = db_connection

    def _find_by_id(self, role_id: UUID) -> Optional[RoleEntity] | None:
        query = "SELECT id, team_id, name, description FROM roles WHERE id = %s"
        params = (str(role_id),)
        results = self.connection.execute_query(query, params)
        if results:
            row = results[0]
            return RoleEntity(
                id=row['id'],
                team_id=row['team_id'],
                name=row['name'],
                description=row['description']
            )
        return None

    def create(self, role: RoleEntity) -> RoleEntity:
        query = """
        INSERT INTO roles (id, team_id, name, description) values (%s, %s, %s, %s)
        RETURNING id, team_id, name, description"""
        params = (str(role.id), str(role.team_id), role.name, role.description)
        result = self.connection.execute_insert(query, params, return_columns=['id', 'team_id', 'name', 'description'])
        newData = result['new']
        return RoleEntity(
            id=newData['id'],
            team_id=newData['team_id'],
            name=newData['name'],
            description=newData['description']
        )
    
    def find_by_name(self, name: str) -> Optional[RoleEntity] | None:
        query = "SELECT id, team_id, name, description FROM roles WHERE name = %s"
        params = (name,)
        results = self.connection.execute_query(query, params)
        if results:
            row = results[0]
            return RoleEntity(
                id=row['id'],
                team_id=row['team_id'],
                name=row['name'],
                description=row['description']
            )
        return None

    def update(self, role: RoleEntity) -> RoleEntity:
        # Implementation to update an existing RoleEntity in the database
        pass

    def delete(self, role_id: UUID) -> RoleEntity:
        # Implementation to delete a RoleEntity by its ID from the database
        pass

    def get_all(self) -> list[RoleEntity]:
        query = """SELECT id, team_id, name, description FROM roles"""
        results = self.connection.execute_query(query)
        roles = list[RoleEntity]()
        for row in results:
            role = RoleEntity(
                id=row['id'],
                team_id=row['team_id'],
                name=row['name'],
                description=row['description']
            )
            roles.append(role)
        return roles