from src.app.retrieval.ingestion_service import ingest_webpage


URL = "https://www.python-httpx.org/quickstart/"


count = ingest_webpage(URL)

print(f"Stored {count} chunks.")