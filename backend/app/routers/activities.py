from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.activity import ActivityCreate, ActivityResponse
from app.services.activity_service import ActivityService
from app.core.dependencies import get_current_user_optional
from app.models.user import User

router = APIRouter(tags=["Activities"])


def _map_activity_response(act) -> ActivityResponse:
    return ActivityResponse(
        id=act.id,
        customer_id=act.customer_id,
        user_id=act.user_id,
        user_name=act.user.name if act.user else None,
        customer_name=act.customer.name if act.customer else None,
        activity_type=act.activity_type,
        title=act.title,
        description=act.description,
        created_at=act.created_at
    )


# Nested customer routes
@router.get("/customers/{customer_id}/activities", response_model=List[ActivityResponse], summary="Get activities for a customer")
def get_customer_activities(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """Retrieve chronologically ordered activities (newest first) for a customer."""
    activities = ActivityService.get_customer_activities(db, customer_id)
    return [_map_activity_response(a) for a in activities]


@router.post("/customers/{customer_id}/activities", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED, summary="Log an activity for a customer")
def create_customer_activity(
    customer_id: int,
    act_in: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Record an interaction or note (CALL, EMAIL, MEETING, DEMO, NOTE, OTHER) for a customer."""
    act = ActivityService.create_activity(db, customer_id, act_in, current_user=current_user)
    return _map_activity_response(act)


# Top-level activity routes
@router.get("/activities/{activity_id}", response_model=ActivityResponse, summary="Get activity by ID")
def get_activity(
    activity_id: int,
    db: Session = Depends(get_db)
):
    """Retrieve details of a single activity."""
    act = ActivityService.get_by_id(db, activity_id)
    return _map_activity_response(act)


@router.delete("/activities/{activity_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an activity")
def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Remove an activity from the CRM."""
    ActivityService.delete_activity(db, activity_id, current_user=current_user)
    return None
