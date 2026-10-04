from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status
from app.models.opportunity import Opportunity
from app.models.customer import Customer
from app.models.user import User
from app.schemas.opportunity import OpportunityCreate, OpportunityUpdate


class OpportunityService:
    @staticmethod
    def get_by_id(db: Session, opportunity_id: int) -> Opportunity:
        opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Opportunity not found with id: {opportunity_id}"
            )
        return opportunity

    @staticmethod
    def get_opportunities(
        db: Session,
        customer_id: Optional[int] = None,
        stage: Optional[str] = None,
        assigned_to: Optional[int] = None,
        current_user: Optional[User] = None
    ) -> List[Opportunity]:
        query = db.query(Opportunity)

        if current_user and current_user.role == "SALES_REP":
            query = query.filter(Opportunity.assigned_to == current_user.id)
        elif assigned_to is not None:
            query = query.filter(Opportunity.assigned_to == assigned_to)

        if customer_id is not None:
            query = query.filter(Opportunity.customer_id == customer_id)

        if stage and stage.strip():
            query = query.filter(Opportunity.stage == stage.strip().upper())

        return query.order_by(desc(Opportunity.created_at)).all()

    @staticmethod
    def create_opportunity(
        db: Session,
        opp_in: OpportunityCreate,
        current_user: Optional[User] = None
    ) -> Opportunity:
        customer = db.query(Customer).filter(Customer.id == opp_in.customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer not found with id: {opp_in.customer_id}"
            )

        assigned_id = opp_in.assigned_to
        if assigned_id is None and current_user:
            assigned_id = current_user.id

        stage_val = opp_in.stage.value if hasattr(opp_in.stage, "value") else str(opp_in.stage)

        opp = Opportunity(
            customer_id=opp_in.customer_id,
            title=opp_in.title.strip(),
            description=opp_in.description.strip() if opp_in.description else None,
            amount=opp_in.amount,
            stage=stage_val.upper(),
            probability=opp_in.probability,
            expected_close_date=opp_in.expected_close_date,
            assigned_to=assigned_id
        )
        db.add(opp)
        db.commit()
        db.refresh(opp)
        return opp

    @staticmethod
    def update_opportunity(
        db: Session,
        opp_id: int,
        opp_in: OpportunityUpdate,
        current_user: Optional[User] = None
    ) -> Opportunity:
        opp = OpportunityService.get_by_id(db, opp_id)

        if current_user and current_user.role == "SALES_REP":
            if opp.assigned_to and opp.assigned_to != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to edit an opportunity assigned to another representative"
                )

        if opp_in.customer_id is not None:
            customer = db.query(Customer).filter(Customer.id == opp_in.customer_id).first()
            if not customer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Customer not found with id: {opp_in.customer_id}"
                )
            opp.customer_id = opp_in.customer_id

        if opp_in.title is not None:
            opp.title = opp_in.title.strip()
        if opp_in.description is not None:
            opp.description = opp_in.description.strip() if opp_in.description else None
        if opp_in.amount is not None:
            opp.amount = opp_in.amount
        if opp_in.stage is not None:
            stage_val = opp_in.stage.value if hasattr(opp_in.stage, "value") else str(opp_in.stage)
            opp.stage = stage_val.upper()
        if opp_in.probability is not None:
            opp.probability = opp_in.probability
        if opp_in.expected_close_date is not None:
            opp.expected_close_date = opp_in.expected_close_date
        if opp_in.assigned_to is not None:
            opp.assigned_to = opp_in.assigned_to

        db.commit()
        db.refresh(opp)
        return opp

    @staticmethod
    def delete_opportunity(db: Session, opp_id: int, current_user: Optional[User] = None) -> bool:
        opp = OpportunityService.get_by_id(db, opp_id)

        if current_user and current_user.role == "SALES_REP":
            if opp.assigned_to and opp.assigned_to != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to delete an opportunity assigned to another representative"
                )

        db.delete(opp)
        db.commit()
        return True
