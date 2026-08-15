from datetime import date

from src.app.db.models.customer import Customer
from src.app.db.models.order import Order
from src.app.db.session import SessionLocal


# ---------------------------------------------------------
# FINAL TEST CUSTOMERS
# ---------------------------------------------------------

TEST_CUSTOMERS = [
    {
        "id": "CUST-901",
        "name": "Alice Test",
        "email": "alice.finaltest@example.com",
    },
    {
        "id": "CUST-902",
        "name": "Bob Test",
        "email": "bob.finaltest@example.com",
    },
    {
        "id": "CUST-903",
        "name": "Charlie Test",
        "email": "charlie.finaltest@example.com",
    },
]


# ---------------------------------------------------------
# FINAL TEST ORDERS
# ---------------------------------------------------------

TEST_ORDERS = [
    # Normal order-status test
    {
        "id": "ORD-9001",
        "customer_id": "CUST-901",
        "product_name": "Wireless Headphones",
        "status": "shipped",
        "estimated_delivery": date(2026, 8, 18),
    },

    # Refund APPROVAL workflow
    {
        "id": "ORD-9002",
        "customer_id": "CUST-901",
        "product_name": "Mechanical Keyboard",
        "status": "delivered",
        "estimated_delivery": None,
    },

    # Refund REJECTION workflow
    {
        "id": "ORD-9003",
        "customer_id": "CUST-901",
        "product_name": "USB-C Dock",
        "status": "delivered",
        "estimated_delivery": None,
    },

    # Ticket / escalation tests
    {
        "id": "ORD-9004",
        "customer_id": "CUST-902",
        "product_name": "27 Inch Monitor",
        "status": "delivered",
        "estimated_delivery": None,
    },

    # Duplicate-refund test
    {
        "id": "ORD-9005",
        "customer_id": "CUST-902",
        "product_name": "Laptop Stand",
        "status": "delivered",
        "estimated_delivery": None,
    },

    # Ownership / wrong-customer test
    {
        "id": "ORD-9006",
        "customer_id": "CUST-903",
        "product_name": "Webcam",
        "status": "processing",
        "estimated_delivery": date(2026, 8, 20),
    },
]


def seed_final_test_data() -> None:
    """
    Create deterministic customers and orders
    for our final end-to-end test suite.

    Safe to run multiple times:
    existing rows are updated instead of duplicated.
    """

    with SessionLocal() as db:

        print("\n================================")
        print("FINAL TEST DATA SEED")
        print("================================")

        # -------------------------------------------------
        # CUSTOMERS
        # -------------------------------------------------

        for data in TEST_CUSTOMERS:

            customer = db.get(
                Customer,
                data["id"],
            )

            if customer is None:

                customer = Customer(
                    **data
                )

                db.add(customer)

                print(
                    f"[CREATED CUSTOMER] "
                    f"{data['id']}"
                )

            else:

                # Keep the test dataset deterministic
                # if this script is run again.
                customer.name = data["name"]
                customer.email = data["email"]

                print(
                    f"[UPDATED CUSTOMER] "
                    f"{data['id']}"
                )

        # Customers must exist before orders
        # because orders contain foreign keys.
        db.flush()

        # -------------------------------------------------
        # ORDERS
        # -------------------------------------------------

        for data in TEST_ORDERS:

            order = db.get(
                Order,
                data["id"],
            )

            if order is None:

                order = Order(
                    **data
                )

                db.add(order)

                print(
                    f"[CREATED ORDER] "
                    f"{data['id']}"
                )

            else:

                # Reset the order to the expected
                # deterministic test values.
                order.customer_id = (
                    data["customer_id"]
                )
                order.product_name = (
                    data["product_name"]
                )
                order.status = (
                    data["status"]
                )
                order.estimated_delivery = (
                    data["estimated_delivery"]
                )

                print(
                    f"[UPDATED ORDER] "
                    f"{data['id']}"
                )

        db.commit()

        print("\n================================")
        print("SEED COMPLETE")
        print("================================")

        print("\nCustomers:")
        for customer in TEST_CUSTOMERS:
            print(
                f"  {customer['id']} "
                f"- {customer['name']}"
            )

        print("\nOrders:")
        for order in TEST_ORDERS:
            print(
                f"  {order['id']} "
                f"→ {order['customer_id']} "
                f"({order['status']})"
            )


if __name__ == "__main__":
    seed_final_test_data()