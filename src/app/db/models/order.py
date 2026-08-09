from datetime import date;

from sqlalchemy import Date, ForeignKey,String;
from sqlalchemy.orm import Mapped,mapped_column;

from src.app.db.base import Base;


class Order(Base):
    __tablename__="orders"

    id:Mapped[str]=mapped_column(
        String(20),
        primary_key=True,
    )

    customer_id:Mapped[str]=mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
    )

    product_name:Mapped[str]=mapped_column(
        String(200),
        nullable=False,
    )

    status:Mapped[str]=mapped_column(
        String(50),
        nullable=False,

    )
    estimated_delivery:Mapped[date |None]=mapped_column(
        Date,
        nullable=True,
    )