from datetime import datetime
from uuid import uuid4
from applications.dto.user.user_request_dto import UserRequestDTO
from applications.dto.user.user_response_dto import UserResponseDTO
from domain.repositories.services.notification import Notification
from domain.entities.event.event_entity import EventEntity
from domain.entities.user.user_enty import UserEntity


class CreateUserUseCase:
    def __init__(self, user_repository, notification_service: Notification):
        self.user_repository = user_repository
        self.notification_service = notification_service

    async def execute(self, dto: UserRequestDTO) -> UserResponseDTO:
        # Check if user already exists
        existing_user = await self.user_repository.find_by_email(dto.email)
        if existing_user:
            raise ValueError(f"User with email {dto.email} already exists")

        # Create a new user entity
        user = UserEntity(
            id=str(uuid4()),
            full_name=dto.full_name,
            email=dto.email,
            created_at=datetime.now(),
            is_active=dto.is_active if dto.is_active is not None else True
        )

        # Save the user using the repository
        created_user = await self.user_repository.create(user)

        # Notifica dell'evento di creazione
        event_entity = EventEntity(
            name="User Created",
            payload=created_user.to_dict(),
            occurred_at=datetime.now()
        )
        await self.notification_service.notify(event_entity)

        return UserResponseDTO.from_entity(created_user)
