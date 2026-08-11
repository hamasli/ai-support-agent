from sqlalchemy import select
from src.app.db.models.knowledge_chunk import KnowledgeChunk
from src.app.db.session import SessionLocal
from src.app.retrieval.embedding_service import create_embedding


def search_knowledge(
    question: str,
    limit: int = 5,
    min_similarity: float = 0.50,
) -> list[dict]:

    question_embedding = create_embedding(question)

    distance = KnowledgeChunk.embedding.cosine_distance(
        question_embedding
    )

    statement = (
        select(
            KnowledgeChunk,
            distance.label("distance"),
        )
        .order_by(distance)
        .limit(limit)
    )

    with SessionLocal() as db:
        results = db.execute(statement).all()

    relevant_results = []

    for chunk, distance_value in results:

        similarity = 1 - float(distance_value)

        if similarity >= min_similarity:
            relevant_results.append(
                {
                    "id": chunk.id,
                    "title": chunk.title,
                    "source_url": chunk.source_url,
                    "content": chunk.content,
                    "similarity": similarity,
                }
            )

    return relevant_results