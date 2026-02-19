from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from mugeshbabu_agents.core.config import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    client: AsyncIOMotorClient | None = None
    master_db: AsyncIOMotorDatabase | None = None

    async def connect(self):
        """Establish connection to MongoDB."""
        logger.info(f"Connecting to MongoDB at {settings.mongo.uri}")
        self.client = AsyncIOMotorClient(
            settings.mongo.uri,
            minPoolSize=settings.mongo.min_pool_size,
            maxPoolSize=settings.mongo.max_pool_size,
            # uuidRepresentation="standard" # Recommended for new projects
        )
        self.master_db = self.client[settings.mongo.db_name]
        logger.info(f"Connected to MongoDB: {settings.mongo.db_name}")

    async def close(self):
        """Close MongoDB connection."""
        if self.client:
            logger.info("Closing MongoDB connection")
            self.client.close()
            self.client = None
            self.master_db = None

    def get_project_db(self, project_id: str) -> AsyncIOMotorDatabase:
        """Get a reference to a project-specific database."""
        if not self.client:
            raise RuntimeError("Database client is not initialized.")
        
        db_name = f"babuai-{project_id}"
        return self.client[db_name]

    def get_master_db(self) -> AsyncIOMotorDatabase:
        if not self.master_db:
            raise RuntimeError("Database client is not initialized.")
        return self.master_db

db_manager = DatabaseManager()

async def get_database() -> AsyncIOMotorDatabase:
    """Dependency to get the master database."""
    return db_manager.get_master_db()
