from pydantic import BaseModel


class KnowledgeQuestion(BaseModel):
    question: str


class KnowledgeAnswer(BaseModel):
    answer: str
    sources: list[str]