#!/usr/bin/env python3
import requests

# 测试登录流程
session = requests.Session()
base_url = "http://127.0.0.1:8001"

# 1. 检查初始状态
print("1. 检查初始登录状态:")
response = session.get(f"{base_url}/api/user")
print(f"   状态: {response.json()}")

# 2. 尝试登录（需要先有用户）
print("\n2. 尝试登录:")
login_data = {
    "username": "test",
    "password": "123456"
}
response = session.post(f"{base_url}/api/login", json=login_data)
print(f"   登录响应: {response.status_code}")
if response.status_code == 200:
    print(f"   登录结果: {response.json()}")
else:
    print(f"   登录失败: {response.text}")

# 3. 检查登录后状态
print("\n3. 检查登录后状态:")
response = session.get(f"{base_url}/api/user")
print(f"   状态: {response.json()}")

# 4. 检查cookies
print(f"\n4. Session cookies: {session.cookies}")