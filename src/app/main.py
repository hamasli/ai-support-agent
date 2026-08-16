from fastapi import FastAPI
from pydantic import BaseModel
from src.app.api.routes.health import router as health_router;
from src.app.api.routes.chat import router as chat_router;
from src.app.api.routes.feedback import router as feedback_router;
from src.app.api.routes.knowledge import router as knowledge_router;
# Import the refund router directly from refunds.py.
# Import the refund router directly from refunds.py.
from src.app.api.routes.refunds import router as refund_router;
from src.app.api.routes.conversations import (
    router as conversations_router,
)

from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(
    title="AI Support Agent API",
    version="0.1.0",
)

app.include_router(health_router);
app.include_router(chat_router);
app.include_router(feedback_router)
app.include_router(knowledge_router);
# Human review endpoint for refund HITL workflows.
app.include_router(
    refund_router
)
app.include_router(
    conversations_router
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)