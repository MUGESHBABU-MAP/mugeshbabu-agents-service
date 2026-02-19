# BabuAI (Mugeshbabu Agents Service)

**BabuAI** is a high-performance Python microservice designed to orchestrate AI agents, manage teams, handle document processing (RAG), and support rich chat interactions. It replaces the legacy system with a modern, async-first architecture.

## 🚀 Features

*   **Agent Orchestration**: Execute AI agents with scalable queue-based architecture (SQS integration).
*   **Chat (RAG)**: Retrieval-Augmented Generation using Redis for caching, BM25 for retrieval, and AWS Bedrock (Claude) for generation.
*   **PDF Generation**: High-fidelity HTML-to-PDF conversion using Playwright, with support for Mermaid diagrams.
*   **Teams**: Manage agent groups with dynamic filtering capabilities.
*   **Architecture**: Built with **FastAPI** (Async), **MongoDB** (Motor), and **Redis**.

## 🛠️ Tech Stack

*   **Language**: Python 3.11+
*   **Framework**: FastAPI
*   **Database**: MongoDB (Motor), Redis
*   **Queue/Cloud**: AWS (SQS, S3, Bedrock)
*   **Browser Engine**: Playwright
*   **Package Manager**: `uv` (recommended) or `pip`

## 📦 Installation & Setup

### Prerequisites
*   Python 3.11+
*   [uv](https://github.com/astral-sh/uv) (Recommended for speed)
*   MongoDB & Redis (running locally or accessible)

### 1. Clone the Repository
```bash
git clone https://github.com/MUGESHBABU-MAP/mugeshbabu-agents-service.git
cd mugeshbabu-agents-service
```

### 2. Setup Environment
Copy the example environment file and configure your credentials:
```bash
cp .env.example .env
```
Edit `.env` to set your MongoDB URI, Redis URL, and AWS credentials.

### 3. Install Dependencies
Using `uv`:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r pyproject.toml
```
*Note: If you don't use `uv`, just use standard `pip install .`*

### 4. Install Playwright Browsers
Required for PDF generation. On macOS/Windows, just install the browser binary:
```bash
playwright install chromium
```
*Note: `playwright install-deps` is generally for Linux distributions and Docker environments.*

## 🏃‍♂️ Running the App

### Local Development
Start the hot-reloading server:
```bash
uv run uvicorn mugeshbabu_agents.main:app --reload --host 0.0.0.0 --port 8000
```
*   **Swagger UI**: `http://localhost:8000/docs`
*   **Health Check**: `http://localhost:8000/health`

### Docker (Production)
Build and run the container:
```bash
docker build -t babuai-service .
docker run -p 8000:8000 --env-file .env babuai-service
```

## 📂 Project Structure

```
src/mugeshbabu_agents/
├── api/v1/          # API Routes (Agents, Chat, Documents, Teams)
├── core/            # Configuration (Pydantic Settings)
├── domain/          # Business Logic (DDD)
│   ├── agents/      # Agent Models & Execution Logic
│   ├── chat/        # RAG Logic (Redis + BM25 + Bedrock)
│   ├── documents/   # PDF Generation (Playwright)
│   └── teams/       # Team Management & Dynamic Filters
├── infrastructure/  # Database Clients (Mongo, Redis)
└── main.py          # Application Entrypoint
```

## 🧪 Testing
Run tests using `pytest` (once implemented):
```bash
uv run pytest
```

## ⚠️ Troubleshooting

**Build Error (`ValueError: Unable to determine which files to ship...`)**
Ensure `pyproject.toml` includes:
```toml
[tool.hatch.build.targets.wheel]
packages = ["src/mugeshbabu_agents"]
```
(This has been fixed in the repo).

**Playwright Installation Fails**
If `playwright install-deps` fails on macOS, simply run `playwright install chromium`. The dependencies command is for Linux systems.
