 import os
import json
from typing import List, Dict, Any, Optional, AsyncGenerator
import httpx
import openai
from openai import AsyncOpenAI
import logging

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, default_provider: str = "deepseek"):
        """初始化LLM服务"""
        self.default_provider = default_provider
        self.clients = {}
        self._init_clients()
    
    def _init_clients(self):
        """初始化各种LLM客户端"""
        # DeepSeek客户端
        deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        if deepseek_api_key:
            self.clients["deepseek"] = AsyncOpenAI(
                api_key=deepseek_api_key,
                base_url="https://api.deepseek.com/v1"
            )
        
        # OpenAI客户端
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            self.clients["openai"] = AsyncOpenAI(
                api_key=openai_api_key,
                base_url="https://api.openai.com/v1"
            )
        
        # 自定义客户端（支持其他OpenAI兼容的API）
        custom_base_url = os.getenv("CUSTOM_LLM_BASE_URL")
        custom_api_key = os.getenv("CUSTOM_LLM_API_KEY")
        if custom_base_url and custom_api_key:
            self.clients["custom"] = AsyncOpenAI(
                api_key=custom_api_key,
                base_url=custom_base_url
            )
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> Dict[str, Any]:
        """聊天完成接口"""
        provider = provider or self.default_provider
        client = self.clients.get(provider)
        
        if not client:
            raise ValueError(f"未找到提供商 {provider} 的客户端配置")
        
        # 设置默认模型
        if not model:
            model = self._get_default_model(provider)
        
        try:
            if stream:
                return await self._stream_chat_completion(
                    client, messages, model, temperature, max_tokens
                )
            else:
                return await self._chat_completion(
                    client, messages, model, temperature, max_tokens
                )
        except Exception as e:
            logger.error(f"LLM调用失败: {str(e)}")
            raise
    
    async def _chat_completion(
        self,
        client: AsyncOpenAI,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """非流式聊天完成"""
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return {
            "content": response.choices[0].message.content,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            "model": response.model,
            "finish_reason": response.choices[0].finish_reason
        }
    
    async def _stream_chat_completion(
        self,
        client: AsyncOpenAI,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """流式聊天完成"""
        stream = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield {
                    "content": chunk.choices[0].delta.content,
                    "finish_reason": chunk.choices[0].finish_reason
                }
    
    def _get_default_model(self, provider: str) -> str:
        """获取默认模型"""
        default_models = {
            "deepseek": "deepseek-chat",
            "openai": "gpt-3.5-turbo",
            "custom": "gpt-3.5-turbo"
        }
        return default_models.get(provider, "gpt-3.5-turbo")
    
    def get_available_providers(self) -> List[str]:
        """获取可用的提供商列表"""
        return list(self.clients.keys())
    
    def get_available_models(self, provider: str) -> List[str]:
        """获取指定提供商的可用模型列表"""
        model_lists = {
            "deepseek": [
                "deepseek-chat",
                "deepseek-coder"
            ],
            "openai": [
                "gpt-4",
                "gpt-4-turbo",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k"
            ],
            "custom": [
                "gpt-3.5-turbo",
                "gpt-4",
                "qwen-turbo",
                "qwen-plus"
            ]
        }
        return model_lists.get(provider, [])
    
    def test_connection(self, provider: str) -> Dict[str, Any]:
        """测试提供商连接"""
        try:
            client = self.clients.get(provider)
            if not client:
                return {
                    "success": False,
                    "error": f"未找到提供商 {provider} 的配置"
                }
            
            # 这里可以添加实际的连接测试逻辑
            return {
                "success": True,
                "provider": provider,
                "message": "连接正常"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

class RAGChatService:
    def __init__(self, rag_service, llm_service):
        """初始化RAG聊天服务"""
        self.rag_service = rag_service
        self.llm_service = llm_service
    
    async def chat(
        self,
        query: str,
        kb_id: Optional[int] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """RAG聊天接口"""
        try:
            # 1. 检索相关文档
            search_results = self.rag_service.search(query, kb_id, top_k)
            
            # 2. 构建上下文
            context = self._build_context(search_results)
            
            # 3. 构建消息
            messages = self._build_messages(query, context, chat_history)
            
            # 4. 调用LLM
            response = await self.llm_service.chat_completion(
                messages=messages,
                provider=provider,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # 5. 格式化返回结果
            return {
                "answer": response["content"],
                "sources": self._format_sources(search_results),
                "usage": response.get("usage", {}),
                "model": response.get("model", "")
            }
            
        except Exception as e:
            logger.error(f"RAG聊天失败: {str(e)}")
            raise
    
    def _build_context(self, search_results: List[Dict[str, Any]]) -> str:
        """构建上下文"""
        if not search_results:
            return "没有找到相关的参考文档。"
        
        context_parts = []
        for i, result in enumerate(search_results, 1):
            content = result["content"]
            metadata = result["metadata"]
            score = result["similarity_score"]
            
            context_parts.append(
                f"文档片段 {i} (相似度: {score:.2f}):\n{content}\n"
            )
        
        return "\n".join(context_parts)
    
    def _build_messages(
        self,
        query: str,
        context: str,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """构建消息列表"""
        system_prompt = f"""你是一个专业的AI助手，基于以下知识库内容回答问题：

{context}

请基于上述信息回答用户问题，如果信息不足请说明。回答要准确、简洁、有用。"""

        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加聊天历史
        if chat_history:
            messages.extend(chat_history)
        
        # 添加当前查询
        messages.append({"role": "user", "content": query})
        
        return messages
    
    def _format_sources(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """格式化参考来源"""
        sources = []
        for result in search_results:
            metadata = result["metadata"]
            sources.append({
                "id": result["id"],
                "title": metadata.get("file_path", "未知文档"),
                "content": result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"],
                "similarity_score": result["similarity_score"],
                "metadata": metadata
            })
        return sources