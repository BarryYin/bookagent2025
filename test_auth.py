#!/usr/bin/env python3
"""
测试播客页面身份验证功能
"""
import requests
import sys

def test_podcasts_auth():
    """测试播客页面的身份验证"""
    base_url = "http://127.0.0.1:8001"
    
    print("🧪 测试播客页面身份验证功能")
    print("=" * 50)
    
    # 测试1: 未登录访问播客页面
    print("1. 测试未登录访问播客页面...")
    try:
        response = requests.get(f"{base_url}/podcasts", allow_redirects=False)
        if response.status_code == 302:
            redirect_url = response.headers.get('Location', '')
            if '/login' in redirect_url and 'redirect=/podcasts' in redirect_url:
                print("   ✅ 正确重定向到登录页面，包含重定向参数")
            else:
                print(f"   ❌ 重定向URL不正确: {redirect_url}")
        else:
            print(f"   ❌ 应该返回302重定向，实际返回: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 测试2: 未登录访问播客API
    print("2. 测试未登录访问播客API...")
    try:
        response = requests.get(f"{base_url}/api/podcasts")
        if response.status_code == 401:
            data = response.json()
            if data.get('detail') == '请先登录':
                print("   ✅ API正确返回401未授权错误")
            else:
                print(f"   ❌ 错误信息不正确: {data}")
        else:
            print(f"   ❌ 应该返回401，实际返回: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 测试3: 未登录访问播客播放API
    print("3. 测试未登录访问播客播放API...")
    try:
        response = requests.post(f"{base_url}/api/podcasts/test_session/play")
        if response.status_code == 401:
            data = response.json()
            if data.get('detail') == '请先登录':
                print("   ✅ 播放API正确返回401未授权错误")
            else:
                print(f"   ❌ 错误信息不正确: {data}")
        else:
            print(f"   ❌ 应该返回401，实际返回: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    print("\n🎯 测试完成！")
    print("如果所有测试都通过，说明身份验证功能正常工作。")

if __name__ == "__main__":
    test_podcasts_auth()