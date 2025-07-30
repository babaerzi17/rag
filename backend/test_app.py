"""
Simple test FastAPI application
"""
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/api/knowledge-bases")
def get_knowledge_bases(page: int = 1, pageSize: int = 10, search: str = ""):
    return {
        "items": [
            {
                "id": 1,
                "name": "Test Knowledge Base",
                "description": "This is a test knowledge base",
                "type": "general",
                "status": "active",
                "color": "#1976D2",
                "is_public": False,
                "created_by": 1,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-02T00:00:00"
            }
        ],
        "total": 1,
        "page": page,
        "pageSize": pageSize,
        "search": search
    }

@app.get("/api/auth/user-permissions")
def get_user_permissions(username: str):
    return ["read:knowledge", "write:knowledge", "delete:knowledge"]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 