from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

from pydantic import BaseModel # Import BaseModel

# Ensure import paths are correct
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from ..config.database import get_db
    from ..schemas import Token, User
    from ..auth.security import (create_access_token, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES, 
                                get_current_user, REMEMBER_ME_TOKEN_EXPIRE_DAYS)
    from ..models.user import User as DBUser
    from ..common.crud import authenticate_user # Import authenticate_user
except ImportError:
    # Try using absolute imports
    from config.database import get_db
    from schemas import Token, User
    from auth.security import (create_access_token, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES, 
                                get_current_user, REMEMBER_ME_TOKEN_EXPIRE_DAYS)
    from models.user import User as DBUser
    from common.crud import authenticate_user # Import authenticate_user

import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

router = APIRouter()

# New Pydantic model for login requests
class LoginForm(BaseModel):
    username: str
    password: str
    remember_me: bool = False # Added remember_me field, default False

@router.post("/token", response_model=Token)
async def login_for_access_token(
    username: str = Form(...),
    password: str = Form(...),
    remember_me: bool = Form(False),
    db: Session = Depends(get_db)
):
    logger.info(f"Attempting to get access token for user '{username}'")
    user = authenticate_user(db, username, password)
    if not user:
        logger.warning(f"Authentication failed for user '{username}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Ensure user roles are loaded
    _ = user.roles

    # Set expiration time based on remember_me
    access_token_expires = None
    if remember_me:
        access_token_expires = timedelta(days=REMEMBER_ME_TOKEN_EXPIRE_DAYS)
    else:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={"sub": user.username, "id": user.id, "roles": [role.name for role in user.roles]},
        expires_delta=access_token_expires,
        remember_me=remember_me # Pass remember_me status
    )
    logger.info(f"Access token successfully created for user '{username}'")
    
    # Ensure user roles are properly serialized
    user_dict = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "roles": [{"id": role.id, "name": role.name, "description": role.description} for role in user.roles],
        "permissions": []  # Add empty permissions list to match frontend expectations
    }
    
    logger.info(f"Returning user information: {user_dict}")
    return {"access_token": access_token, "token_type": "bearer", "user": user_dict}

@router.get("/user-permissions")
async def get_user_permissions(
    username: str,
    db: Session = Depends(get_db)
):
    """Get user's permission list"""
    logger.info(f"Getting user permissions: username={username}")
    # Get user permissions from database
    try:
        from ..common.crud import get_user_by_username
    except ImportError:
        from backend.common.crud import get_user_by_username
        
    user = get_user_by_username(db, username)
    if not user:
        logger.warning(f"User does not exist: username={username}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")
    
    # Get permissions list from all user roles
    permissions = set()
    for role in user.roles:
        for perm in role.permissions:
            permissions.add(perm.name)
            
    return list(permissions)

@router.get("/me", response_model=User)
async def read_users_me(current_user: DBUser = Depends(get_current_user)):
    logger.info(f"Getting current user information: {current_user.username}")
    return current_user

# Helper route for testing current user and permissions
@router.get("/test_current_user_from_db", response_model=User)
async def get_current_user_from_db(current_user: DBUser = Depends(get_current_user)):
    logger.info(f"Test route: Getting current user (loading complete info from database): {current_user.username}")
    # Ensure roles and permissions relationships are loaded
    _ = current_user.roles
    _ = current_user.permissions
    return current_user