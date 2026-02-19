from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict
from mugeshbabu_agents.core.types import PyObjectId

class Team(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    description: Optional[str] = None
    agent_ids: List[str] = [] # Static list of Agent IDs
    dynamic_filters: Optional[Dict[str, Any]] = None # e.g. {"category": "SAP"}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True, json_encoders={ObjectId: str})

class CreateTeamRequest(BaseModel):
    name: str
    description: Optional[str] = None
    agent_ids: List[str] = []
    dynamic_filters: Optional[Dict[str, Any]] = None
