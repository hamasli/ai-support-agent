from pydantic import BaseModel, Field;

class OrderStatusArgs(BaseModel):
    order_id: str=Field(
        pattern=r"^ORD-\d{4}$"
    )


class CreateTicketArgs(BaseModel):
    customer_id: str=Field(
        pattern=r"^CUST-\d{3}$"
    )

    order_id: str = Field(
        pattern=r"^ORD-\d{4}$"
    )

    issue:str=Field(
        min_length=5,
        max_length=500
    )


class EscalateArgs(BaseModel):
    customer_id: str = Field(
        pattern=r"^CUST-\d{3}$"
    )

    reason: str = Field(
        min_length=5,
        max_length=500
    )



class RefundRequestArgs(BaseModel):
    customer_id: str = Field(
        pattern=r"^CUST-\d{3}$"
    )

    order_id: str = Field(
        pattern=r"^ORD-\d{4}$"
    )

    reason: str = Field(
        min_length=5,
        max_length=500
    )

