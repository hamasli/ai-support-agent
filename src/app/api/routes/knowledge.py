from fastapi import APIRouter

from src.app.retrieval.rag_service import answer_with_rag
from src.app.schemas.knowledge import (
    KnowledgeAnswer,
    KnowledgeQuestion,
)


router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge"],
)


@router.post(
    "/ask",
    response_model=KnowledgeAnswer,
)
def ask_knowledge(
    request: KnowledgeQuestion,
) -> KnowledgeAnswer:

    result = answer_with_rag(
        request.question
    )

    return KnowledgeAnswer(**result)