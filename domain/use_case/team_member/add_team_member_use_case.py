from datetime import datetime
from uuid import uuid4
from applications.dto.team_member.team_member_request_dto import TeamMemberRequestDTO
from applications.dto.team_member.team_member_response_dto import TeamMemberResponseDTO
from domain.repositories.services.notification import Notification
from domain.entities.event.event_entity import EventEntity
from domain.entities.team_member.team_member_entity import TeamMemberEntity
from domain.exceptions.team.team_exception import TeamAlreadyExists
from domain.repositories.role import role_repository


class AddTeamMemberUseCase:
    def __init__(self, team_member_repository, user_repository, role_repository, notification_service: Notification):
        self.team_member_repository = team_member_repository
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.notification_service = notification_service

    async def execute(self, dto: TeamMemberRequestDTO) -> TeamMemberResponseDTO:
        # Check if user exists
        user = await self.user_repository.find_by_email_if_not_exist_create(dto.user_email)
        if not user:
            raise ValueError(f"User with email {dto.user_email} not found")

        if await self.team_member_repository.find_by_name_and_user_id(dto.team_id, user.id):
            raise TeamAlreadyExists(user.email)
        default_team_id = '11111111-1111-1111-1111-111111111111'

        role = await self.role_repository.find_by_name_and_in_default_team_id(dto.role_id, dto.team_id, default_team_id)



        try:
            team_member = TeamMemberEntity(
                id=str(uuid4()),
                team_id=dto.team_id,
                user_id=user.id,
                status=dto.status.value if hasattr(dto.status, 'value') else dto.status,
                role_id=role.id,
                image_url=dto.image_url,
                joined_at=datetime.now(),
                image_bytes=dto.image_bytes,
                image_file=dto.image_file,
                file_name=dto.file_name,
                initialName=dto.initialName
            )
        except Exception as e:
            raise ValueError(f"Error creating team member entity: {str(e)}")

        # Save the team member using the repository
        created_member = await self.team_member_repository.add_team_member(team_member)

        # Notifica dell'evento di creazione
        event_entity = EventEntity(
            name="Team Member Added",
            payload=created_member.to_dict(),
            occurred_at=datetime.now()
        )
        await self.notification_service.notify(event_entity)

        return TeamMemberResponseDTO.from_entity(created_member)