#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API测试模块
用于测试各个API端点是否正常工作
"""

import requests
import json
import sys
import os
from typing import Dict, Any, Optional, List, Union

# 设置API基础URL
BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
API_PREFIX = "/api"  # API前缀

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
    try:
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/auth/token",
            data={"username": TEST_USERNAME, "password": TEST_PASSWORD, "remember_me": False}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
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

def test_health_endpoint() -> bool:
    """测试健康检查端点"""
    print_colored("\n测试健康检查端点...", Colors.HEADER)
    
    # 测试根健康检查
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print_colored(f"✅ /health 端点正常: {response.json()}", Colors.OKGREEN)
        root_health_ok = True
    else:
        print_colored(f"❌ /health 端点失败: {response.status_code} - {response.text}", Colors.FAIL)
        root_health_ok = False
    
    # 测试API健康检查
    response = requests.get(f"{BASE_URL}{API_PREFIX}/health")
    if response.status_code == 200:
        print_colored(f"✅ {API_PREFIX}/health 端点正常: {response.json()}", Colors.OKGREEN)
        api_health_ok = True
    else:
        print_colored(f"❌ {API_PREFIX}/health 端点失败: {response.status_code} - {response.text}", Colors.FAIL)
        api_health_ok = False
    
    return root_health_ok and api_health_ok

def test_auth_endpoints(token: Optional[str] = None) -> bool:
    """测试认证相关端点"""
    print_colored("\n测试认证相关端点...", Colors.HEADER)
    
    # 如果没有提供token，尝试获取
    if not token:
        token = get_auth_token()
        if not token:
            print_colored("❌ 无法获取认证令牌，跳过认证端点测试", Colors.FAIL)
            return False
    
    # 测试当前用户信息
    response = make_api_request("GET", "/auth/me", token=token)
    if response.status_code == 200:
        user_info = response.json()
        print_colored(f"✅ /auth/me 端点正常: 用户 {user_info.get('username', 'unknown')}", Colors.OKGREEN)
        auth_me_ok = True
    else:
        print_colored(f"❌ /auth/me 端点失败: {response.status_code} - {response.text}", Colors.FAIL)
        auth_me_ok = False
    
    # 测试用户权限
    response = make_api_request("GET", f"/auth/user-permissions?username={TEST_USERNAME}", token=token)
    if response.status_code == 200:
        permissions = response.json()
        print_colored(f"✅ /auth/user-permissions 端点正常: {len(permissions)} 个权限", Colors.OKGREEN)
        permissions_ok = True
    else:
        print_colored(f"❌ /auth/user-permissions 端点失败: {response.status_code} - {response.text}", Colors.FAIL)
        permissions_ok = False
    
    return auth_me_ok and permissions_ok

def test_knowledge_base_endpoints(token: Optional[str] = None) -> bool:
    """测试知识库相关端点"""
    print_colored("\n测试知识库相关端点...", Colors.HEADER)
    
    # 如果没有提供token，尝试获取
    if not token:
        token = get_auth_token()
        if not token:
            print_colored("❌ 无法获取认证令牌，跳过知识库端点测试", Colors.FAIL)
            return False
    
    # 测试获取知识库列表
    response = make_api_request(
        "GET", 
        "/knowledge-bases", 
        token=token,
        params={"page": 1, "pageSize": 10, "search": ""}
    )
    
    if response.status_code == 200:
        kb_data = response.json()
        if isinstance(kb_data, dict) and "items" in kb_data:
            kb_count = len(kb_data.get("items", []))
            print_colored(f"✅ /knowledge-bases 端点正常: 找到 {kb_count} 个知识库", Colors.OKGREEN)
            kb_list_ok = True
        else:
            print_colored(f"⚠️ /knowledge-bases 端点返回格式异常: {kb_data}", Colors.WARNING)
            kb_list_ok = False
    else:
        print_colored(f"❌ /knowledge-bases 端点失败: {response.status_code} - {response.text}", Colors.FAIL)
        kb_list_ok = False
    
    # 尝试创建知识库
    test_kb_name = f"测试知识库-{os.urandom(4).hex()}"
    kb_data = {
        "name": test_kb_name,
        "description": "这是一个自动化测试创建的知识库",
        "type": "技术文档",
        "color": "#1976D2",
        "isPublic": False
    }
    
    response = make_api_request("POST", "/knowledge-bases", token=token, data=kb_data)
    
    if response.status_code == 200 or response.status_code == 201:
        new_kb = response.json()
        kb_id = new_kb.get("id")
        print_colored(f"✅ 创建知识库成功: ID={kb_id}, 名称={test_kb_name}", Colors.OKGREEN)
        kb_create_ok = True
        
        # 测试获取单个知识库
        response = make_api_request("GET", f"/knowledge-bases/{kb_id}", token=token)
        if response.status_code == 200:
            kb_detail = response.json()
            print_colored(f"✅ 获取知识库详情成功: {kb_detail.get('name')}", Colors.OKGREEN)
            kb_get_ok = True
        else:
            print_colored(f"❌ 获取知识库详情失败: {response.status_code} - {response.text}", Colors.FAIL)
            kb_get_ok = False
        
        # 测试删除知识库
        response = make_api_request("DELETE", f"/knowledge-bases/{kb_id}", token=token)
        if response.status_code == 200:
            print_colored(f"✅ 删除知识库成功: ID={kb_id}", Colors.OKGREEN)
            kb_delete_ok = True
        else:
            print_colored(f"❌ 删除知识库失败: {response.status_code} - {response.text}", Colors.FAIL)
            kb_delete_ok = False
    else:
        print_colored(f"❌ 创建知识库失败: {response.status_code} - {response.text}", Colors.FAIL)
        kb_create_ok = False
        kb_get_ok = False
        kb_delete_ok = False
    
    return kb_list_ok and kb_create_ok and kb_get_ok and kb_delete_ok

def run_all_tests():
    """运行所有测试"""
    print_colored("=" * 60, Colors.BOLD)
    print_colored("开始API测试", Colors.BOLD)
    print_colored("=" * 60, Colors.BOLD)
    
    # 测试健康检查
    health_ok = test_health_endpoint()
    
    # 获取认证令牌
    token = get_auth_token()
    
    # 测试认证端点
    auth_ok = test_auth_endpoints(token)
    
    # 测试知识库端点
    kb_ok = test_knowledge_base_endpoints(token)
    
    # 输出测试结果摘要
    print_colored("\n" + "=" * 60, Colors.BOLD)
    print_colored("测试结果摘要", Colors.BOLD)
    print_colored("=" * 60, Colors.BOLD)
    
    print(f"健康检查端点: {'✅ 通过' if health_ok else '❌ 失败'}")
    print(f"认证相关端点: {'✅ 通过' if auth_ok else '❌ 失败'}")
    print(f"知识库相关端点: {'✅ 通过' if kb_ok else '❌ 失败'}")
    
    all_passed = health_ok and auth_ok and kb_ok
    status = "全部通过" if all_passed else "部分失败"
    color = Colors.OKGREEN if all_passed else Colors.FAIL
    
    print_colored(f"\n总体结果: {status}", color)
    
    return all_passed

if __name__ == "__main__":
    # 允许通过命令行参数设置API基础URL
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]
        print(f"使用自定义API基础URL: {BASE_URL}")
    
    success = run_all_tests()
    sys.exit(0 if success else 1) 