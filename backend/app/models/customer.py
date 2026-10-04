from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), index=True, nullable=False)
    email = Column(String(255), index=True, nullable=False)
    phone = Column(String(50), nullable=True)
    company = Column(String(150), index=True, nullable=True)
    industry = Column(String(100), nullable=True)
    status = Column(String(50), default="LEAD", nullable=False, index=True)
    source = Column(String(100), nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    assigned_user = relationship("User", back_populates="assigned_customers", foreign_keys=[assigned_to])
    activities = relationship("Activity", back_populates="customer", cascade="all, delete-orphan", passive_deletes=True)
    opportunities = relationship("Opportunity", back_populates="customer", cascade="all, delete-orphan", passive_deletes=True)
    follow_ups = relationship("FollowUp", back_populates="customer", cascade="all, delete-orphan", passive_deletes=True)
