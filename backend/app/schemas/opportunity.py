from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class OpportunityStage(str, Enum):
    LEAD = "LEAD"
    CONTACTED = "CONTACTED"
    QUALIFIED = "QUALIFIED"
    PROPOSAL = "PROPOSAL"
    NEGOTIATION = "NEGOTIATION"
    WON = "WON"
    LOST = "LOST"


class OpportunityBase(BaseModel):
    customer_id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    amount: float = Field(default=0.0, ge=0.0)
    stage: OpportunityStage = OpportunityStage.LEAD
    probability: float = Field(default=10.0, ge=0.0, le=100.0)
    expected_close_date: Optional[datetime] = None
    assigned_to: Optional[int] = None


class OpportunityCreate(OpportunityBase):
    pass


class OpportunityUpdate(BaseModel):
    customer_id: Optional[int] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    amount: Optional[float] = Field(None, ge=0.0)
    stage: Optional[OpportunityStage] = None
    probability: Optional[float] = Field(None, ge=0.0, le=100.0)
    expected_close_date: Optional[datetime] = None
    assigned_to: Optional[int] = None


class OpportunityResponse(OpportunityBase):
    id: int
    customer_name: Optional[str] = None
    assigned_user_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
