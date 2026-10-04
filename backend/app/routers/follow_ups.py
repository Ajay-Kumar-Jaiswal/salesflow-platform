from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.follow_up import FollowUpCreate, FollowUpUpdate, FollowUpResponse
from app.services.follow_up_service import FollowUpService
from app.core.dependencies import get_current_user_optional
from app.models.user import User

router = APIRouter(prefix="/follow-ups", tags=["Follow-ups"])


def _map_follow_up_response(fu) -> FollowUpResponse:
    return FollowUpResponse(
        id=fu.id,
        customer_id=fu.customer_id,
        user_id=fu.user_id,
        user_name=fu.user.name if fu.user else None,
        customer_name=fu.customer.name if fu.customer else None,
        title=fu.title,
        description=fu.description,
        follow_up_type=fu.follow_up_type,
        scheduled_at=fu.scheduled_at,
        completed=fu.completed,
        created_at=fu.created_at,
        updated_at=fu.updated_at
    )


@router.get("", response_model=List[FollowUpResponse], summary="List scheduled follow-ups")
def list_follow_ups(
    filter_status: str = Query("all", description="Filter by status: 'today', 'upcoming', 'completed', 'all'"),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    user_id: Optional[int] = Query(None, description="Filter by assigned user ID"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Retrieve follow-ups categorized by today, upcoming, or completed."""
    fus = FollowUpService.get_follow_ups(
        db=db,
        filter_status=filter_status,
        customer_id=customer_id,
        user_id=user_id,
        current_user=current_user
    )
    return [_map_follow_up_response(f) for f in fus]


@router.get("/{follow_up_id}", response_model=FollowUpResponse, summary="Get follow-up by ID")
def get_follow_up(
    follow_up_id: int,
    db: Session = Depends(get_db)
):
    """Retrieve details of a single scheduled follow-up."""
    fu = FollowUpService.get_by_id(db, follow_up_id)
    return _map_follow_up_response(fu)


@router.post("", response_model=FollowUpResponse, status_code=status.HTTP_201_CREATED, summary="Schedule a follow-up")
def create_follow_up(
    fu_in: FollowUpCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Schedule a call, email, meeting, demo, or reminder for a customer."""
    fu = FollowUpService.create_follow_up(db, fu_in, current_user=current_user)
    return _map_follow_up_response(fu)


@router.put("/{follow_up_id}", response_model=FollowUpResponse, summary="Update follow-up or mark completed")
def update_follow_up(
    follow_up_id: int,
    fu_in: FollowUpUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Update follow-up details or toggle its completed state."""
    fu = FollowUpService.update_follow_up(db, follow_up_id, fu_in, current_user=current_user)
    return _map_follow_up_response(fu)


@router.delete("/{follow_up_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a follow-up")
def delete_follow_up(
    follow_up_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Remove a scheduled follow-up task."""
    FollowUpService.delete_follow_up(db, follow_up_id, current_user=current_user)
    return None
