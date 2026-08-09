from sqlalchemy import String;
from sqlalchemy.orm import Mapped,mapped_column;


from src.app.db.base import Base;


class Customer(Base):
    __tablename__="customers"


    id:Mapped[str]=mapped_column(
        String(20),
        primary_key=True,
    )

    name:Mapped[str]=mapped_column(
        String(100),
        nullable=False,
    )
    email: Mapped[str]=mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )