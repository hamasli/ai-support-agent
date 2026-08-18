# AI Support Agent

AI Support Agent is a full-stack customer-support application built to demonstrate how an LLM-based agent can work with application data, internal knowledge, persistent conversation state, and human approval workflows.

The backend is implemented with FastAPI and LangGraph. The agent uses the OpenAI Responses API for reasoning and tool selection, PostgreSQL for application data and conversation history, and pgvector for retrieval over internal support documentation. The frontend is built with React and TypeScript and provides conversation history, structured tool results, and a reviewer interface for refund requests that require human approval.

The project focuses on four practical AI-engineering concerns: reliable tool use, retrieval-augmented generation, persistent agent state, and human-in-the-loop execution.

## Demo

The demo is intentionally placed at the beginning of the repository so the main workflows can be understood before reading the implementation details.

![AI Support Agent demo preview](docs/demo/demo-preview.gif)

[Watch the full 2-minute demo](ProjectDemo/Demo/ai-support-agent-demo.mp4)

The demo covers:

- reopening persisted conversations;
- retrieving company policy information through RAG;
- querying order information through an application tool;
- creating a support ticket;
- creating a refund request;
- pausing the refund workflow for human review;
- preserving the pending review state when switching conversations;
- approving or rejecting the refund from Reviewer Mode;
- resuming the LangGraph workflow and displaying the final result.

> The GIF is intended as a short automatically visible preview. The MP4 contains the full demonstration.

## System Architecture

![AI Support Agent system architecture](docs/architecture.png)

The application is divided into several clear layers.

### Frontend

The React and TypeScript frontend is responsible for the user-facing support experience. It communicates with FastAPI over HTTP and does not contain business logic for orders, refunds, tickets, or retrieval.

The frontend provides:

- a chat interface;
- a conversation sidebar;
- creation of new conversations;
- loading of previously saved conversations;
- restoration of the active conversation after browser refresh;
- Markdown rendering for assistant responses;
- structured cards for tool results;
- loading and error states;
- responsive mobile behavior;
- a reviewer interface for pending refund requests.

The API base URL is provided through the `VITE_API_BASE_URL` environment variable rather than being permanently hard-coded into the application.

### Backend API

FastAPI exposes the application API and acts as the boundary between the frontend and the agent workflow.

The main responsibilities of the backend are:

- receiving chat messages;
- creating or reusing conversation IDs;
- persisting user and assistant messages;
- invoking the LangGraph agent;
- exposing conversation history;
- exposing pending refund state to the frontend;
- receiving human refund decisions;
- resuming paused LangGraph executions.

The local API runs on:

```text
http://localhost:8001
```

Interactive API documentation is available at:

```text
http://localhost:8001/docs
```

### Agent Orchestration

LangGraph controls the agent workflow.

The agent uses the OpenAI Responses API for reasoning and tool selection. Tool calls are executed by the application and their results are returned to the agent before the final response is produced.

LangGraph is also used to manage the refund approval workflow because it supports interruption, checkpointing, and resume behavior.

The high-level agent loop is:

```text
User message
    |
    v
FastAPI
    |
    v
LangGraph agent
    |
    v
OpenAI Responses API
    |
    +---- no tool required ----> final response
    |
    +---- tool required -------> execute application tool
                                      |
                                      v
                                  tool result
                                      |
                                      v
                                LangGraph agent
                                      |
                                      v
                                final response
```

## Agent Tools

The agent currently has five application tools.

### Order Status

```text
get_order_status
```

Retrieves order information from PostgreSQL.

The tool validates the supplied customer and order identifiers before returning data. The agent is instructed not to invent order information if a valid record cannot be found.

Example request:

```text
What is the status of order ORD-9005 for customer CUST-902?
```

A successful result is rendered in the frontend as a structured Order Details card.

### Support Ticket

```text
create_support_ticket
```

Creates a support ticket associated with a valid customer and order.

A typical result contains:

- ticket ID;
- customer ID;
- order ID;
- status;
- issue description.

The frontend detects the structured result and renders it as a Support Ticket card rather than displaying an unformatted block of text.

### Refund Request

```text
request_refund
```

Creates a refund request with an initial status of:

```text
pending_approval
```

Refunds are intentionally not approved automatically.

A pending refund enters the human-in-the-loop workflow described later in this README.

Duplicate refund behavior is handled by the backend so that an existing pending or approved request is not silently recreated for the same order. A rejected request can be followed by a new request when appropriate.

### Human Escalation

```text
escalate_to_human
```

Creates an escalation when a case requires human support.

Escalation records are stored in PostgreSQL and can be referenced in the assistant response.

### Knowledge Search

```text
search_knowledge_base
```

Retrieves relevant internal company documentation through the RAG pipeline.

This tool is used for questions about policies, instructions, and support documentation. The agent is instructed to use retrieved information rather than inventing company policy.

## Retrieval-Augmented Generation

The project includes a retrieval pipeline backed by PostgreSQL and pgvector.

The knowledge base currently contains internal support documents such as:

- Company Return Policy;
- Company Delivery Policy;
- Damaged Item Policy;
- Order Support Policy.

Documents are split into chunks, embedded, and stored in the `knowledge_chunks` table together with their source metadata.

The retrieval path is designed to use a fast hybrid search first. When a stronger fallback is required, the system can rewrite the query and rerank candidate chunks.

A simplified flow is:

```text
User policy question
        |
        v
search_knowledge_base
        |
        v
Hybrid retrieval
        |
        +---- sufficient result ----> relevant company knowledge
        |
        +---- fallback required ----> query rewrite
                                          |
                                          v
                                       reranking
                                          |
                                          v
                               relevant company knowledge
        |
        v
Agent response
```

pgvector is used for embedding-based similarity search, while PostgreSQL also remains the source of truth for the rest of the application data.

Internal implementation metadata such as `internal://...` source URLs is not intended to be exposed in the customer-facing response.

## Human-in-the-Loop Refund Workflow

The refund workflow is the main safety-sensitive path in the project.

The agent can create a refund request, but it cannot make the final approval decision by itself.

The workflow is:

```text
Customer requests refund
        |
        v
request_refund
        |
        v
Refund created
status = pending_approval
        |
        v
LangGraph interrupt()
        |
        v
Workflow paused
        |
        v
Human reviewer
   /           \
Approve       Reject
   \           /
        v
LangGraph resume
        |
        v
Refund status updated
        |
        v
Final assistant response
```

When the refund is created, the `/chat` response includes structured state:

```json
{
  "status": "pending_human_review",
  "requires_human_review": true,
  "data": {
    "refund_id": "REF-...",
    "refund_status": "pending_approval"
  }
}
```

The frontend uses this information to display the Reviewer Mode card.

### Reviewer Mode

Reviewer Mode is included in the same frontend for demonstration purposes so the complete HITL workflow can be shown from one interface.

The card exposes:

- refund ID;
- current review state;
- Approve action;
- Reject action.

The decision is sent to:

```text
POST /refunds/{refund_id}/review
```

The backend then resumes the interrupted LangGraph execution and updates the stored refund status.

In a production deployment, reviewer permissions would normally be separated from the customer interface through authentication and role-based authorization. This project keeps the reviewer control visible in the demo UI so the HITL behavior can be inspected directly.

### Review Persistence

Pending refund state is stored in the database rather than inferred from old chat text.

When an existing conversation is opened, the conversation endpoint returns the current pending refund, if one exists.

This allows the reviewer card to survive:

- switching to another conversation;
- returning to the original conversation;
- page refresh;
- reopening a previously saved conversation.

Once a refund has been approved or rejected, it no longer appears as a pending review.

## Conversation Persistence

Conversations are stored in PostgreSQL.

Each conversation receives a generated conversation ID. User and assistant messages are stored separately and ordered by creation time.

The frontend uses:

```text
GET /conversations
```

to populate the sidebar and:

```text
GET /conversations/{conversation_id}/messages
```

to restore a conversation.

The conversation history endpoint also returns pending refund information when a review is still active.

The selected conversation ID is stored in browser `localStorage`, allowing the same conversation to reopen after a refresh.

## Structured Responses in the Frontend

Tool results are displayed as structured cards where possible.

The frontend recognizes identifiers such as:

```text
ORD-...
CUST-...
TKT-...
REF-...
ESC-...
```

and status labels in assistant responses.

The current structured result types include:

- Order Details;
- Support Ticket Created;
- Refund Request;
- Refund Approved;
- Refund Rejected;
- Support Escalation.

This keeps operational data visually separate from normal conversational text while still preserving the original assistant response.

Markdown is rendered with `react-markdown` and `remark-gfm`.

## Technology Stack

### Backend

- Python 3.13+
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL
- pgvector
- psycopg

### AI and Orchestration

- OpenAI Responses API
- LangGraph
- LangGraph PostgreSQL checkpointing
- LangSmith

### Retrieval

- pgvector
- OpenAI embeddings
- hybrid retrieval
- query rewriting fallback
- reranking

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- Lucide React
- react-markdown
- remark-gfm

### Testing and Development

- pytest
- Docker
- Docker Compose
- GitHub Actions

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Basic service health check |
| `POST` | `/chat` | Send a message to the support agent |
| `GET` | `/conversations` | List saved conversations |
| `GET` | `/conversations/{conversation_id}/messages` | Load conversation history and current pending refund state |
| `POST` | `/refunds/{refund_id}/review` | Approve or reject a pending refund |

### Chat Request

```json
{
  "message": "What is the status of order ORD-9005 for customer CUST-902?",
  "conversation_id": null
}
```

### Completed Chat Response

```json
{
  "conversation_id": "CONV-...",
  "reply": "...",
  "status": "completed",
  "requires_human_review": false,
  "data": {}
}
```

### Pending Review Response

```json
{
  "conversation_id": "CONV-...",
  "reply": "Your refund request has been created and is waiting for human review.",
  "status": "pending_human_review",
  "requires_human_review": true,
  "data": {
    "refund_id": "REF-...",
    "refund_status": "pending_approval"
  }
}
```

## Database

PostgreSQL is used for both application persistence and vector retrieval.

The application schema includes data for:

```text
customers
orders
tickets
refund_requests
escalations
conversations
messages
tool_calls
feedback
knowledge_chunks
```

LangGraph checkpoint tables are also created in PostgreSQL for workflow persistence.

The Docker environment exposes PostgreSQL on a different host port from the local Windows PostgreSQL installation used during development:

```text
Inside Docker API -> db:5432
Windows host -> Docker PostgreSQL -> localhost:5433
```

## Project Structure

The following shows the main project layout rather than every generated file:

```text
AI-Support-Agent/
|
|-- src/
|   `-- app/
|       |-- agents/
|       |   |-- agent_graph.py
|       |   `-- state.py
|       |
|       |-- api/
|       |   `-- routes/
|       |
|       |-- db/
|       |   |-- models/
|       |   `-- session.py
|       |
|       |-- retrieval/
|       |   `-- ingestion_service.py
|       |
|       |-- schemas/
|       |-- services/
|       |-- tools/
|       |-- config.py
|       `-- main.py
|
|-- frontend/
|   |-- src/
|   |   |-- components/
|   |   |   |-- AssistantMessageContent.tsx
|   |   |   `-- ResultCard.tsx
|   |   |
|   |   |-- services/
|   |   |   `-- api.ts
|   |   |
|   |   |-- types/
|   |   |   `-- chat.ts
|   |   |
|   |   |-- utils/
|   |   |   `-- messageResult.ts
|   |   |
|   |   |-- App.tsx
|   |   `-- index.css
|   |
|   |-- package.json
|   |-- vite.config.ts
|   `-- .env.example
|
|-- scripts/
|-- tests/
|-- migrations/
|
|-- docs/
|   |-- architecture.png
|   `-- demo/
|       |-- demo-preview.gif
|       `-- ai-support-agent-demo.mp4
|
|-- .github/
|   `-- workflows/
|       `-- ci.yml
|
|-- Dockerfile
|-- compose.yaml
|-- pyproject.toml
|-- .env.example
|-- .gitignore
`-- README.md
```

## Running the Project Locally

### Prerequisites

Install:

- Python 3.13 or later;
- Docker Desktop;
- Node.js LTS;
- Git.

An OpenAI API key is required for agent and embedding calls.

LangSmith is optional unless tracing/evaluation is being used.

### 1. Clone the Repository

```bash
git clone <YOUR-REPOSITORY-URL>
cd AI-Support-Agent
```

### 2. Configure Backend Environment Variables

Create a `.env` file in the repository root using `.env.example` as the starting point.

Typical settings include:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-5-nano

LANGSMITH_TRACING=false
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=ai-support-agent
```

Do not commit real API keys.

The Docker Compose configuration provides the containerized API with the database URL required to connect to the `db` service.

### 3. Start the Backend and Database

From the repository root:

```powershell
docker compose up -d --build
```

Check service status:

```powershell
docker compose ps
```

The expected services are:

```text
api
db
```

The API is available at:

```text
http://localhost:8001
```

To stop the environment:

```powershell
docker compose down
```

If backend source code has not changed, restart without rebuilding:

```powershell
docker compose up -d
```

After backend code changes:

```powershell
docker compose up -d --build
```

### 4. Database Migrations and Demo Data

Apply the project's Alembic migrations to a fresh database before using the application.

The repository also includes scripts used during development to seed demo customers/orders and ingest internal company documentation.

The RAG knowledge ingestion should be run before testing company-policy questions on a new database.

### 5. Configure the Frontend

From the `frontend` directory:

```powershell
npm install
```

Create:

```text
frontend/.env
```

using:

```env
VITE_API_BASE_URL=http://localhost:8001
```

Start Vite:

```powershell
npm run dev
```

The frontend is then available at:

```text
http://localhost:5173
```

## Frontend Production Build

To verify that the frontend compiles successfully outside development mode:

```powershell
cd frontend
npm run build
```

Vite creates:

```text
frontend/dist/
```

The generated `dist` directory is not intended to be committed.

## Testing

The backend test suite uses pytest.

The project currently contains 17 backend tests covering areas including:

- health checks;
- order and ticket tools;
- escalation behavior;
- refund behavior;
- knowledge and tool-service logic;
- refund review logic;
- API routes.

Run the suite from the repository root:

```powershell
pytest
```

The expected result for the current suite is:

```text
17 passed
```

The tests are intended to validate deterministic application behavior. AI workflow traces and evaluations are handled separately through LangSmith.

## LangSmith Tracing and Evaluation

LangSmith is used to inspect and evaluate agent behavior.

Tracing provides visibility into:

- LangGraph execution paths;
- model calls;
- tool calls;
- retrieval behavior;
- workflow timing.

A LangSmith evaluation dataset was created for representative support scenarios, including:

- return-policy questions;
- damaged-item questions;
- valid order lookup;
- invalid order lookup;
- refund requests.

This is complementary to pytest: pytest checks application logic, while LangSmith is used to inspect and evaluate AI behavior.

## Continuous Integration

GitHub Actions runs the backend test workflow automatically on pushes and pull requests to `main`.

The CI workflow uses a fresh Linux runner and:

1. checks out the repository;
2. starts PostgreSQL with pgvector;
3. installs Python 3.13;
4. installs the project dependencies;
5. enables the vector extension;
6. runs Alembic migrations;
7. seeds the required test data;
8. runs pytest.

Using a Linux runner also catches issues that can be hidden on a case-insensitive Windows development environment.

The workflow configuration is located at:

```text
.github/workflows/ci.yml
```

## Docker

Docker Compose is used to provide a reproducible local backend environment.

The main services are:

```text
api - FastAPI application
db  - PostgreSQL with pgvector
```

The API container connects to PostgreSQL through:

```text
db:5432
```

The database is exposed to the Windows host through:

```text
localhost:5433
```

The API is exposed through:

```text
localhost:8001
```

## Security and Repository Hygiene

Secrets are intentionally kept outside source control.

The repository should not contain:

- `.env`;
- `frontend/.env`;
- OpenAI API keys;
- LangSmith API keys;
- private production database credentials;
- `node_modules`;
- generated frontend `dist` output.

Relevant entries should remain in `.gitignore`, for example:

```gitignore
.env
frontend/.env

venv/
__pycache__/
*.pyc
.pytest_cache/

frontend/node_modules/
frontend/dist/

.vscode/
.idea/
```

Before pushing changes, review:

```powershell
git status
```

and verify that no secret or generated dependency directory is staged.

## Design Decisions

A few implementation choices are intentional.

### The agent does not own business data

Orders, tickets, refunds, and conversations are stored in PostgreSQL. The language model can request tools, but it does not act as the source of truth for operational data.

### Policies are retrieved rather than invented

Company policy questions are handled through the knowledge-search tool and internal RAG pipeline.

### Refund approval is not delegated to the model

The model may initiate a refund request, but approval and rejection require a human decision.

### Conversation state is persistent

Messages are stored in PostgreSQL and LangGraph uses PostgreSQL checkpointing for workflow state.

### Reviewer Mode is intentionally visible in the demo frontend

For the portfolio demonstration, customer chat and refund review are shown in one interface. A deployed production system would normally protect reviewer functionality with authentication and authorization.

## Known Limitations

The project currently runs locally and has not been deployed to a public cloud environment.

Other current limitations include:

- no production authentication or role-based access control;
- reviewer controls are included in the demo frontend;
- no public customer account system;
- no production monitoring/alerting stack;
- no file-upload workflow for damaged-item evidence;
- frontend automated tests are not yet included;
- deployment configuration is intentionally deferred.

These limitations are kept explicit because the purpose of the repository is to demonstrate the agent architecture and application workflows rather than present the demo as a fully deployed commercial support platform.

## Future Work

Potential extensions include:

- deploying the frontend and API to a suitable cloud provider;
- using managed PostgreSQL with pgvector;
- introducing authentication and reviewer roles;
- separating the reviewer interface from the customer chat;
- streaming assistant responses;
- supporting file/image evidence for damaged items;
- adding rate limiting and production security controls;
- expanding the knowledge base;
- increasing automated RAG evaluation coverage;
- adding frontend unit and end-to-end tests;
- integrating additional customer-support systems.

Cloud deployment is intentionally deferred. The local Docker-based implementation is the current completed project scope and deployment can be revisited later when an appropriate free or paid hosting option is selected.

## What This Project Demonstrates

The repository brings together several parts of an AI application that are often demonstrated separately:

- LLM reasoning through the OpenAI Responses API;
- LangGraph orchestration;
- application tool calling;
- persistent conversation state;
- PostgreSQL-backed business data;
- pgvector-based retrieval;
- retrieval-augmented generation;
- human-in-the-loop workflow control;
- React and TypeScript API integration;
- structured frontend presentation;
- Docker-based local execution;
- automated backend testing;
- GitHub Actions CI;
- LangSmith tracing and evaluation.

The main goal was not to build another single-turn chatbot. The goal was to build a support-agent workflow in which the model can retrieve grounded information, call controlled application tools, preserve state, and stop for human approval when an action should not be automated.
