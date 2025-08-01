# 这个文件现在完全使用 MySQL 配置，不再使用 SQLite
# 所有数据库相关的配置都从 config.database 导入

from .config.database import engine, SessionLocal, Base, get_db

# 自动创建表，如果不存在
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: Could not create tables: {e}")

# 为了保持向后兼容，重新导出所有需要的对象
__all__ = ['engine', 'SessionLocal', 'Base', 'get_db'] 