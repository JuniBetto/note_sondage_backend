from applications.dto.user.user_response_dto import UserResponseDTO


class FindUserByEmailUseCase:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    async def execute(self, email: str) -> UserResponseDTO | None:
        user = await self.user_repository.find_by_email(email)
        if not user:
            return None
        
        return UserResponseDTO.from_entity(user)
