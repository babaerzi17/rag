from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from ..database import get_db
from ..models.chat import ChatSession, ChatMessage
from ..models.user import User
from ..auth.security import get_current_user
from ..services.llm_service import LLMService, RAGChatService
from ..services.rag_service import RAGService
from ..schemas import chat as schemas

router = APIRouter()

# 初始化服务
llm_service = LLMService()
rag_service = RAGService()
rag_chat_service = RAGChatService(llm_service)

@router.get("/sessions", response_model=List[schemas.ChatSessionResponse])
async def get_chat_sessions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取聊天会话列表"""
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.updated_at.desc()).offset(skip).limit(limit).all()
    
    return sessions

@router.post("/sessions", response_model=schemas.ChatSessionResponse)
async def create_chat_session(
    session: schemas.ChatSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建聊天会话"""
    db_session = ChatSession(
        **session.dict(),
        user_id=current_user.id
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@router.get("/sessions/{session_id}", response_model=schemas.ChatSessionResponse)
async def get_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取聊天会话详情"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    return session

@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除聊天会话"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    db.delete(session)
    db.commit()
    
    return {"message": "会话删除成功"}

@router.get("/sessions/{session_id}/messages", response_model=List[schemas.ChatMessageResponse])
async def get_chat_messages(
    session_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取聊天消息历史"""
    # 检查会话权限
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at.asc()).offset(skip).limit(limit).all()
    
    return messages

@router.post("/sessions/{session_id}/messages", response_model=schemas.ChatMessageResponse)
async def send_message(
    session_id: int,
    message: schemas.ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """发送消息"""
    # 检查会话权限
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    # 保存用户消息
    user_message = ChatMessage(
        session_id=session_id,
        role="user",
        content=message.content
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    
    try:
        # 获取聊天历史
        chat_history = []
        if message.include_history:
            history_messages = db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.created_at.desc()).limit(10).all()
            
            # 转换为消息格式
            for msg in reversed(history_messages):
                chat_history.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # 调用RAG聊天服务
        response = await rag_chat_service.chat(
            query=message.content,
            kb_id=session.kb_id,
            chat_history=chat_history,
            provider=message.provider,
            model=message.model,
            temperature=message.temperature,
            max_tokens=message.max_tokens,
            top_k=message.top_k
        )
        
        # 保存AI回复
        ai_message = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=response["answer"],
            sources=response["sources"],
            metadata={
                "usage": response["usage"],
                "model": response["model"]
            }
        )
        db.add(ai_message)
        db.commit()
        db.refresh(ai_message)
        
        # 更新会话标题（如果是第一条消息）
        if not session.title:
            session.title = message.content[:50] + "..." if len(message.content) > 50 else message.content
            db.commit()
        
        return ai_message
        
    except Exception as e:
        # 保存错误消息
        error_message = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=f"抱歉，处理您的消息时出现错误: {str(e)}",
            metadata={"error": str(e)}
        )
        db.add(error_message)
        db.commit()
        db.refresh(error_message)
        
        return error_message

@router.post("/stream")
async def stream_chat(
    request: schemas.StreamChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """流式聊天接口"""
    # 检查会话权限
    session = db.query(ChatSession).filter(
        ChatSession.id == request.session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    # 保存用户消息
    user_message = ChatMessage(
        session_id=request.session_id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    
    try:
        # 获取聊天历史
        chat_history = []
        if request.include_history:
            history_messages = db.query(ChatMessage).filter(
                ChatMessage.session_id == request.session_id
            ).order_by(ChatMessage.created_at.desc()).limit(10).all()
            
            for msg in reversed(history_messages):
                chat_history.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # 调用流式RAG聊天
        response = await rag_chat_service.chat(
            query=request.message,
            kb_id=session.kb_id,
            chat_history=chat_history,
            provider=request.provider,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_k=request.top_k,
            stream=True
        )
        
        # 这里应该返回流式响应
        # 由于FastAPI的流式响应比较复杂，这里先返回普通响应
        return {"message": "流式聊天功能开发中"}
        
    except Exception as e:
        return {"error": str(e)}

@router.get("/providers")
async def get_available_providers():
    """获取可用的LLM提供商"""
    providers = llm_service.get_available_providers()
    provider_info = {}
    
    for provider in providers:
        provider_info[provider] = {
            "models": llm_service.get_available_models(provider),
            "connection": llm_service.test_connection(provider)
        }
    
    return provider_info

@router.post("/test-connection")
async def test_provider_connection(
    request: schemas.TestConnectionRequest
):
    """测试提供商连接"""
    result = llm_service.test_connection(request.provider)
    return result 