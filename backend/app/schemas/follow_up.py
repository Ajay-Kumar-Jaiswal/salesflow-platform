from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class FollowUpType(str, Enum):
    CALL = "CALL"
    EMAIL = "EMAIL"
    MEETING = "MEETING"
    DEMO = "DEMO"
    OTHER = "OTHER"


class FollowUpBase(BaseModel):
    customer_id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    follow_up_type: FollowUpType = FollowUpType.CALL
    scheduled_at: datetime
    completed: bool = False


class FollowUpCreate(FollowUpBase):
    pass


class FollowUpUpdate(BaseModel):
    customer_id: Optional[int] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    follow_up_type: Optional[FollowUpType] = None
    scheduled_at: Optional[datetime] = None
    completed: Optional[bool] = None


class FollowUpResponse(FollowUpBase):
    id: int
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    customer_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
