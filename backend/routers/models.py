from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.knowledge import ModelConfig
from ..models.user import User
from ..auth.security import get_current_user
from ..services.llm_service import LLMService
from ..schemas import models as schemas

router = APIRouter()
llm_service = LLMService()

@router.get("/", response_model=List[schemas.ModelConfigResponse])
async def get_model_configs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取模型配置列表"""
    # 这里可以添加权限检查，只有管理员才能管理模型配置
    configs = db.query(ModelConfig).all()
    return configs

@router.post("/", response_model=schemas.ModelConfigResponse)
async def create_model_config(
    config: schemas.ModelConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建模型配置"""
    # 检查是否已存在同名配置
    existing = db.query(ModelConfig).filter(
        ModelConfig.name == config.name
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="配置名称已存在")
    
    # 如果设置为默认，先取消其他默认配置
    if config.is_default:
        db.query(ModelConfig).update({"is_default": False})
    
    db_config = ModelConfig(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

@router.get("/{config_id}", response_model=schemas.ModelConfigResponse)
async def get_model_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取模型配置详情"""
    config = db.query(ModelConfig).filter(ModelConfig.id == config_id).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    return config

@router.put("/{config_id}", response_model=schemas.ModelConfigResponse)
async def update_model_config(
    config_id: int,
    config: schemas.ModelConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新模型配置"""
    db_config = db.query(ModelConfig).filter(ModelConfig.id == config_id).first()
    
    if not db_config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    # 如果设置为默认，先取消其他默认配置
    if config.is_default:
        db.query(ModelConfig).update({"is_default": False})
    
    for field, value in config.dict(exclude_unset=True).items():
        setattr(db_config, field, value)
    
    db.commit()
    db.refresh(db_config)
    return db_config

@router.delete("/{config_id}")
async def delete_model_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除模型配置"""
    config = db.query(ModelConfig).filter(ModelConfig.id == config_id).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    db.delete(config)
    db.commit()
    
    return {"message": "配置删除成功"}

@router.post("/{config_id}/test")
async def test_model_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """测试模型配置"""
    config = db.query(ModelConfig).filter(ModelConfig.id == config_id).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    # 测试连接
    result = llm_service.test_connection(config.provider)
    return result

@router.get("/providers/available")
async def get_available_providers():
    """获取可用的提供商信息"""
    providers = llm_service.get_available_providers()
    provider_info = {}
    
    for provider in providers:
        provider_info[provider] = {
            "models": llm_service.get_available_models(provider),
            "connection": llm_service.test_connection(provider)
        }
    
    return provider_info

@router.get("/providers/{provider}/models")
async def get_provider_models(provider: str):
    """获取指定提供商的模型列表"""
    models = llm_service.get_available_models(provider)
    return {"provider": provider, "models": models} 