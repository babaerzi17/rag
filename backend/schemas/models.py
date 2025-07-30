from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class ModelConfigBase(BaseModel):
    name: str
    provider: str
    model_name: str
    base_url: Optional[str] = None
    is_default: bool = False
    config: Optional[Dict[str, Any]] = None

class ModelConfigCreate(ModelConfigBase):
    api_key: str

class ModelConfigUpdate(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model_name: Optional[str] = None
    is_default: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None

class ModelConfigResponse(BaseModel):
    id: int
    name: str
    provider: str
    model_name: str
    base_url: Optional[str] = None
    is_default: bool
    config: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True 