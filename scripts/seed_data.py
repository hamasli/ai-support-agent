from datetime import date

from src.app.db.models.customer import Customer
from src.app.db.models.order import Order
from src.app.db.session import SessionLocal


def seed_data() -> None:
    with SessionLocal() as db:

        # --------------------
        # Customers
        # --------------------

        if db.get(Customer, "CUST-001") is None:
            db.add(
                Customer(
                    id="CUST-001",
                    name="Ali",
                    email="ali@example.com",
                )
            )

        if db.get(Customer, "CUST-002") is None:
            db.add(
                Customer(
                    id="CUST-002",
                    name="Sara",
                    email="sara@example.com",
                )
            )

        if db.get(Customer, "CUST-003") is None:
            db.add(
                Customer(
                    id="CUST-003",
                    name="John",
                    email="john@example.com",
                )
            )

        # --------------------
        # Orders
        # --------------------

        if db.get(Order, "ORD-1001") is None:
            db.add(
                Order(
                    id="ORD-1001",
                    customer_id="CUST-001",
                    product_name="Wireless Headphones",
                    status="shipped",
                    estimated_delivery=date(2026, 8, 10),
                )
            )

        if db.get(Order, "ORD-1002") is None:
            db.add(
                Order(
                    id="ORD-1002",
                    customer_id="CUST-001",
                    product_name="Mechanical Keyboard",
                    status="processing",
                    estimated_delivery=date(2026, 8, 12),
                )
            )

        if db.get(Order, "ORD-1003") is None:
            db.add(
                Order(
                    id="ORD-1003",
                    customer_id="CUST-002",
                    product_name="Gaming Mouse",
                    status="delivered",
                    estimated_delivery=date(2026, 8, 7),
                )
            )

        if db.get(Order, "ORD-1004") is None:
            db.add(
                Order(
                    id="ORD-1004",
                    customer_id="CUST-002",
                    product_name="USB-C Hub",
                    status="shipped",
                    estimated_delivery=date(2026, 8, 11),
                )
            )

        if db.get(Order, "ORD-1005") is None:
            db.add(
                Order(
                    id="ORD-1005",
                    customer_id="CUST-003",
                    product_name="Laptop Stand",
                    status="processing",
                    estimated_delivery=date(2026, 8, 14),
                )
            )

        if db.get(Order, "ORD-1006") is None:
            db.add(
                Order(
                    id="ORD-1006",
                    customer_id="CUST-003",
                    product_name="Webcam",
                    status="cancelled",
                    estimated_delivery=date(2026, 8, 15),
                )
            )

        db.commit()

    print("Sample data added successfully.")


if __name__ == "__main__":
    seed_data();