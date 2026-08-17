# AI Research Agent

An Agentic AI Research application that combines **LangGraph, MCP, FastAPI, Streamlit, web search, and a Chroma-based internal knowledge base** to research questions, generate a structured report, and include a human-in-the-loop review and approval workflow.

## Project Overview

The application accepts a research question from the user and runs it through an agentic workflow:

```text
User
  ↓
Streamlit UI
  ↓
FastAPI
  ↓
LangGraph Workflow
  ↓
Research Agent
  ├── Live Web Search (Tavily)
  └── Internal Knowledge Base (Chroma)
  ↓
Writer Agent
  ↓
Reviewer Agent
  ↓
Human Approval
  ├── Approve → Final Report
  └── Reject + Feedback → Revision Workflow
```

## Key Features

- Agentic research workflow built with **LangGraph**
- **Human-in-the-loop** approval and revision workflow
- Live web research using **Tavily**
- Internal document retrieval using **Chroma**
- **MCP** server/client integration for research tools
- Research, writing, and reviewing handled as separate workflow stages
- FastAPI backend with REST endpoints
- Streamlit web interface
- Dockerized API and UI
- AWS deployment support using **Amazon ECR, ECS Fargate, and Application Load Balancer**
- API secrets supplied through environment variables / AWS Secrets Manager rather than committed to source control

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| Agent orchestration | LangGraph |
| LLM framework | LangChain |
| Tool protocol | MCP |
| Web search | Tavily |
| Vector database | Chroma |
| Backend API | FastAPI |
| Frontend | Streamlit |
| Containerization | Docker |
| Container registry | Amazon ECR |
| Cloud runtime | Amazon ECS Fargate |
| Load balancing | Application Load Balancer |

## Project Structure

```text
Agentic AI Research/
│
├── app/
│   ├── agents/
│   │   ├── human_approval.py
│   │   ├── research_agent.py
│   │   ├── reviewer_agent.py
│   │   ├── supervisor.py
│   │   └── writer_agent.py
│   │
│   ├── api/
│   │   └── main.py
│   │
│   ├── graph/
│   │   ├── builder.py
│   │   ├── routing.py
│   │   └── state.py
│   │
│   ├── mcp/
│   │   ├── client.py
│   │   └── server.py
│   │
│   ├── retrieval/
│   │   ├── chunker.py
│   │   ├── embeddings.py
│   │   ├── loader.py
│   │   ├── pipeline.py
│   │   ├── retriever.py
│   │   └── vector_store.py
│   │
│   ├── tools/
│   │   ├── retrieval_tool.py
│   │   └── web_search.py
│   │
│   └── ui/
│       └── streamlit_app.py
│
├── Dockerfile.api
├── Dockerfile.ui
├── .dockerignore
├── docker-compose.yml
├── requirements.txt
├── .gitignore
└── README.md
```

## How the Workflow Works

### 1. Submit a research question

The user enters a question through the Streamlit interface.

### 2. Research Agent

The Research Agent identifies the user's question and gathers information from two sources:

- Live web search through Tavily
- Internal research documents through the Chroma knowledge base

The two searches are performed concurrently to reduce waiting time.

### 3. Writer Agent

The workflow passes the research information to the Writer Agent, which produces the research report.

### 4. Reviewer Agent

The report is reviewed before the user makes the final decision.

### 5. Human Approval

The user can either:

- **Approve** the report and finish the workflow
- **Reject** the report and provide revision instructions

The LangGraph workflow resumes using the same thread and continues through the revision workflow.

## Local Setup

### Prerequisites

- Python 3.11+
- Git
- Docker Desktop (optional for containerized local execution)
- API keys for the services used by the application

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd "Agentic AI Research"
```

### 2. Create and activate an environment

For example with Conda:

```bash
conda create -n ragadvanced python=3.11
conda activate ragadvanced
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file and provide the required API keys used by the application, for example:

```env
GROQ_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

**Never commit `.env` or API keys to GitHub.**

### 5. Run the FastAPI backend

```bash
uvicorn app.api.main:api --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

### 6. Run the Streamlit UI

Open another terminal in the project directory and run:

```bash
streamlit run app/ui/streamlit_app.py
```

The UI will normally be available at:

```text
http://localhost:8501
```

The UI uses the `API_URL` environment variable when provided and falls back to the local FastAPI address for local development.

## Docker

The project contains separate Dockerfiles for the API and Streamlit UI.

Build the API image:

```bash
docker build -f Dockerfile.api -t agenticairesearch-api .
```

Build the UI image:

```bash
docker build -f Dockerfile.ui -t agenticairesearch-ui .
```

The repository also includes `docker-compose.yml` for running the services together.

```bash
docker compose up --build
```

To stop the containers:

```bash
docker compose down
```

## API Endpoints

### Start research

```text
POST /research
```

Request example:

```json
{
  "question": "What are the latest applications of RAG in enterprise AI?"
}
```

The response contains a `thread_id` that identifies the LangGraph workflow.

### Human decision

```text
POST /research/{thread_id}/decision
```

Approve example:

```json
{
  "decision": "approve",
  "revision_reason": ""
}
```

Reject example:

```json
{
  "decision": "reject",
  "revision_reason": "Add more practical examples and technical details."
}
```

## AWS Deployment

The application was containerized with Docker and prepared for deployment using AWS services including:

```text
Docker
  ↓
Amazon ECR
  ↓
Amazon ECS Fargate
  ↓
Application Load Balancer
  ↓
FastAPI / Streamlit
```

The AWS deployment configuration used separate ECS services for the API and UI.

AWS task-definition and deployment JSON files containing deployment-specific configuration are intentionally excluded from this repository.

## Security

The repository intentionally excludes sensitive and environment-specific files such as:

- `.env`
- API keys
- AWS credentials
- ECS task-definition JSON files used during deployment
- ECS IAM policy/trust-policy JSON files
- Local Chroma database files
- Python cache files

Secrets should be supplied through environment variables locally and an appropriate secrets-management mechanism when deployed.

## Future Improvements

- Add explicit timeouts and better failure handling around MCP/tool calls
- Improve persistent LangGraph checkpoint storage
- Improve long-running research request handling with asynchronous/background jobs
- Improve production observability and evaluation
- Add HTTPS and a custom domain for the public deployment
- Improve persistent vector-store deployment for cloud environments

## Author

**Harish**

Artificial Intelligence & Data Science Graduate

This project demonstrates practical experience with Agentic AI, LangGraph, MCP, RAG, FastAPI, Docker, and AWS deployment.
