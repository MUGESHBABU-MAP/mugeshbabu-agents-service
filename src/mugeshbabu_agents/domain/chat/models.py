from datetime import datetime
from typing import List, Optional, Literal
from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict
from mugeshbabu_agents.core.types import PyObjectId

class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatRequest(BaseModel):
    project_id: str
    document_url: str
    question: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    source_chunks: List[str] = []
    conversation_id: str

class Conversation(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    project_id: str
    document_url: str
    messages: List[Message] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True, json_encoders={ObjectId: str})
