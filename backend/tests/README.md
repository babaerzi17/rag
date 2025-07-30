# API测试模块

本目录包含用于测试RAG系统API的测试脚本。

## 目录结构

```
tests/
├── __init__.py           # 测试包初始化文件
├── README.md             # 本文档
├── test_api.py           # 通用API测试
├── test_knowledge.py     # 知识库API专项测试
└── ...                   # 其他专项测试文件
```

## 测试文件说明

1. **test_api.py**: 通用API测试脚本，包含对所有主要API端点的基本测试
2. **test_knowledge.py**: 专门针对知识库API的详细测试
3. 其他专项测试文件将根据需要添加

## 如何运行测试

### 运行通用API测试

```bash
# 使用默认本地服务器地址 (http://localhost:8000)
python -m backend.tests.test_api

# 指定自定义服务器地址
python -m backend.tests.test_api http://your-server-address:port
```

### 运行知识库API测试

```bash
# 使用默认本地服务器地址
python -m backend.tests.test_knowledge

# 指定自定义服务器地址
python -m backend.tests.test_knowledge http://your-server-address:port
```

## 添加新的测试

如需添加新的API测试，请遵循以下步骤：

1. 创建新的测试文件，命名为 `test_<功能>.py`
2. 导入必要的模块和函数（可参考现有测试文件）
3. 实现测试函数，每个函数测试一个具体功能
4. 实现一个主运行函数，如 `run_<功能>_tests()`
5. 添加 `if __name__ == "__main__":` 代码块以支持直接运行

## 测试最佳实践

1. 每个测试函数应该专注于测试一个API端点或功能
2. 使用清晰的打印信息指示测试进度和结果
3. 测试应该是独立的，不依赖于其他测试的结果
4. 测试后应该清理创建的资源（如删除测试创建的知识库）
5. 测试应该处理异常情况，不应因错误而中断

## 环境变量

测试脚本支持以下环境变量：

- `API_BASE_URL`: API服务器的基础URL，默认为 `http://localhost:8000`
- `TEST_USERNAME`: 测试用户名，默认为 `admin`
- `TEST_PASSWORD`: 测试用户密码，默认为 `admin`

示例：

```bash
API_BASE_URL=http://example.com:8000 python -m backend.tests.test_api
``` 