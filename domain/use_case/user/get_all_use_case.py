from applications.dto.user.user_response_dto import UserResponseDTO


class GetAllUsersUseCase:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    async def execute(self) -> list[UserResponseDTO]:
        users = await self.user_repository.get_all()
        return [
            UserResponseDTO.from_entity(user) for user in users
        ]
