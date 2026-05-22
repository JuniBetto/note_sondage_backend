from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel




class TeamMemberStatus(str, Enum):
    INVITED = "INVITED"
    ACTIVATE = "ACTIVATE"
    SUSPENDED = "SUSPENDED"
    DEACTIVATED = "DEACTIVATED"
    PENDING = "PENDING"


class TeamMemberRequestDTO(BaseModel):
    team_id: str
    user_email: str
    image_url: Optional[str] = None
    status: TeamMemberStatus = TeamMemberStatus.INVITED
    role_id: str
    file_name: str
    image_bytes: Optional[bytes] = None
    image_file: Optional[bytes] = None
    initialName: Optional[str] = None