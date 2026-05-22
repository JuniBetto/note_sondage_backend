from datetime import datetime
from typing import Optional


class UserEntity:
    def __init__(self, id: str, full_name: str, email: str, created_at: datetime, is_active: bool = True):
        self.id = id
        self.full_name = full_name
        self.email = email
        self.created_at = created_at
        self.is_active = is_active

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active
        }
    


# class UserEntityUpdated:
#     def __init__(self, id: str, full_name: str, email: str,status: str | None, created_at: datetime, role: str | None, teamMember_id: str, image_url: str | None, is_active: bool = True):
#         self.id = id
#         self.full_name = full_name
#         self.email = email
#         self.created_at = created_at
#         self.role = role
#         self.teamMember_id = teamMember_id
#         self.image_url = image_url
#         self.is_active = is_active
#         self.status = status


#     def to_dict(self):
#         return {
#             "id": self.id,
#             "full_name": self.full_name,
#             "email": self.email,
#             "teamMember_id": self.teamMember_id,
#             "image_url": self.image_url,
#             "created_at": self.created_at.isoformat(),
#             "is_active": self.is_active,
#             "role": self.role,
#             "status": self.status
#         }
    


class UserEntityUpdated(UserEntity):
    def __init__(self, id: str, full_name: str, email: str, created_at: datetime, is_active: bool = True, teamMember_id: Optional[str] = None, status: Optional[str] = None, role: Optional[str] = None,image_url: Optional[str] = None):
        super().__init__(id, full_name, email, created_at, is_active)
        self.teamMember_id = teamMember_id
        self.status = status
        self.role = role
        self.image_url = image_url

    def to_dict(self):
        data = super().to_dict()
        data["teamMember_id"] = self.teamMember_id
        data["status"] = self.status
        data["role"] = self.role
        data["image_url"] = self.image_url
        return data