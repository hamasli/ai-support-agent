def get_order_status(order_id:str)->dict:
    orders={
        "ORD-1001": {
            "status": "shipped",
            "estimated_delivery": "2026-08-10",
        },
        "ORD-1002": {
            "status": "processing",
            "estimated_delivery": "2026-08-12",
        },
    }
    order=orders.get(order_id)
    if order is None:
        return {
            "order_id":order_id,
            "found":False,
        }
    return {
        "order_id": order_id,
        "found":True,
        **order,
    }