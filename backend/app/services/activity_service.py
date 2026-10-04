from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status
from app.models.activity import Activity
from app.models.customer import Customer
from app.models.user import User
from app.schemas.activity import ActivityCreate


class ActivityService:
    @staticmethod
    def get_by_id(db: Session, activity_id: int) -> Activity:
        activity = db.query(Activity).filter(Activity.id == activity_id).first()
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Activity not found with id: {activity_id}"
            )
        return activity

    @staticmethod
    def get_customer_activities(db: Session, customer_id: int) -> List[Activity]:
        # Verify customer exists
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer not found with id: {customer_id}"
            )
        return db.query(Activity).filter(
            Activity.customer_id == customer_id
        ).order_by(desc(Activity.created_at)).all()

    @staticmethod
    def create_activity(
        db: Session,
        customer_id: int,
        activity_in: ActivityCreate,
        current_user: Optional[User] = None
    ) -> Activity:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer not found with id: {customer_id}"
            )

        type_val = activity_in.activity_type.value if hasattr(activity_in.activity_type, "value") else str(activity_in.activity_type)

        activity = Activity(
            customer_id=customer_id,
            user_id=current_user.id if current_user else None,
            activity_type=type_val.upper(),
            title=activity_in.title.strip(),
            description=activity_in.description.strip() if activity_in.description else None
        )
        db.add(activity)
        db.commit()
        db.refresh(activity)
        return activity

    @staticmethod
    def delete_activity(db: Session, activity_id: int, current_user: Optional[User] = None) -> bool:
        activity = ActivityService.get_by_id(db, activity_id)

        if current_user and current_user.role == "SALES_REP":
            if activity.user_id and activity.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to delete another representative's activity"
                )

        db.delete(activity)
        db.commit()
        return True
