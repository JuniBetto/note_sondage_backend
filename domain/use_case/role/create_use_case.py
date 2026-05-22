from datetime import datetime
from uuid import uuid4
from applications.dto.role.role_request_dto import RoleRequestDTO
from applications.dto.role.role_response_dto import RoleResponseDTO
from domain.repositories.services.notification import Notification
from domain.entities.event.event_entity import EventEntity
from domain.exceptions.role.role_exception import RoleAlreadyExists
from domain.entities.role.role_entity import RoleEntity


class CreateRoleUseCase:
    def __init__(self, role_repository, notification_service: Notification):
        self.role_repository = role_repository
        self.notification_service = notification_service

    async def execute(self, team_id: str, dto: RoleRequestDTO) -> RoleResponseDTO:
        if await self.role_repository.find_by_name(dto.name, team_id=team_id):
            raise RoleAlreadyExists(dto.name)
        
        # Create a new role entity
        role = RoleEntity(id=uuid4(), team_id=team_id, name=dto.name, description=dto.description, permissions=dto.permissions)

        # Save the role using the repository
        created_role = await self.role_repository.create(role)

        # Notifica dell'evento di creazione
        eventEntity = EventEntity(
            name="Role Created",
            payload=created_role.to_dict(),
            occurred_at=datetime.now()
        )
        await self.notification_service.notify(eventEntity)

        return RoleResponseDTO.from_entity(created_role)