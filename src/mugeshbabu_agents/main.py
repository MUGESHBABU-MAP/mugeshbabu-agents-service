from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mugeshbabu_agents.core.config import settings
from mugeshbabu_agents.infrastructure.db import db_manager
from mugeshbabu_agents.api.v1 import agents, chat, documents

import logging

# Configure logging
logging.basicConfig(
    level=settings.app.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up BabuAI Agents Service...")
    await db_manager.connect()
    yield
    # Shutdown
    logger.info("Shutting down BabuAI Agents Service...")
    await db_manager.close()

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app.project_name,
        description="Microservice for BabuAI Agent Orchestration",
        version="0.1.0",
        lifespan=lifespan,
        debug=settings.app.debug
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # Adjust for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include Routers
    app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agents"])
    app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
    app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])

    @app.get("/health")
    async def health_check():
        return {"status": "ok", "version": "0.1.0", "env": settings.app.env}

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mugeshbabu_agents.main:app", host="0.0.0.0", port=8000, reload=True)
