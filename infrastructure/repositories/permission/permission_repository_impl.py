from typing import Optional
from uuid import UUID
from domain.entities.permission.permission_entity import PermissionEntity
from domain.repositories.permission.permission_repository import PermissionRepository
from infrastructure.database.postgres_connection import PostgresConnection


class PermissionRepositoryImpl(PermissionRepository):
    def __init__(self, db_connection: PostgresConnection):
        self.connection = db_connection

    def get_all(self) -> list[PermissionEntity]:
        query="""SELECT id, code, description FROM permissions"""
        results = self.connection.execute_query(query)
        permissions = []
        for row in results:
            permission = PermissionEntity(
                id=row['id'],
                code=row['code'],
                description=row['description']
            )
            permissions.append(permission)
        return permissions

    def save(self, permission: PermissionEntity) -> PermissionEntity:
        query = """
        INSERT INTO permissions (id, code, description)
        VALUES (%s, %s, %s)
        RETURNING id, code, description
        """
        params = (str(permission.id), permission.code, permission.description)
        result = self.connection.execute_insert(query, params, return_columns=['id', 'code', 'description'])
        newData = result['new']
        return PermissionEntity(
            id=newData['id'],
            code=newData['code'],
            description=newData['description']
        )
    def find_by_id(self, permission_id: UUID) -> Optional[PermissionEntity]:
        query = "SELECT id, code, description FROM permissions WHERE id = %s"
        params = (str(permission_id),)
        results = self.connection.execute_query(query, params)
        if results:
            row = results[0]
            return PermissionEntity(
                id=row['id'],
                code=row['code'],
                description=row['description']
            )
        return None
    
    def find_by_code(self, code: str) -> Optional[PermissionEntity]:
        query = "SELECT id, code, description FROM permissions WHERE code = %s"
        params = (code,)
        results = self.connection.execute_query(query, params)
        if results:
            row = results[0]
            return PermissionEntity(
                id=row['id'],
                code=row['code'],
                description=row['description']
            )
        return None 
    
    def find_all(self, skip: int = 0, limit: int = 100) -> tuple[list[PermissionEntity], int]:
        query = "SELECT id, code, description FROM permissions ORDER BY code LIMIT %s OFFSET %s"
        count_query = "SELECT COUNT(*) FROM permissions"
        params = (limit, skip)
        results = self.connection.execute_query(query, params)
        count_result = self.connection.execute_query(count_query)
        total_count = count_result[0]['count'] if count_result else 0
        
        permissions = []
        for row in results:
            permission = PermissionEntity(
                id=row['id'],
                code=row['code'],
                description=row['description']
            )
            permissions.append(permission)
        return permissions, total_count
    
    def delete(self, permission_id: UUID) -> bool:
        query = "DELETE FROM permissions WHERE id = %s"
        old_values_query = "SELECT id, code, description FROM permissions WHERE id = %s"
        params = (str(permission_id),)
        results = self.connection.execute_delete(query, params,old_values_query, params)

        if results:
            row = results['old']
            return PermissionEntity(
                id=row['id'],
                code=row['code'],
                description=row['description']
            )
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