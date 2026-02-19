from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, handler):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        json_schema = handler(core_schema)
        json_schema.update(type="string")
        return json_schema

class MCPConfig(BaseModel):
    """Configuration for Model Context Protocol servers."""
    server_name: str
    server_url: Optional[str] = None
    # We might need to resolve auth tokens here
    auth_config: Optional[Dict[str, Any]] = None

class Agent(BaseModel):
    """Master Agent Definition."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    description: Optional[str] = None
    system_prompt: str
    mcp_servers: List[MCPConfig] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True, json_encoders={ObjectId: str})

class AgentInstance(BaseModel):
    """Runtime execution instance of an Agent."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    master_agent_id: str # Reference to the parent agent
    project_id: str
    input_data: Dict[str, Any]
    status: str = "PENDING"  # PENDING, RUNNING, COMPLETED, FAILED
    result: Optional[Dict[str, Any]] = None
    logs: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True, json_encoders={ObjectId: str})
