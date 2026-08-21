

#now instead of manually passing the data, we are taking the data from database. 
from src.app.db.models.order import Order
from src.app.db.session import SessionLocal


def get_order_status(order_id: str) -> dict:

    with SessionLocal() as db:
        order = db.get(Order, order_id)

        if order is None:
            return {
                "order_id": order_id,
                "found": False,
            }

        return {
            "order_id": order.id,
            "customer_id": order.customer_id,
            "product_name": order.product_name,
            "status": order.status,
            "estimated_delivery": (
                order.estimated_delivery.isoformat()
                if order.estimated_delivery
                else None
            ),
            "found": True,
        }