#!/bin/bash

# 等待MySQL服务启动
echo "等待MySQL服务启动..."
while ! nc -z db 3306; do
  sleep 1
done
echo "MySQL服务已启动"

# 等待ChromaDB服务启动
echo "等待ChromaDB服务启动..."
while ! nc -z chromadb 8000; do
  sleep 1
done
echo "ChromaDB服务已启动"

# 初始化数据库
echo "初始化数据库..."
python init_database.py

# 初始化知识库
echo "初始化知识库..."
python init_knowledge.py

# 启动FastAPI应用
echo "启动FastAPI应用..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload 