from fastapi import APIRouter, Depends

from api.depends.dependency import get_team_repository, get_notification_service
from applications.dto.team.team_request_dto import TeamRequestDTO, UpdateTeamRequestDTO
from applications.dto.team.team_response_dto import TeamResponseDTO, UpdateTeamResponseDTO
from domain.use_case.team.create_use_case import CreateTeamUseCase
from domain.use_case.team.update_use_case import UpdateTeamUseCase
from domain.use_case.team.delete_use_case import DeleteTeamUseCase
from domain.use_case.team.get_all_use_case import GetAllTeamsUseCase
from domain.use_case.team.find_by_id_use_case import FindTeamByIdUseCase
from domain.use_case.team.get_all_by_user_use_case import GetAllTeamsByUserUseCase


router = APIRouter()


@router.get("/all", response_model=list[TeamResponseDTO])
async def get_all_teams(repo=Depends(get_team_repository)):
    return await GetAllTeamsUseCase(repo).execute()


@router.get("/{team_id}", response_model=TeamResponseDTO | None)
async def get_team_by_id(team_id: str, repo=Depends(get_team_repository)):
    return await FindTeamByIdUseCase(repo).execute(team_id)


@router.post("/create/{created_by_user_id}", response_model=TeamResponseDTO)
async def create_team(
    created_by_user_id: str,
    team: TeamRequestDTO,
    repo=Depends(get_team_repository),
    notification_service=Depends(get_notification_service)
):
    return await CreateTeamUseCase(repo, notification_service).execute(team, created_by_user_id)


@router.put("/update/{team_id}", response_model=UpdateTeamResponseDTO)
async def update_team(
    team_id: str,
    team: UpdateTeamRequestDTO,
    repo=Depends(get_team_repository),
    notification_service=Depends(get_notification_service)
):
    return await UpdateTeamUseCase(repo, notification_service).execute(team_id, team)


@router.delete("/delete/{team_id}", response_model=TeamResponseDTO)
async def delete_team(
    team_id: str,
    repo=Depends(get_team_repository),
    notification_service=Depends(get_notification_service)
):
    return await DeleteTeamUseCase(repo, notification_service).execute(team_id)


@router.get("/all_by_user/{user_id}", response_model=list[TeamResponseDTO]|None)
async def get_teams_by_user(
    user_id: str,
    repo=Depends(get_team_repository),
):
    return await GetAllTeamsByUserUseCase(user_id=user_id, team_repository=repo).execute()