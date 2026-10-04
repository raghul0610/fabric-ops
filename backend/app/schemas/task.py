from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    assignee_id: UUID


class TaskStateUpdate(BaseModel):
    state: str = Field(pattern="^(TODO|IN_PROGRESS|SUBMITTED|APPROVED|REJECTED)$")


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    event_id: UUID
    team_id: UUID
    title: str
    description: str | None
    assignee_id: UUID | None
    state: str
    created_at: datetime
    updated_at: datetime
