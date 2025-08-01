import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 导入统一的 Base
from ..models.base import Base

load_dotenv()

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', 'Admin.123')}@{os.getenv('DB_HOST', 'localhost')}/{os.getenv('DB_NAME', 'rag')}"

# 根据环境变量决定是否打印SQL
# 设置 SQLALCHEMY_ECHO=True 在 .env 文件中可以开启SQL打印
echo_sql = os.getenv('SQLALCHEMY_ECHO', 'False').lower() == 'true'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=echo_sql  # 根据 echo_sql 变量设置是否打印SQL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 自动创建表，如果不存在
# 注意：只有在所有模型都被导入后才能创建表
try:
    # 确保所有模型都被导入
    from ..models import *  # 这会导入 __init__.py 中的所有模型
    Base.metadata.create_all(bind=engine)
    print("Successfully created/verified all database tables using MySQL")
except Exception as e:
    print(f"Warning: Could not create tables: {e}") 