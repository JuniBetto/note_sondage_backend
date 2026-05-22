from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse

from api.depends.dependency import get_role_repository, get_team_member_repository, get_user_repository, get_notification_service, get_profile_image_service
from applications.dto.team_member.team_member_request_dto import TeamMemberRequestDTO
from applications.dto.team_member.team_member_response_dto import TeamMemberResponseDTO
from domain.use_case.team_member.add_team_member_use_case import AddTeamMemberUseCase
from domain.use_case.team_member.update_team_member_use_case import UpdateTeamMemberUseCase
from domain.use_case.team_member.delete_team_member_use_case import DeleteTeamMemberUseCase
from domain.use_case.team_member.get_all_by_team_use_case import GetAllTeamMembersByTeamUseCase
from domain.use_case.team_member.get_by_email_use_case import GetTeamMemberByEmailUseCase
from domain.services.profile_image_service import ProfileImageService
import io


router = APIRouter()


@router.get("/team/{team_id}", response_model=list[TeamMemberResponseDTO])
async def get_all_team_members_by_team(
    team_id: str,
    team_member_repo=Depends(get_team_member_repository),
    user_repo=Depends(get_user_repository)
):
    return await GetAllTeamMembersByTeamUseCase(team_member_repo, user_repo).execute(team_id)


@router.get("/email/{email}", response_model=TeamMemberResponseDTO | None)
async def get_team_member_by_email(
    email: str,
    repo=Depends(get_team_member_repository)
):
    return await GetTeamMemberByEmailUseCase(repo).execute(email)


@router.post("/add", response_model=TeamMemberResponseDTO)
async def add_team_member(
    team_member: TeamMemberRequestDTO,
    team_member_repo=Depends(get_team_member_repository),
    role_repo=Depends(get_role_repository),
    user_repo=Depends(get_user_repository),
    notification_service=Depends(get_notification_service)
):
    return await AddTeamMemberUseCase(team_member_repo, user_repo, role_repo, notification_service).execute(team_member)


@router.put("/update/{member_email}", response_model=TeamMemberResponseDTO)
async def update_team_member(
    member_email: str,
    team_member: TeamMemberRequestDTO,
    repo=Depends(get_team_member_repository),
    notification_service=Depends(get_notification_service)
):
    return await UpdateTeamMemberUseCase(repo, notification_service).execute(member_email, team_member)


@router.delete("/delete/{member_id}/{member_email}", response_model=TeamMemberResponseDTO)
async def delete_team_member(
    member_id: str,
    member_email: str,
    repo=Depends(get_team_member_repository),
    notification_service=Depends(get_notification_service)
):
    return await DeleteTeamMemberUseCase(repo, notification_service).execute(member_id, member_email)


# ============ PROFILE IMAGE ENDPOINTS ============

@router.post("/{member_id}/profile-image", response_model=dict)
async def upload_profile_image(
    member_id: str,
    file: UploadFile = File(...),
    profile_image_service: ProfileImageService = Depends(get_profile_image_service)
):
    """
    Upload o aggiorna l'immagine profilo di un team member.
    Accetta formati: JPEG, PNG, GIF, WebP
    L'immagine viene automaticamente ottimizzata e convertita in JPEG.
    """
    # Validazione tipo file
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo file non supportato. Tipi accettati: {', '.join(allowed_types)}"
        )
    
    # Leggi il contenuto del file
    file_content = await file.read()
    
    try:
        # Upload dell'immagine
        image_url = await profile_image_service.upload_profile_image(
            entity_type="team_member",
            entity_id=member_id,
            image_bytes=file_content
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante l'upload dell'immagine: {str(e)}")    
    

    return {"image_url": image_url, "message": "Immagine profilo caricata con successo"}


@router.get("/{member_id}/profile-image")
async def get_profile_image(
    member_id: str,
    profile_image_service: ProfileImageService = Depends(get_profile_image_service)
):
    """
    Ottieni l'immagine profilo di un team member.
    """
    image_data = await profile_image_service.get_profile_image(
        entity_type="team_member",
        entity_id=member_id
    )
    
    if not image_data:
        raise HTTPException(status_code=404, detail="Immagine profilo non trovata")
    
    return StreamingResponse(
        io.BytesIO(image_data),
        media_type="image/jpeg"
    )


@router.get("/{member_id}/profile-image/url", response_model=dict)
async def get_profile_image_url(
    member_id: str,
    profile_image_service: ProfileImageService = Depends(get_profile_image_service)
):
    """
    Ottieni l'URL dell'immagine profilo di un team member.
    L'URL è valido per 1 ora.
    """
    image_url = await profile_image_service.get_profile_image_url(
        entity_type="team_member",
        entity_id=member_id
    )
    
    if not image_url:
        raise HTTPException(status_code=404, detail="Immagine profilo non trovata")
    
    return {"image_url": image_url}


@router.delete("/{member_id}/profile-image", response_model=dict)
async def delete_profile_image(
    member_id: str,
    profile_image_service: ProfileImageService = Depends(get_profile_image_service)
):
    """
    Elimina l'immagine profilo di un team member.
    """
    deleted = await profile_image_service.delete_profile_image(
        entity_type="team_member",
        entity_id=member_id
    )
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Immagine profilo non trovata")
    
    return {"message": "Immagine profilo eliminata con successo"}