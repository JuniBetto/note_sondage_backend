from fastapi import APIRouter, Depends

from api.depends.dependency import get_role_repository, get_notification_service
from applications.dto.role.role_request_dto import RoleRequestDTO
from applications.dto.role.role_response_dto import RoleResponseDTO
from domain.use_case.role.create_use_case import CreateRoleUseCase
from domain.use_case.role.get_all_use_case import GetAllRolesUseCase
from domain.use_case.role.update_use_case import UpdateRoleUseCase
from domain.use_case.role.get_all_by_team_use_case import GetAllRolesByTeamUseCase
from domain.use_case.role.delete_use_case import DeleteRoleUseCase


router=APIRouter()

@router.get("/all",response_model=list[RoleResponseDTO])
async def get_all_roles( repo=Depends(get_role_repository)):
    return await GetAllRolesUseCase(repo).execute()

@router.post("/create/{team_id}",response_model=RoleResponseDTO)
async def create_role( team_id: str,
                       role: RoleRequestDTO, 
                       repo=Depends(get_role_repository),
                       notification_service=Depends(get_notification_service)):
    return await CreateRoleUseCase(repo, notification_service).execute(team_id, role)

@router.get("/all_by_team/{team_id}",response_model=list[RoleResponseDTO])
async def get_all_roles_by_team(team_id: str, repo=Depends(get_role_repository)):
    return await GetAllRolesByTeamUseCase(repo).execute(team_id)

@router.get("/find_by_name/{role_name}/{team_id}",response_model=RoleResponseDTO | None)
async def find_role_by_name(role_name: str, team_id: str, repo=Depends(get_role_repository)):
    role = await repo.find_by_name(role_name, team_id=team_id)
    if role:
        return RoleResponseDTO.from_entity(role)
    return None

@router.put("/update/{old_role_id}",response_model=RoleResponseDTO)
async def update_role(old_role_id: str, 
                      role: RoleRequestDTO, 
                      repo=Depends(get_role_repository),
                      notification_service=Depends(get_notification_service)):    
    return await UpdateRoleUseCase(repo, notification_service).execute(old_role_id, role)


@router.delete("/delete/{role_id}", response_model=RoleResponseDTO)
async def delete_role(role_id: str, 
                      repo=Depends(get_role_repository), 
                      notification_service=Depends(get_notification_service)):
    return await DeleteRoleUseCase(repo, notification_service).execute(role_id)



