#!/bin/bash

echo "开始部署AI知识库管理系统..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: 未找到Docker，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "错误: 未找到docker-compose，请先安装docker-compose"
    exit 1
fi

# 创建必要的目录
echo "创建必要的目录..."
mkdir -p uploads
mkdir -p logs
mkdir -p frontend/dist

# 构建前端
echo "构建前端..."
cd frontend
npm install
npm run build
cd ..

# 创建环境配置文件
if [ ! -f backend/.env ]; then
    echo "创建环境配置文件..."
    cp backend/.env.example backend/.env
    echo "请编辑 backend/.env 文件，配置数据库和API密钥"
fi

# 启动服务
echo "启动服务..."
docker-compose up -d

# 等待服务启动
echo "等待服务启动..."
sleep 10

# 初始化数据库
echo "初始化数据库..."
docker-compose exec backend python init_db.py

echo "部署完成！"
echo "前端地址: http://localhost"
echo "后端API: http://localhost:8000"
echo "ChromaDB: http://localhost:8001"
echo ""
echo "默认管理员账户: admin / Admin.123" 