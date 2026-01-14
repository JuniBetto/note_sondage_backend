# domain/repositories/permission_repository.py
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
from uuid import UUID

from domain.entities.permission.permission_entity import PermissionEntity


class PermissionRepository(ABC):
    """Interfaccia del repository - solo nel dominio"""
    
    @abstractmethod
    def get_all(self, ) -> list[PermissionEntity]:
        pass

    @abstractmethod
    def save(self, permission: PermissionEntity) -> PermissionEntity:
        pass
    
    @abstractmethod
    def find_by_id(self, permission_id: UUID) -> Optional[PermissionEntity]:
        pass
    
    @abstractmethod
    def find_by_code(self, code: str) -> Optional[PermissionEntity]:
        pass
    
    @abstractmethod
    def find_all(self, skip: int = 0, limit: int = 100) -> Tuple[List[PermissionEntity], int]:
        pass
    
    @abstractmethod
    def delete(self, permission_id: UUID) -> bool:
        pass
    
    @abstractmethod
    def exists_by_code(self, code: str, exclude_id: Optional[UUID] = None) -> bool:
        pass