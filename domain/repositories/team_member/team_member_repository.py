from abc import ABC, abstractmethod
from typing import Optional

from domain.entities.team_member.team_member_entity import TeamMemberEntity


class TeamMemberRepository(ABC):
    @abstractmethod
    async def add_team_member(self, team_member: TeamMemberEntity) -> None:...

    @abstractmethod
    async def get_team_member_by_email(self, email: str) -> Optional[TeamMemberEntity]:...

    @abstractmethod
    async def get_all_team_members_by_team_id(self, team_id: str) -> list[TeamMemberEntity]:...

    @abstractmethod
    async def update_team_member(self, team_member: TeamMemberEntity) -> None:...
    
    @abstractmethod
    async def update_image_url(self, team_member_id: str, image_url: str) -> None:...
    
    @abstractmethod
    async def delete_team_member(self, email: str) -> None:...