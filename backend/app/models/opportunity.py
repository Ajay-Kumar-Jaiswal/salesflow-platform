from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Float, default=0.0, nullable=False)
    stage = Column(String(50), default="LEAD", nullable=False, index=True)  # LEAD, CONTACTED, QUALIFIED, PROPOSAL, NEGOTIATION, WON, LOST
    probability = Column(Float, default=10.0, nullable=False)  # 0 to 100 percentage
    expected_close_date = Column(DateTime(timezone=True), nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    customer = relationship("Customer", back_populates="opportunities")
    assigned_user = relationship("User", back_populates="opportunities", foreign_keys=[assigned_to])
