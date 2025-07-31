from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os
import sys

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("FastAPI application initializing...")
logger.info(f"Python path: {sys.path}")

app = FastAPI(title="RAG Backend API", version="1.0.0", docs_url="/api/docs", openapi_url="/api/openapi.json")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, in production should be restricted to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
try:
    logger.info("Attempting to import routers...")
    from backend.routers.auth import router as auth_router
    from backend.routers.users import router as users_router
    from backend.routers.roles import router as roles_router
    from backend.routers.permissions import router as permissions_router
    from backend.routers.knowledge import router as knowledge_router
    from backend.routers.chat import router as chat_router
    
    logger.info("Successfully imported routers with backend prefix")
except ImportError as e:
    logger.error(f"Failed to import with backend prefix: {str(e)}")
    try:
        # Try direct import
        from routers.auth import router as auth_router
        from routers.users import router as users_router
        from routers.roles import router as roles_router
        from routers.permissions import router as permissions_router
        from routers.knowledge import router as knowledge_router
        from routers.chat import router as chat_router
        
        logger.info("Successfully imported routers directly")
    except ImportError as e2:
        logger.error(f"Failed to import routers directly: {str(e2)}")
        sys.exit(1)  # Exit program if import fails

# Register routers
try:
    # Add global API prefix
    app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
    app.include_router(users_router, prefix="/api/users", tags=["users"])
    app.include_router(roles_router, prefix="/api/roles", tags=["roles"])
    app.include_router(permissions_router, prefix="/api/permissions", tags=["permissions"])
    app.include_router(knowledge_router, prefix="/api/knowledge-bases", tags=["knowledge"])
    app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
    logger.info("All routers successfully registered")
except NameError as e:
    logger.error(f"Error registering routers: {str(e)}")
    sys.exit(1)  # Exit on error

# Add error handling middleware (using function instead of import)
@app.middleware("http")
async def error_handler_middleware(request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        logger.error(f"Request processing error: {str(exc)}", exc_info=True)
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Internal server error"}
        )

@app.get("/")
def read_root():
    """API root path, returns welcome message"""
    return {"message": "Welcome to RAG Backend", "status": "ok", "version": "1.0.0"} 

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "rag-backend"}

@app.get("/api/health")
def api_health_check():
    """API health check endpoint"""
    return {"status": "healthy", "api_version": "1.0.0"}

# SPA routing: any request not handled by API routes returns index.html
# This must be the last route to ensure API routes are matched first
# @app.get("/{full_path:path}")
# def serve_spa(full_path: str):
#     from fastapi.responses import FileResponse
#     return FileResponse("frontend/dist/index.html")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server, listening on all network interfaces (0.0.0.0:8000)")
    uvicorn.run(app, host="0.0.0.0", port=8000)