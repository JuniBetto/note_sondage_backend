from fastapi import APIRouter, Depends

from api.depends.dependency import get_user_repository, get_notification_service
from applications.dto.user.user_request_dto import UserRequestDTO
from applications.dto.user.user_response_dto import UserFromTeamIdResponseDTO, UserResponseDTO
from domain.use_case.user.create_use_case import CreateUserUseCase
from domain.use_case.user.update_use_case import UpdateUserUseCase
from domain.use_case.user.delete_use_case import DeleteUserUseCase
from domain.use_case.user.get_all_use_case import GetAllUsersUseCase
from domain.use_case.user.find_by_id_use_case import FindUserByIdUseCase
from domain.use_case.user.find_by_email_use_case import FindUserByEmailUseCase
from domain.use_case.user.find_all_user_by_team_id import FindUserByTeamIdUseCase


router = APIRouter()


@router.get("/all", response_model=list[UserResponseDTO])
async def get_all_users(repo=Depends(get_user_repository)):
    return await GetAllUsersUseCase(repo).execute()


@router.get("/{user_id}", response_model=UserResponseDTO | None)
async def get_user_by_id(user_id: str, repo=Depends(get_user_repository)):
    return await FindUserByIdUseCase(repo).execute(user_id)

@router.get("/list_on_team/{team_id}", response_model=list[UserFromTeamIdResponseDTO] | None)
async def get_user_by_team_id(team_id: str, repo=Depends(get_user_repository)):
    return await FindUserByTeamIdUseCase(repo).execute(team_id)

@router.get("/email/{email}", response_model=UserResponseDTO | None)
async def get_user_by_email(email: str, repo=Depends(get_user_repository)):
    return await FindUserByEmailUseCase(repo).execute(email)


@router.post("/create", response_model=UserResponseDTO)
async def create_user(
    user: UserRequestDTO,
    repo=Depends(get_user_repository),
    notification_service=Depends(get_notification_service)
):
    return await CreateUserUseCase(repo, notification_service).execute(user)


@router.put("/update/{user_id}", response_model=UserResponseDTO)
async def update_user(
    user_id: str,
    user: UserRequestDTO,
    repo=Depends(get_user_repository),
    notification_service=Depends(get_notification_service)
):
    return await UpdateUserUseCase(repo, notification_service).execute(user_id, user)


@router.delete("/delete/{user_id}", response_model=UserResponseDTO)
async def delete_user(
    user_id: str,
    repo=Depends(get_user_repository),
    notification_service=Depends(get_notification_service)
):
    return await DeleteUserUseCase(repo, notification_service).execute(user_id)
