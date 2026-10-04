from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.dashboard import DashboardSummary
from app.services.dashboard_service import DashboardService
from app.core.dependencies import get_current_user_optional
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary, summary="Get CRM dashboard summary metrics")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Retrieve aggregated CRM metrics including total customers, open deals,
    pipeline value, won revenue, win rate, stage breakdown, upcoming tasks,
    and recent activity stream.
    """
    return DashboardService.get_summary(db, current_user=current_user)
