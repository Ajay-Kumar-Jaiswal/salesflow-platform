from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.opportunity import OpportunityCreate, OpportunityUpdate, OpportunityResponse
from app.services.opportunity_service import OpportunityService
from app.core.dependencies import get_current_user_optional
from app.models.user import User

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])


def _map_opportunity_response(opp) -> OpportunityResponse:
    return OpportunityResponse(
        id=opp.id,
        customer_id=opp.customer_id,
        title=opp.title,
        description=opp.description,
        amount=opp.amount,
        stage=opp.stage,
        probability=opp.probability,
        expected_close_date=opp.expected_close_date,
        assigned_to=opp.assigned_to,
        customer_name=opp.customer.name if opp.customer else None,
        assigned_user_name=opp.assigned_user.name if opp.assigned_user else None,
        created_at=opp.created_at,
        updated_at=opp.updated_at
    )


@router.get("", response_model=List[OpportunityResponse], summary="List opportunities / deals")
def list_opportunities(
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    stage: Optional[str] = Query(None, description="Filter by opportunity stage"),
    assigned_to: Optional[int] = Query(None, description="Filter by assigned user ID"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Retrieve deals for the sales pipeline and Kanban board."""
    opps = OpportunityService.get_opportunities(
        db=db,
        customer_id=customer_id,
        stage=stage,
        assigned_to=assigned_to,
        current_user=current_user
    )
    return [_map_opportunity_response(o) for o in opps]


@router.get("/{opportunity_id}", response_model=OpportunityResponse, summary="Get opportunity by ID")
def get_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db)
):
    """Retrieve full details of a specific deal/opportunity."""
    opp = OpportunityService.get_by_id(db, opportunity_id)
    return _map_opportunity_response(opp)


@router.post("", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED, summary="Create an opportunity")
def create_opportunity(
    opp_in: OpportunityCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Create a new sales opportunity linked to a customer."""
    opp = OpportunityService.create_opportunity(db, opp_in, current_user=current_user)
    return _map_opportunity_response(opp)


@router.put("/{opportunity_id}", response_model=OpportunityResponse, summary="Update an opportunity")
def update_opportunity(
    opportunity_id: int,
    opp_in: OpportunityUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Update opportunity attributes, such as stage, amount, probability, or close date."""
    opp = OpportunityService.update_opportunity(db, opportunity_id, opp_in, current_user=current_user)
    return _map_opportunity_response(opp)


@router.delete("/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an opportunity")
def delete_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Remove an opportunity from the system."""
    OpportunityService.delete_opportunity(db, opportunity_id, current_user=current_user)
    return None
