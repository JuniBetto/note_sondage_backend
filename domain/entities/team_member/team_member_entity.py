import base64
from datetime import datetime


class TeamMemberEntity:
    def __init__(self, id: str, team_id: str, user_id: str, status: str, role_id: str, image_url: str,
                  file_name: str, joined_at: datetime, initialName: str, image_bytes: bytes = None, image_file: bytes = None):
        self.id = id
        self.team_id = team_id
        self.user_id = user_id
        self.image_url = image_url
        self.status = status
        self.role_id = role_id
        self.joined_at = joined_at
        self.file_name = file_name
        self.image_bytes = image_bytes
        self.image_file = image_file
        self.initialName = initialName

    def to_dict(self):
        result = {
            "id": self.id,
            "team_id": self.team_id,
            "user_id": self.user_id,
            "status": self.status,
            "role_id": self.role_id,
            "image_url": self.image_url,
            "joined_at": self.joined_at,
            "file_name": self.file_name,
            'initialName':self.initialName
           
        }
         # Convert bytes to base64 for JSON serialization
        if self.image_bytes:
            result["image_bytes"] = base64.b64encode(self.image_bytes).decode('utf-8')
        
        if self.image_file:
            result["image_file"] = base64.b64encode(self.image_file).decode('utf-8')
            
        return result
    