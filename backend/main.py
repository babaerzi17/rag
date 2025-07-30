from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os
import sys

# 将当前目录添加到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("FastAPI 应用程序初始化中...")
logger.info(f"Python 路径: {sys.path}")

app = FastAPI(title="RAG Backend API", version="1.0.0", docs_url="/api/docs", openapi_url="/api/openapi.json")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 导入路由
try:
    logger.info("尝试导入路由...")
    from backend.routers.auth import router as auth_router
    from backend.routers.users import router as users_router
    from backend.routers.roles import router as roles_router
    from backend.routers.permissions import router as permissions_router
    from backend.routers.knowledge import router as knowledge_router
    from backend.routers.chat import router as chat_router
    
    logger.info("使用backend前缀导入路由成功")
except ImportError as e:
    logger.error(f"使用backend前缀导入失败: {str(e)}")
    try:
        # 尝试直接导入
        from routers.auth import router as auth_router
        from routers.users import router as users_router
        from routers.roles import router as roles_router
        from routers.permissions import router as permissions_router
        from routers.knowledge import router as knowledge_router
        from routers.chat import router as chat_router
        
        logger.info("直接导入路由成功")
    except ImportError as e2:
        logger.error(f"直接导入路由失败: {str(e2)}")
        sys.exit(1)  # 导入失败退出程序

# 注册路由
try:
    # 添加全局API前缀
    app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
    app.include_router(users_router, prefix="/api/users", tags=["users"])
    app.include_router(roles_router, prefix="/api/roles", tags=["roles"])
    app.include_router(permissions_router, prefix="/api/permissions", tags=["permissions"])
    app.include_router(knowledge_router, prefix="/api/knowledge-bases", tags=["knowledge"])
    app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
    logger.info("所有路由已成功注册")
except NameError as e:
    logger.error(f"注册路由时出错: {str(e)}")
    sys.exit(1)  # 错误退出

# 添加错误处理中间件（使用函数而非导入）
@app.middleware("http")
async def error_handler_middleware(request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        logger.error(f"请求处理错误: {str(exc)}", exc_info=True)
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "服务器内部错误"}
        )

@app.get("/")
def read_root():
    """API根路径，返回欢迎信息"""
    return {"message": "Welcome to RAG Backend", "status": "ok", "version": "1.0.0"} 

@app.get("/health")
def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "rag-backend"}

@app.get("/api/health")
def api_health_check():
    """API健康检查端点"""
    return {"status": "healthy", "api_version": "1.0.0"}

# SPA 路由：任何未被API路由处理的请求都返回 index.html
# 这必须是最后一个路由，以确保API路由优先被匹配
# @app.get("/{full_path:path}")
# def serve_spa(full_path: str):
#     from fastapi.responses import FileResponse
#     return FileResponse("frontend/dist/index.html")

if __name__ == "__main__":
    import uvicorn
    logger.info("启动服务器，监听所有网络接口 (0.0.0.0:8000)")
    uvicorn.run(app, host="0.0.0.0", port=8000)