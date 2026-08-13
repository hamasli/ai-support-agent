from typing import Any
from typing_extensions import TypedDict


class AgentState(TypedDict):
    conversation_id: str
    messages: list[dict[str, Any]]