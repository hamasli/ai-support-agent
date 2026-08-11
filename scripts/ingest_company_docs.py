from src.app.retrieval.ingestion_service import ingest_webpage


URLS = [
    # Return policy
    "https://www.ikea.com/gb/en/customer-service/returns-claims/return-policy/",

    # Damaged item after delivery
    "https://www.ikea.com/gb/en/customer-service/knowledge/articles/06gd5116-29d3-41c9-ge22-c23425737816.html",

    # Track / manage / cancel orders
    "https://www.ikea.com/gb/en/customer-service/track-manage-order/",

    # Delivery information
    "https://www.ikea.com/gb/en/customer-service/services/delivery/",
]


for url in URLS:

    print(f"\nIngesting: {url}")

    try:
        count = ingest_webpage(url)

        print(
            f"Stored {count} chunks."
        )

    except Exception as error:
        print(
            f"Failed: {error}"
        )