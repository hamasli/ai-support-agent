from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.app.db.base import Base


class Escalation(Base):
    __tablename__ = "escalations"

    id: Mapped[str] = mapped_column(
        String(20),
        primary_key=True,
    )

    customer_id: Mapped[str] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="escalated",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )