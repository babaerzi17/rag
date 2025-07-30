# AI知识库管理系统部署指南

## 概述

本文档详细说明了AI知识库管理系统的部署方案，包括开发环境、测试环境和生产环境的部署步骤。

## 系统架构

### 技术栈
- **前端**: Vue 3 + Element Plus + TypeScript
- **后端**: FastAPI + SQLAlchemy + MySQL
- **向量数据库**: ChromaDB
- **缓存**: Redis
- **异步任务**: Celery
- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx

### 服务组件
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx (80)    │    │   Frontend      │    │   Backend       │
│   (反向代理)     │◄──►│   (Vue 3)       │◄──►│   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                       ┌─────────────────┐            │
                       │   MySQL         │◄───────────┤
                       │   (数据库)       │            │
                       └─────────────────┘            │
                                                       │
                       ┌─────────────────┐            │
                       │   ChromaDB      │◄───────────┤
                       │   (向量数据库)   │            │
                       └─────────────────┘            │
                                                       │
                       ┌─────────────────┐            │
                       │   Redis         │◄───────────┘
                       │   (缓存/队列)    │
                       └─────────────────┘
```

## 环境要求

### 最低配置
- **CPU**: 2核心
- **内存**: 4GB RAM
- **存储**: 20GB 可用空间
- **网络**: 稳定的互联网连接

### 推荐配置
- **CPU**: 4核心
- **内存**: 8GB RAM
- **存储**: 50GB SSD
- **网络**: 100Mbps以上带宽

### 软件要求
- **操作系统**: Linux (Ubuntu 20.04+ / CentOS 8+)
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 2.20+

## 部署方案

### 方案一：Docker Compose 部署（推荐）

#### 1. 环境准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 将当前用户添加到docker组
sudo usermod -aG docker $USER
```

#### 2. 项目部署

```bash
# 克隆项目
git clone <repository-url>
cd rag2

# 创建环境配置文件
cp .env.example .env

# 编辑环境配置
nano .env
```

#### 3. 环境配置

创建 `.env` 文件：

```env
# 数据库配置
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_DATABASE=rag_system
MYSQL_USER=rag_user
MYSQL_PASSWORD=your_db_password

# Redis配置
REDIS_PASSWORD=your_redis_password

# 后端配置
BACKEND_SECRET_KEY=your_secret_key_here
BACKEND_DEBUG=false
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# 前端配置
VITE_API_BASE_URL=http://localhost/api

# 文件存储配置
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=104857600

# LLM配置
DEFAULT_MODEL_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_deepseek_api_key
OPENAI_API_KEY=your_openai_api_key

# 监控配置
ENABLE_MONITORING=true
LOG_LEVEL=INFO
```

#### 4. 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 5. 初始化数据库

```bash
# 进入后端容器
docker-compose exec backend bash

# 运行数据库初始化
python init_database.py

# 退出容器
exit
```

#### 6. 验证部署

```bash
# 检查服务健康状态
curl http://localhost/health

# 检查API状态
curl http://localhost/api/health

# 访问前端界面
# 浏览器打开: http://localhost
```

### 方案二：手动部署

#### 1. 系统环境准备

```bash
# 安装Python 3.9+
sudo apt install python3.9 python3.9-venv python3.9-dev

# 安装MySQL
sudo apt install mysql-server

# 安装Redis
sudo apt install redis-server

# 安装Nginx
sudo apt install nginx

# 安装Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### 2. 数据库配置

```sql
-- 创建数据库
CREATE DATABASE rag_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户
CREATE USER 'rag_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON rag_system.* TO 'rag_user'@'localhost';
FLUSH PRIVILEGES;
```

#### 3. 后端部署

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python3.9 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
nano .env

# 初始化数据库
python init_database.py

# 启动后端服务
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### 4. 前端部署

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 构建生产版本
npm run build

# 配置Nginx
sudo nano /etc/nginx/sites-available/rag-system
```

Nginx配置：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/rag2/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API代理
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 文件上传
    location /uploads/ {
        alias /path/to/rag2/backend/uploads/;
    }
}
```

```bash
# 启用站点
sudo ln -s /etc/nginx/sites-available/rag-system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 环境配置

### 开发环境

```bash
# 启动开发环境
docker-compose -f docker-compose.dev.yml up -d

# 前端开发服务器
cd frontend
npm run dev

# 后端开发服务器
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 测试环境

```bash
# 启动测试环境
docker-compose -f docker-compose.test.yml up -d

# 运行测试
python test_integration.py
```

### 生产环境

```bash
# 启动生产环境
docker-compose -f docker-compose.prod.yml up -d

# 配置SSL证书
sudo certbot --nginx -d your-domain.com
```

## 监控和维护

### 系统监控

```bash
# 查看服务状态
docker-compose ps

# 查看资源使用
docker stats

# 查看日志
docker-compose logs -f [service_name]

# 系统监控面板
# 访问: http://localhost/admin/settings
```

### 备份策略

```bash
# 数据库备份
docker-compose exec mysql mysqldump -u root -p rag_system > backup_$(date +%Y%m%d_%H%M%S).sql

# 文件备份
tar -czf uploads_backup_$(date +%Y%m%d_%H%M%S).tar.gz backend/uploads/

# 自动备份脚本
chmod +x scripts/backup.sh
crontab -e
# 添加: 0 2 * * * /path/to/rag2/scripts/backup.sh
```

### 日志管理

```bash
# 查看应用日志
docker-compose logs -f backend

# 查看Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# 日志轮转配置
sudo nano /etc/logrotate.d/rag-system
```

### 性能优化

```bash
# 数据库优化
docker-compose exec mysql mysql -u root -p
# 执行数据库优化命令

# 缓存优化
docker-compose exec redis redis-cli
# 配置Redis缓存策略

# 前端优化
cd frontend
npm run build
# 启用gzip压缩
```

## 故障排除

### 常见问题

1. **服务无法启动**
   ```bash
   # 检查端口占用
   sudo netstat -tlnp | grep :8000
   
   # 检查Docker状态
   sudo systemctl status docker
   
   # 查看详细错误日志
   docker-compose logs [service_name]
   ```

2. **数据库连接失败**
   ```bash
   # 检查MySQL服务
   sudo systemctl status mysql
   
   # 检查数据库连接
   docker-compose exec backend python -c "from database import engine; print(engine.execute('SELECT 1').fetchone())"
   ```

3. **前端无法访问API**
   ```bash
   # 检查CORS配置
   # 检查Nginx代理配置
   # 检查防火墙设置
   sudo ufw status
   ```

4. **文件上传失败**
   ```bash
   # 检查目录权限
   sudo chown -R www-data:www-data backend/uploads/
   sudo chmod -R 755 backend/uploads/
   
   # 检查磁盘空间
   df -h
   ```

### 性能调优

1. **数据库优化**
   ```sql
   -- 优化MySQL配置
   SET GLOBAL innodb_buffer_pool_size = 1073741824; -- 1GB
   SET GLOBAL max_connections = 200;
   ```

2. **Redis优化**
   ```bash
   # 配置Redis内存策略
   docker-compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
   ```

3. **Nginx优化**
   ```nginx
   # 启用gzip压缩
   gzip on;
   gzip_types text/plain text/css application/json application/javascript;
   
   # 配置缓存
   location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
       expires 1y;
       add_header Cache-Control "public, immutable";
   }
   ```

## 安全配置

### 网络安全

```bash
# 配置防火墙
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# 配置SSL证书
sudo certbot --nginx -d your-domain.com
```

### 应用安全

```bash
# 更新密钥
# 修改.env文件中的SECRET_KEY

# 配置HTTPS重定向
# 在Nginx配置中添加SSL重定向

# 启用安全头
# 在Nginx配置中添加安全头
```

### 数据安全

```bash
# 数据库加密
# 配置MySQL SSL连接

# 文件加密
# 配置文件存储加密

# 备份加密
# 配置备份文件加密
```

## 扩展部署

### 负载均衡

```bash
# 使用HAProxy或Nginx进行负载均衡
# 配置多个后端实例

# 使用Redis集群
# 配置Redis主从复制
```

### 高可用部署

```bash
# 数据库主从复制
# 配置MySQL主从同步

# 应用集群
# 使用Kubernetes或Docker Swarm
```

### 微服务架构

```bash
# 服务拆分
# 将不同功能拆分为独立服务

# 服务发现
# 使用Consul或etcd进行服务发现

# API网关
# 使用Kong或Envoy作为API网关
```

## 总结

本文档提供了完整的部署方案，包括：

1. **Docker Compose部署**（推荐）：简单快速，适合中小型部署
2. **手动部署**：更灵活，适合大型生产环境
3. **监控维护**：系统监控、备份策略、日志管理
4. **故障排除**：常见问题解决方案
5. **安全配置**：网络安全、应用安全、数据安全
6. **扩展部署**：负载均衡、高可用、微服务架构

根据实际需求选择合适的部署方案，并按照文档步骤进行部署。如有问题，请参考故障排除部分或联系技术支持。 