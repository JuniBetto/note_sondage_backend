

from fastapi import APIRouter, Depends


from api.depends.dependency import get_notification_service, get_permission_repository
from domain.use_case.permission.delete_use_case import DeletePermissionUseCase
from applications.dto.permission.permission_request_dto import PermissionRequestDTO
from domain.use_case.permission.create_use_case import CreatePermissionUseCase
from domain.use_case.permission.get_all_use_case import GetAllPermissionsUseCase
from applications.dto.permission.permission_response_dto import PermissionResponseDTO


router=APIRouter()

@router.get("/all",response_model=list[PermissionResponseDTO])
async def get_all_permissions( repo=Depends(get_permission_repository)):
    return await GetAllPermissionsUseCase(repo).execute()

@router.post("/create",response_model=PermissionResponseDTO)
async def create_permission( permission: PermissionRequestDTO,
                             repo=Depends(get_permission_repository),
                             notification_service=Depends(get_notification_service)):
    return await CreatePermissionUseCase(repo, notification_service).execute(permission)

@router.delete("/delete/{permission_id}", response_model=PermissionResponseDTO)
async def delete_permission(permission_id: str, 
                            repo=Depends(get_permission_repository), 
                            notification_service=Depends(get_notification_service)):
    return await DeletePermissionUseCase(repo, notification_service).execute(permission_id)