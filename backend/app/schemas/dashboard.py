from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.schemas.customer import CustomerResponse
from app.schemas.activity import ActivityResponse
from app.schemas.follow_up import FollowUpResponse


class StageDistribution(BaseModel):
    stage: str
    count: int
    value: float


class DashboardSummary(BaseModel):
    total_customers: int
    open_opportunities: int
    won_opportunities: int
    pipeline_value: float
    won_revenue: float
    conversion_rate: float
    customer_status_distribution: Dict[str, int]
    pipeline_distribution: List[StageDistribution]
    upcoming_follow_ups: List[FollowUpResponse]
    recent_activities: List[ActivityResponse]
    recent_customers: List[CustomerResponse]
