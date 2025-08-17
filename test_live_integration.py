#!/usr/bin/env python3
"""
实际测试已部署的推荐对话API
验证workflow模型集成是否正常工作
"""

import requests
import json
import time

def test_recommendation_chat():
    """测试推荐对话API"""
    
    # API端点
    base_url = "http://127.0.0.1:8001"
    chat_endpoint = f"{base_url}/api/recommendation/chat/test"  # 使用无认证测试端点
    
    print("🚀 开始测试线上推荐对话API...")
    
    # 测试数据
    test_cases = [
        {
            "name": "基本推荐请求",
            "data": {
                "message": "能帮我推荐几本好书吗？",
                "history": []
            }
        },
        {
            "name": "带历史的对话", 
            "data": {
                "message": "我喜欢科幻小说，有什么推荐吗？",
                "history": [
                    {"role": "user", "content": "你好"},
                    {"role": "assistant", "content": "你好！我是你的阅读顾问"}
                ]
            }
        },
        {
            "name": "特定类型推荐",
            "data": {
                "message": "推荐一些自我成长类的书籍",
                "history": []
            }
        }
    ]
    
    # 检查服务器是否启动
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ 服务器运行正常，状态码: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保appbook.py正在运行")
        return
    
    # 执行测试用例
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 测试 {i}: {test_case['name']}")
        print(f"请求: {test_case['data']['message']}")
        
        try:
            # 直接发送POST请求（不使用认证，因为我们修改了API）
            response = requests.post(
                chat_endpoint,
                json=test_case['data'],
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 成功响应:")
                print(f"   消息: {result.get('message', '无消息')[:100]}...")
                print(f"   推荐数量: {len(result.get('recommendations', []))}")
                print(f"   模型来源: {result.get('source', '未知')}")
                
                if result.get('success'):
                    print(f"   ✨ API响应成功")
                else:
                    print(f"   ⚠️ API返回错误: {result.get('error', '未知错误')}")
                    
            else:
                print(f"❌ HTTP错误: {response.text}")
                
        except requests.exceptions.Timeout:
            print("⏰ 请求超时")
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
            
        # 等待一秒避免请求过于频繁
        time.sleep(1)
    
    print(f"\n🏁 测试完成")

if __name__ == "__main__":
    test_recommendation_chat()
