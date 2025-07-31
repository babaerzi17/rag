from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# ChatSession schemas
class ChatSessionBase(BaseModel):
    title: Optional[str] = None
    knowledge_base_id: Optional[int] = None  # Changed from kb_id
    model_config: Optional[Dict[str, Any]] = None

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionUpdate(BaseModel):
    title: Optional[str] = None
    knowledge_base_id: Optional[int] = None  # Changed from kb_id
    model_config: Optional[Dict[str, Any]] = None

class ChatSessionResponse(ChatSessionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ChatMessage schemas
class ChatMessageBase(BaseModel):
    content: str

class ChatMessageCreate(ChatMessageBase):
    include_history: bool = True
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000
    top_k: int = 5

class ChatMessageResponse(ChatMessageBase):
    id: int
    session_id: int
    role: str
    sources: Optional[List[Dict[str, Any]]] = None
    message_metadata: Optional[Dict[str, Any]] = None  # Changed from metadata
    created_at: datetime
    
    class Config:
        from_attributes = True

# Stream chat schemas
class StreamChatRequest(BaseModel):
    session_id: int
    message: str
    include_history: bool = True
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000
    top_k: int = 5

# Test connection schemas
class TestConnectionRequest(BaseModel):
    provider: str 