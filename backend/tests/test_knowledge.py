#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
知识库API测试模块
用于专门测试知识库相关的API端点
"""

import requests
import json
import sys
import os
from typing import Dict, Any, Optional, List, Union
import time

print("测试脚本开始执行...")

# 设置API基础URL
BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
API_PREFIX = "/api"  # API前缀

# 如果通过命令行参数提供了URL，则使用它
if len(sys.argv) > 1:
    BASE_URL = sys.argv[1]
    print(f"使用命令行参数提供的URL: {BASE_URL}")

print(f"API基础URL: {BASE_URL}")
print(f"API前缀: {API_PREFIX}")

# 测试用户凭据
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin"

# 颜色输出
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_colored(text: str, color: str) -> None:
    """打印彩色文本"""
    print(f"{color}{text}{Colors.ENDC}")

def get_auth_token() -> Optional[str]:
    """获取认证令牌"""
    print(f"尝试获取认证令牌，URL: {BASE_URL}{API_PREFIX}/auth/token")
    try:
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/auth/token",
            data={"username": TEST_USERNAME, "password": TEST_PASSWORD, "remember_me": False}
        )
        print(f"认证请求状态码: {response.status_code}")
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"成功获取令牌: {token[:10]}...")
            return token
        else:
            print_colored(f"获取认证令牌失败: {response.status_code} - {response.text}", Colors.FAIL)
            return None
    except Exception as e:
        print_colored(f"获取认证令牌时发生错误: {str(e)}", Colors.FAIL)
        return None

def make_api_request(
    method: str, 
    endpoint: str, 
    token: Optional[str] = None, 
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    files: Optional[Dict[str, Any]] = None
) -> requests.Response:
    """发送API请求"""
    url = f"{BASE_URL}{API_PREFIX}{endpoint}"
    headers = {}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    print(f"发送 {method} 请求到 {url}")
    if params:
        print(f"参数: {params}")
    if data:
        print(f"数据: {data}")
    
    try:
        if method.upper() == "GET":
            return requests.get(url, headers=headers, params=params)
        elif method.upper() == "POST":
            return requests.post(url, headers=headers, json=data, params=params, files=files)
        elif method.upper() == "PUT":
            return requests.put(url, headers=headers, json=data, params=params)
        elif method.upper() == "DELETE":
            return requests.delete(url, headers=headers, params=params)
        else:
            raise ValueError(f"不支持的HTTP方法: {method}")
    except Exception as e:
        print_colored(f"API请求失败: {str(e)}", Colors.FAIL)
        # 创建一个模拟的响应对象
        mock_response = requests.Response()
        mock_response.status_code = 500
        mock_response._content = str(e).encode('utf-8')
        return mock_response

def test_knowledge_base_list(token: str) -> bool:
    """测试获取知识库列表"""
    print_colored("\n测试获取知识库列表...", Colors.HEADER)
    
    response = make_api_request(
        "GET", 
        "/knowledge-bases", 
        token=token,
        params={"page": 1, "pageSize": 10, "search": ""}
    )
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text[:200]}...")
    
    if response.status_code == 200:
        kb_data = response.json()
        if isinstance(kb_data, dict) and "items" in kb_data:
            kb_count = len(kb_data.get("items", []))
            print_colored(f"✅ 获取知识库列表成功: 找到 {kb_count} 个知识库", Colors.OKGREEN)
            return True
        else:
            print_colored(f"⚠️ 知识库列表返回格式异常: {kb_data}", Colors.WARNING)
            return False
    else:
        print_colored(f"❌ 获取知识库列表失败: {response.status_code} - {response.text}", Colors.FAIL)
        return False

def test_create_knowledge_base(token: str) -> Optional[str]:
    """测试创建知识库"""
    print_colored("\n测试创建知识库...", Colors.HEADER)
    
    test_kb_name = f"测试知识库-{int(time.time())}"
    kb_data = {
        "name": test_kb_name,
        "description": "这是一个自动化测试创建的知识库",
        "type": "技术文档",
        "color": "#1976D2",
        "isPublic": False
    }
    
    response = make_api_request("POST", "/knowledge-bases", token=token, data=kb_data)
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text[:200]}...")
    
    if response.status_code == 200 or response.status_code == 201:
        new_kb = response.json()
        kb_id = new_kb.get("id")
        print_colored(f"✅ 创建知识库成功: ID={kb_id}, 名称={test_kb_name}", Colors.OKGREEN)
        return kb_id
    else:
        print_colored(f"❌ 创建知识库失败: {response.status_code} - {response.text}", Colors.FAIL)
        return None

def test_get_knowledge_base(token: str, kb_id: str) -> bool:
    """测试获取单个知识库详情"""
    print_colored(f"\n测试获取知识库详情 (ID={kb_id})...", Colors.HEADER)
    
    response = make_api_request("GET", f"/knowledge-bases/{kb_id}", token=token)
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text[:200]}...")
    
    if response.status_code == 200:
        kb_detail = response.json()
        print_colored(f"✅ 获取知识库详情成功: {kb_detail.get('name')}", Colors.OKGREEN)
        return True
    else:
        print_colored(f"❌ 获取知识库详情失败: {response.status_code} - {response.text}", Colors.FAIL)
        return False

def test_update_knowledge_base(token: str, kb_id: str) -> bool:
    """测试更新知识库"""
    print_colored(f"\n测试更新知识库 (ID={kb_id})...", Colors.HEADER)
    
    update_data = {
        "name": f"更新的知识库-{int(time.time())}",
        "description": "这是更新后的知识库描述",
        "color": "#388E3C"  # 绿色
    }
    
    response = make_api_request("PUT", f"/knowledge-bases/{kb_id}", token=token, data=update_data)
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text[:200]}...")
    
    if response.status_code == 200:
        updated_kb = response.json()
        print_colored(f"✅ 更新知识库成功: {updated_kb.get('name')}", Colors.OKGREEN)
        return True
    else:
        print_colored(f"❌ 更新知识库失败: {response.status_code} - {response.text}", Colors.FAIL)
        return False

def test_delete_knowledge_base(token: str, kb_id: str) -> bool:
    """测试删除知识库"""
    print_colored(f"\n测试删除知识库 (ID={kb_id})...", Colors.HEADER)
    
    response = make_api_request("DELETE", f"/knowledge-bases/{kb_id}", token=token)
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text[:200]}...")
    
    if response.status_code == 200:
        print_colored(f"✅ 删除知识库成功: ID={kb_id}", Colors.OKGREEN)
        return True
    else:
        print_colored(f"❌ 删除知识库失败: {response.status_code} - {response.text}", Colors.FAIL)
        return False

def run_knowledge_tests():
    """运行知识库相关的所有测试"""
    print_colored("=" * 60, Colors.BOLD)
    print_colored("开始知识库API测试", Colors.BOLD)
    print_colored("=" * 60, Colors.BOLD)
    
    # 获取认证令牌
    token = get_auth_token()
    if not token:
        print_colored("❌ 无法获取认证令牌，无法继续测试", Colors.FAIL)
        return False
    
    # 测试获取知识库列表
    list_ok = test_knowledge_base_list(token)
    
    # 测试创建知识库
    kb_id = test_create_knowledge_base(token)
    if not kb_id:
        create_ok = False
        get_ok = False
        update_ok = False
        delete_ok = False
    else:
        create_ok = True
        
        # 测试获取知识库详情
        get_ok = test_get_knowledge_base(token, kb_id)
        
        # 测试更新知识库
        update_ok = test_update_knowledge_base(token, kb_id)
        
        # 测试删除知识库
        delete_ok = test_delete_knowledge_base(token, kb_id)
    
    # 输出测试结果摘要
    print_colored("\n" + "=" * 60, Colors.BOLD)
    print_colored("知识库API测试结果摘要", Colors.BOLD)
    print_colored("=" * 60, Colors.BOLD)
    
    print(f"获取知识库列表: {'✅ 通过' if list_ok else '❌ 失败'}")
    print(f"创建知识库: {'✅ 通过' if create_ok else '❌ 失败'}")
    print(f"获取知识库详情: {'✅ 通过' if get_ok else '❌ 失败'}")
    print(f"更新知识库: {'✅ 通过' if update_ok else '❌ 失败'}")
    print(f"删除知识库: {'✅ 通过' if delete_ok else '❌ 失败'}")
    
    all_passed = list_ok and create_ok and get_ok and update_ok and delete_ok
    status = "全部通过" if all_passed else "部分失败"
    color = Colors.OKGREEN if all_passed else Colors.FAIL
    
    print_colored(f"\n总体结果: {status}", color)
    
    return all_passed

if __name__ == "__main__":
    print("脚本作为主程序运行...")
    # 允许通过命令行参数设置API基础URL
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]
        print(f"使用自定义API基础URL: {BASE_URL}")
    
    success = run_knowledge_tests()
    print(f"测试完成，结果: {'成功' if success else '失败'}")
    sys.exit(0 if success else 1) 