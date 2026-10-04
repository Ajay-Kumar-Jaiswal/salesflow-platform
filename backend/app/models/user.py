from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="SALES_REP", nullable=False)  # ADMIN, SALES_REP
    created_at = Column(DateTime(timezone=True), server_default=func.now(), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    assigned_customers = relationship("Customer", back_populates="assigned_user", foreign_keys="Customer.assigned_to")
    activities = relationship("Activity", back_populates="user")
    opportunities = relationship("Opportunity", back_populates="assigned_user", foreign_keys="Opportunity.assigned_to")
    follow_ups = relationship("FollowUp", back_populates="user")
