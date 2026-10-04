from datetime import datetime
from enum import Enum
from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class CustomerStatus(str, Enum):
    LEAD = "LEAD"
    CONTACTED = "CONTACTED"
    QUALIFIED = "QUALIFIED"
    PROPOSAL = "PROPOSAL"
    NEGOTIATION = "NEGOTIATION"
    WON = "WON"
    LOST = "LOST"
    INACTIVE = "INACTIVE"
    ACTIVE = "ACTIVE"  # Legacy compatibility support


class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    company: Optional[str] = Field(None, max_length=150)
    industry: Optional[str] = Field(None, max_length=100)
    status: CustomerStatus = CustomerStatus.LEAD
    source: Optional[str] = Field(None, max_length=100)
    assigned_to: Optional[int] = None
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    company: Optional[str] = Field(None, max_length=150)
    industry: Optional[str] = Field(None, max_length=100)
    status: Optional[CustomerStatus] = None
    source: Optional[str] = Field(None, max_length=100)
    assigned_to: Optional[int] = None
    notes: Optional[str] = None


class CustomerResponse(CustomerBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    assigned_user_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CustomerPagination(BaseModel):
    items: List[CustomerResponse]
    total: int
    page: int
    page_size: int
    pages: int
