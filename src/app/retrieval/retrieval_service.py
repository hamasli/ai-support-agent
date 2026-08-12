from sqlalchemy import select
from src.app.db.models.knowledge_chunk import KnowledgeChunk
from src.app.db.session import SessionLocal
from src.app.retrieval.embedding_service import create_embedding;
from sqlalchemy import func, select


def search_knowledge(
    question: str,
    limit: int = 5,
    min_similarity: float | None = 0.50,
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

        if (
            min_similarity is None
            or similarity >= min_similarity
        ):
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


def search_knowledge_keyword(
    question: str,
    limit: int = 5,
) -> list[dict]:

    document = func.to_tsvector(
        "english",
        KnowledgeChunk.title
        + " "
        + KnowledgeChunk.content,
    )

    query = func.websearch_to_tsquery(
        "english",
        question,
    )

    rank = func.ts_rank_cd(
        document,
        query,
    )

    statement = (
        select(
            KnowledgeChunk,
            rank.label("rank"),
        )
        .where(
            document.bool_op("@@")(query)
        )
        .order_by(rank.desc())
        .limit(limit)
    )

    with SessionLocal() as db:
        results = db.execute(statement).all()

    return [
        {
            "id": chunk.id,
            "title": chunk.title,
            "source_url": chunk.source_url,
            "content": chunk.content,
            "keyword_score": float(rank_value),
        }
        for chunk, rank_value in results
    ]



def search_knowledge_hybrid(
    question: str,
    limit: int = 5,
    candidate_limit: int = 10,
) -> list[dict]:

    vector_results = search_knowledge(
    question=question,
    limit=candidate_limit,
    min_similarity=None,
    )

    keyword_results = search_knowledge_keyword(
        question=question,
        limit=candidate_limit,
    )

    combined = {}

    # Reciprocal Rank Fusion constant
    k = 60

    # Add vector-search ranking
    for rank, result in enumerate(
        vector_results,
        start=1,
    ):
        chunk_id = result["id"]

        combined[chunk_id] = {
            "id": result["id"],
            "title": result["title"],
            "source_url": result["source_url"],
            "content": result["content"],
            "similarity": result["similarity"],
            "keyword_score": 0.0,
            "hybrid_score": 0.0,
        }

        combined[chunk_id]["hybrid_score"] += (
            1 / (k + rank)
        )

    # Add keyword-search ranking
    for rank, result in enumerate(
        keyword_results,
        start=1,
    ):
        chunk_id = result["id"]

        if chunk_id not in combined:
            combined[chunk_id] = {
                "id": result["id"],
                "title": result["title"],
                "source_url": result["source_url"],
                "content": result["content"],
                "similarity": 0.0,
                "keyword_score": result["keyword_score"],
                "hybrid_score": 0.0,
            }
        else:
            combined[chunk_id]["keyword_score"] = (
                result["keyword_score"]
            )

        combined[chunk_id]["hybrid_score"] += (
            1 / (k + rank)
        )

    ranked_results = sorted(
        combined.values(),
        key=lambda item: item["hybrid_score"],
        reverse=True,
    )

    return ranked_results[:limit]