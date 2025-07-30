"""from sqlalchemy.orm import Session
from .models.user import User
from .models.role import Role
from .models.permission import Permission
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_user(db: Session, username: str, email: str, password: str):
    hashed_password = get_password_hash(password)
    db_user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_role(db: Session, name: str):
    db_role = Role(name=name)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def create_permission(db: Session, name: str):
    db_perm = Permission(name=name)
    db.add(db_perm)
    db.commit()
    db.refresh(db_perm)
    return db_perm

# 添加更多CRUD如get, update, delete
""" 