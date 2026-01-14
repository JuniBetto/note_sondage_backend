from fastapi import APIRouter, Depends

from api.depends.dependency import get_role_repository
from applications.dto.role.role_request_dto import RoleRequestDTO
from applications.dto.role.role_response_dto import RoleResponseDTO
from domain.use_case.role.create_use_case import CreateRoleUseCase
from domain.use_case.role.get_all_use_case import GetAllRolesUseCase


router=APIRouter()

@router.get("/all",response_model=list[RoleResponseDTO])
def get_all_roles( repo=Depends(get_role_repository)):
    return GetAllRolesUseCase(repo).execute()

@router.post("/create",response_model=RoleResponseDTO)
def create_role( role: RoleRequestDTO, repo=Depends(get_role_repository)):
    return CreateRoleUseCase(repo).execute(role)

