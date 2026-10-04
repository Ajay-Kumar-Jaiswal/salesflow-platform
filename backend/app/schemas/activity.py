from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ActivityType(str, Enum):
    CALL = "CALL"
    EMAIL = "EMAIL"
    MEETING = "MEETING"
    NOTE = "NOTE"
    DEMO = "DEMO"
    OTHER = "OTHER"


class ActivityBase(BaseModel):
    activity_type: ActivityType
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class ActivityCreate(ActivityBase):
    customer_id: Optional[int] = None  # Inferred if provided in URL path


class ActivityResponse(ActivityBase):
    id: int
    customer_id: int
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    customer_name: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
