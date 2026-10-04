from datetime import datetime, timezone, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from fastapi import HTTPException, status
from app.models.follow_up import FollowUp
from app.models.customer import Customer
from app.models.user import User
from app.schemas.follow_up import FollowUpCreate, FollowUpUpdate


class FollowUpService:
    @staticmethod
    def get_by_id(db: Session, follow_up_id: int) -> FollowUp:
        follow_up = db.query(FollowUp).filter(FollowUp.id == follow_up_id).first()
        if not follow_up:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Follow-up not found with id: {follow_up_id}"
            )
        return follow_up

    @staticmethod
    def get_follow_ups(
        db: Session,
        filter_status: str = "all",
        customer_id: Optional[int] = None,
        user_id: Optional[int] = None,
        current_user: Optional[User] = None
    ) -> List[FollowUp]:
        query = db.query(FollowUp)

        if current_user and current_user.role == "SALES_REP":
            query = query.filter(FollowUp.user_id == current_user.id)
        elif user_id is not None:
            query = query.filter(FollowUp.user_id == user_id)

        if customer_id is not None:
            query = query.filter(FollowUp.customer_id == customer_id)

        now = datetime.now(timezone.utc)
        start_of_today = datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=timezone.utc)
        end_of_today = start_of_today + timedelta(days=1)

        filter_lower = filter_status.lower()
        if filter_lower == "today":
            query = query.filter(
                FollowUp.scheduled_at >= start_of_today,
                FollowUp.scheduled_at < end_of_today,
                FollowUp.completed == False
            ).order_by(asc(FollowUp.scheduled_at))
        elif filter_lower == "upcoming":
            query = query.filter(
                FollowUp.scheduled_at >= end_of_today,
                FollowUp.completed == False
            ).order_by(asc(FollowUp.scheduled_at))
        elif filter_lower == "completed":
            query = query.filter(FollowUp.completed == True).order_by(desc(FollowUp.updated_at))
        else:
            # "all" or any other value
            query = query.order_by(asc(FollowUp.scheduled_at))

        return query.all()

    @staticmethod
    def create_follow_up(
        db: Session,
        fu_in: FollowUpCreate,
        current_user: Optional[User] = None
    ) -> FollowUp:
        customer = db.query(Customer).filter(Customer.id == fu_in.customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer not found with id: {fu_in.customer_id}"
            )

        user_id = current_user.id if current_user else None
        type_val = fu_in.follow_up_type.value if hasattr(fu_in.follow_up_type, "value") else str(fu_in.follow_up_type)

        follow_up = FollowUp(
            customer_id=fu_in.customer_id,
            user_id=user_id,
            title=fu_in.title.strip(),
            description=fu_in.description.strip() if fu_in.description else None,
            follow_up_type=type_val.upper(),
            scheduled_at=fu_in.scheduled_at,
            completed=fu_in.completed
        )
        db.add(follow_up)
        db.commit()
        db.refresh(follow_up)
        return follow_up

    @staticmethod
    def update_follow_up(
        db: Session,
        fu_id: int,
        fu_in: FollowUpUpdate,
        current_user: Optional[User] = None
    ) -> FollowUp:
        follow_up = FollowUpService.get_by_id(db, fu_id)

        if current_user and current_user.role == "SALES_REP":
            if follow_up.user_id and follow_up.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to edit a follow-up assigned to another representative"
                )

        if fu_in.customer_id is not None:
            customer = db.query(Customer).filter(Customer.id == fu_in.customer_id).first()
            if not customer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Customer not found with id: {fu_in.customer_id}"
                )
            follow_up.customer_id = fu_in.customer_id

        if fu_in.title is not None:
            follow_up.title = fu_in.title.strip()
        if fu_in.description is not None:
            follow_up.description = fu_in.description.strip() if fu_in.description else None
        if fu_in.follow_up_type is not None:
            type_val = fu_in.follow_up_type.value if hasattr(fu_in.follow_up_type, "value") else str(fu_in.follow_up_type)
            follow_up.follow_up_type = type_val.upper()
        if fu_in.scheduled_at is not None:
            follow_up.scheduled_at = fu_in.scheduled_at
        if fu_in.completed is not None:
            follow_up.completed = fu_in.completed

        db.commit()
        db.refresh(follow_up)
        return follow_up

    @staticmethod
    def delete_follow_up(db: Session, fu_id: int, current_user: Optional[User] = None) -> bool:
        follow_up = FollowUpService.get_by_id(db, fu_id)

        if current_user and current_user.role == "SALES_REP":
            if follow_up.user_id and follow_up.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to delete a follow-up assigned to another representative"
                )

        db.delete(follow_up)
        db.commit()
        return True
