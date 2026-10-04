from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TeamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class TeamMemberAdd(BaseModel):
    user_id: UUID
    membership_role: str = Field(default="MEMBER", pattern="^(LEAD|MEMBER)$")


class TeamMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    team_id: UUID
    user_id: UUID
    membership_role: str
    created_at: datetime


class TeamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    event_id: UUID
    name: str
    created_at: datetime
