# PROJECT_STATUS.md

# AI Support Agent — Project Status

**Current date:** 2026-08-09  
**Target:** Junior Applied AI Engineer portfolio project  
**Goal:** Complete a production-style AI support agent before starting job applications in early September 2026.

## 1. Completed

### Project foundation
- Git + GitHub repository
- `src/` project structure
- Virtual environment
- `pyproject.toml`
- `.env` / `.env.example`

### FastAPI backend
- `GET /health`
- `POST /chat`
- Routes separated into modules
- Swagger docs at `/docs`
- Pydantic request/response validation

### OpenAI integration
- OpenAI Python SDK
- Responses API
- Environment-based API configuration
- Real AI responses through `/chat`

### Manual AI agent
Implemented without LangGraph yet so the agent loop is understood directly.

Current tools:
- `get_order_status`
- `create_support_ticket`
- `request_refund`
- `escalate_to_human`

Implemented:
- Tool/function calling
- Multiple tool calls in one request
- Multi-step agent loop
- `max_steps`
- Maximum tool-call protection
- Pydantic validation for tool arguments
- Customer/order ID validation
- OpenAI timeout and retry handling
- Tool execution error handling

### PostgreSQL database
Installed and connected:
- PostgreSQL 18
- pgAdmin 4
- Psycopg 3
- SQLAlchemy 2
- Alembic

Database:
- `ai_support_agent`

Current tables:
- `customers`
- `orders`
- `tickets`
- `refund_requests`
- `escalations`
- `alembic_version`

### Real database-backed tools
- `get_order_status()` reads orders from PostgreSQL
- `create_support_ticket()` validates customer/order and saves a real ticket
- `request_refund()` validates customer/order and saves a pending refund request
- `escalate_to_human()` validates the customer and saves a real escalation

## 2. Current Project Flow

```text
User
  ↓
FastAPI /chat
  ↓
OpenAI Responses API
  ↓
AI decides whether a tool is needed
  ↓
Pydantic validates tool arguments
  ↓
Python tool executes
  ↓
PostgreSQL reads/writes real records
  ↓
Tool result returns to AI
  ↓
AI may call another tool
  ↓
Final response
```

## 3. Next Tasks

### Database completion
Add:
- `conversations`
- `messages`
- `tool_calls`
- `feedback`

Then store:
- conversation history
- user/assistant messages
- executed tool calls
- user feedback

### RAG
Tools/technologies:
- OpenAI embeddings
- PostgreSQL + pgvector
- BeautifulSoup or Trafilatura
- `langchain-text-splitters`

Implement:
- webpage ingestion
- chunking
- embeddings
- vector search
- keyword search
- hybrid retrieval
- reranking
- source citations
- refusal when evidence is insufficient

### LangGraph
Convert the manual agent loop to a controlled workflow.

Learn/use only:
- State
- Nodes
- Edges
- Conditional edges
- Tool nodes
- Checkpointing
- Human approval
- Step limits

### Production finishing
- Docker
- Docker Compose
- pytest
- LangSmith
- GitHub Actions
- Azure deployment

## 4. Project 1 Final Goal

Production-style AI customer-support agent with:

- FastAPI backend
- OpenAI agent
- PostgreSQL persistence
- RAG
- reliable tool calling
- refund approval workflow
- conversation history
- testing
- observability
- Docker
- CI/CD
- cloud deployment

## 5. Project 2 — After Project 1

Industrial Computer Vision Inspector.

Planned tools:
- PyTorch
- Ultralytics YOLO
- OpenCV
- Albumentations
- FiftyOne
- CVAT
- MLflow
- ONNX
- ONNX Runtime

Reuse from Project 1:
- FastAPI
- Pydantic
- PostgreSQL
- Docker
- pytest
- GitHub Actions
- Azure

## 6. Current Position

**Project 1 status:** Core backend + manual agent + core PostgreSQL persistence are working.

**Immediate next step:** Add conversation/message/tool-call/feedback persistence, then move to RAG.
