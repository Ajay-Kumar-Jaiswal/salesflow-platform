from app.schemas.auth import LoginRequest, Token, TokenPayload
from app.schemas.user import UserRole, UserBase, UserCreate, UserUpdate, UserResponse
from app.schemas.customer import (
    CustomerStatus,
    CustomerBase,
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerPagination,
)
from app.schemas.activity import ActivityType, ActivityBase, ActivityCreate, ActivityResponse
from app.schemas.opportunity import (
    OpportunityStage,
    OpportunityBase,
    OpportunityCreate,
    OpportunityUpdate,
    OpportunityResponse,
)
from app.schemas.follow_up import FollowUpType, FollowUpBase, FollowUpCreate, FollowUpUpdate, FollowUpResponse
from app.schemas.dashboard import DashboardSummary, StageDistribution

__all__ = [
    "LoginRequest", "Token", "TokenPayload",
    "UserRole", "UserBase", "UserCreate", "UserUpdate", "UserResponse",
    "CustomerStatus", "CustomerBase", "CustomerCreate", "CustomerUpdate", "CustomerResponse", "CustomerPagination",
    "ActivityType", "ActivityBase", "ActivityCreate", "ActivityResponse",
    "OpportunityStage", "OpportunityBase", "OpportunityCreate", "OpportunityUpdate", "OpportunityResponse",
    "FollowUpType", "FollowUpBase", "FollowUpCreate", "FollowUpUpdate", "FollowUpResponse",
    "DashboardSummary", "StageDistribution"
]
