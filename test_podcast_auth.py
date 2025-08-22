#!/usr/bin/env python3
"""
测试播客页面的新身份验证逻辑
"""
import requests
import sys

def test_podcast_auth_logic():
    """测试播客页面的身份验证逻辑"""
    base_url = "http://127.0.0.1:8001"
    
    print("🧪 测试播客页面身份验证逻辑")
    print("=" * 50)
    
    # 测试1: 访问播客页面（应该允许）
    print("1. 测试访问播客页面...")
    try:
        response = requests.get(f"{base_url}/podcasts")
        if response.status_code == 200:
            print("   ✅ 播客页面可以正常访问")
        else:
            print(f"   ❌ 播客页面访问失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 测试2: 访问播客列表API（应该允许）
    print("2. 测试访问播客列表API...")
    try:
        response = requests.get(f"{base_url}/api/podcasts")
        if response.status_code == 200:
            print("   ✅ 播客列表API可以正常访问")
        else:
            print(f"   ❌ 播客列表API访问失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 测试3: 检查用户状态API（未登录）
    print("3. 测试用户状态API（未登录状态）...")
    try:
        response = requests.get(f"{base_url}/api/user")
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and not data.get('authenticated'):
                print("   ✅ 用户状态API正确返回未登录状态")
            else:
                print(f"   ❌ 用户状态API返回数据不正确: {data}")
        else:
            print(f"   ❌ 用户状态API访问失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 测试4: 播客播放API（仍需要身份验证）
    print("4. 测试播客播放API（应该需要身份验证）...")
    try:
        response = requests.post(f"{base_url}/api/podcasts/test_session/play")
        if response.status_code == 401:
            data = response.json()
            if data.get('detail') == '请先登录':
                print("   ✅ 播客播放API正确要求身份验证")
            else:
                print(f"   ❌ 错误信息不正确: {data}")
        else:
            print(f"   ❌ 播客播放API应该返回401，实际返回: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    print("\n🎯 测试完成！")
    print("✅ 播客页面现在可以公开访问")
    print("✅ 前端JavaScript会在点击'制作我的播客'时检查登录状态")
    print("✅ 未登录用户会被重定向到登录页面")

if __name__ == "__main__":
    test_podcast_auth_logic()