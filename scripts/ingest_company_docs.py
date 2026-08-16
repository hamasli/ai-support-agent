# from src.app.retrieval.ingestion_service import ingest_webpage


# URLS = [
#     # Return policy
#     "https://www.ikea.com/gb/en/customer-service/returns-claims/return-policy/",

#     # Damaged item after delivery
#     "https://www.ikea.com/gb/en/customer-service/knowledge/articles/06gd5116-29d3-41c9-ge22-c23425737816.html",

#     # Track / manage / cancel orders
#     "https://www.ikea.com/gb/en/customer-service/track-manage-order/",

#     # Delivery information
#     "https://www.ikea.com/gb/en/customer-service/services/delivery/",
# ]


# for url in URLS:

#     print(f"\nIngesting: {url}")

#     try:
#         count = ingest_webpage(url)

#         print(
#             f"Stored {count} chunks."
#         )

#     except Exception as error:
#         print(
#             f"Failed: {error}"
#         )



from src.app.retrieval.ingestion_service import (
    ingest_text_document,
)


DOCUMENTS = [
    {
        "title": "Company Return Policy",
        "source_url": "internal://return-policy",
        "text": """
                Customers may request a return within 30 days of delivery.

                Returned products should be unused and in their original condition
                unless the product arrived damaged or defective.

                Customers should provide their order ID when requesting a return.

                Refund requests are reviewed before final approval.

                Once a refund is approved, the customer will receive confirmation
                from customer support.

                Items damaged during delivery should be reported to customer support
                as soon as possible.
        """,
    },

    {
        "title": "Company Delivery Policy",
        "source_url": "internal://delivery-policy",
        "text": """
            Customers can check their current delivery status using their order ID.

            Estimated delivery dates may be available for orders that are still
            being processed or shipped.

            Delivered orders no longer require an estimated delivery date.

            If a delivery is significantly delayed, the customer may contact
            support for assistance.
            """,
    },

    {
        "title": "Damaged Item Policy",
        "source_url": "internal://damaged-item-policy",
        "text": """
            If an item arrives damaged or defective, the customer should contact
            customer support and provide the order ID and a description of the damage.

            Support may create a support ticket for further investigation.

            A refund may also be requested when appropriate, but refund requests
            require review before they are approved or rejected.
            """,
    },

    {
        "title": "Order Support Policy",
        "source_url": "internal://order-support-policy",
        "text": """
            Customers should provide their order ID when asking about an order.

            Support can provide the current order status and estimated delivery date
            when that information is available.

            If required information is missing, the support agent should ask the
            customer for that information rather than inventing it.
            """,
    },
]


for document in DOCUMENTS:

    print(
        f"\nIngesting: {document['title']}"
    )

    try:
        count = ingest_text_document(
            title=document["title"],
            text=document["text"],
            source_url=document["source_url"],
        )

        print(
            f"Stored {count} chunks."
        )

    except Exception as error:
        print(
            f"Failed: {error}"
        )