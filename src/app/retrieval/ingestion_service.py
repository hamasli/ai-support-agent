from sqlalchemy import delete

from src.app.db.models.knowledge_chunk import KnowledgeChunk
from src.app.db.session import SessionLocal
from src.app.retrieval.embedding_service import create_embedding
from src.app.retrieval.web_loader import (
    load_webpage,
    split_into_chunks,
)


def ingest_webpage(url: str) -> int:

    # IMPORTANT: pass url here, not KnowledgeChunk
    title, text = load_webpage(url)

    chunks = split_into_chunks(text)

    with SessionLocal() as db:

        # Remove old chunks for the same webpage
        db.execute(
            delete(KnowledgeChunk).where(
                KnowledgeChunk.source_url == url
            )
        )

        for index, chunk in enumerate(chunks):

            embedding = create_embedding(chunk)

            knowledge_chunk = KnowledgeChunk(
                source_url=url,
                title=title,
                chunk_index=index,
                content=chunk,
                embedding=embedding,
            )

            db.add(knowledge_chunk)

        db.commit()

    return len(chunks)