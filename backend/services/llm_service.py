 import os
import json
from typing import List, Dict, Any, Optional, AsyncGenerator
import httpx
import openai
from openai import AsyncOpenAI
import logging

logger = logging.getLogger(__name__)

class ModelConfig:
    """模型配置类"""
    def __init__(self, name: str, provider: str, model_name: str, api_key: str, base_url: str = None, config: Dict[str, Any] = None):
        self.name = name
        self.provider = provider
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url
        self.config = config or {}

class LLMService:
    """大语言模型服务"""
    
    def __init__(self):
        self.models = {}
        self.default_model = None
        # 从环境变量或配置加载模型
        self._load_default_models()
    
    def _load_default_models(self):
        """加载默认模型配置"""
        # OpenAI 模型
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            self.add_model(ModelConfig(
                name="gpt-3.5-turbo",
                provider="openai",
                model_name="gpt-3.5-turbo",
                api_key=openai_api_key,
                base_url="https://api.openai.com/v1"
            ))
        
        # 设置默认模型
        if self.models:
            self.default_model = list(self.models.keys())[0]
    
    def add_model(self, config: ModelConfig):
        """添加模型配置"""
        self.models[config.name] = config
        
    def get_model(self, name: str = None) -> ModelConfig:
        """获取模型配置"""
        if name is None:
            name = self.default_model
        return self.models.get(name)
    
    async def chat_completion(self, messages: List[Dict[str, str]], model_name: str = None, stream: bool = False, **kwargs) -> Any:
        """聊天补全"""
        config = self.get_model(model_name)
        if not config:
            raise ValueError(f"Model {model_name} not found")
        
        if config.provider == "openai":
            return await self._openai_chat_completion(config, messages, stream, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {config.provider}")
    
    async def _openai_chat_completion(self, config: ModelConfig, messages: List[Dict[str, str]], stream: bool = False, **kwargs):
        """OpenAI 聊天补全"""
        client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )
        
        try:
            response = await client.chat.completions.create(
                model=config.model_name,
                messages=messages,
                stream=stream,
                **kwargs
            )
            return response
        except Exception as e:
            logger.error(f"OpenAI API 调用失败: {e}")
            raise

class RAGChatService:
    """RAG 聊天服务"""
    
    def __init__(self, llm_service: LLMService = None):
        self.llm_service = llm_service or LLMService()
        
    async def chat_with_knowledge(self, 
                                question: str, 
                                knowledge_base_id: int,
                                chat_history: List[Dict[str, str]] = None,
                                model_name: str = None,
                                stream: bool = False) -> Any:
        """基于知识库的聊天"""
        
        # TODO: 实现知识检索逻辑
        # 1. 从知识库中检索相关文档
        # 2. 构建上下文
        # 3. 调用LLM生成回答
        
        # 临时实现：直接调用LLM
        messages = []
        if chat_history:
            messages.extend(chat_history)
        
        messages.append({"role": "user", "content": question})
        
        return await self.llm_service.chat_completion(
            messages=messages,
            model_name=model_name,
            stream=stream
        )
    
    async def stream_chat_with_knowledge(self, 
                                       question: str, 
                                       knowledge_base_id: int,
                                       chat_history: List[Dict[str, str]] = None,
                                       model_name: str = None) -> AsyncGenerator[str, None]:
        """流式聊天"""
        response = await self.chat_with_knowledge(
            question=question,
            knowledge_base_id=knowledge_base_id,
            chat_history=chat_history,
            model_name=model_name,
            stream=True
        )
        
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content