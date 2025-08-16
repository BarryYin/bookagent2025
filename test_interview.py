#!/usr/bin/env python3
"""
测试访谈功能
"""
import json
import requests
import time

BASE_URL = "http://127.0.0.1:8001"

def test_interview_functionality():
    """测试访谈功能"""
    print("🧪 测试读后感访谈功能...")
    
    # 1. 测试开始访谈
    print("\n1. 测试开始访谈...")
    start_data = {
        "book_title": "三体",
        "book_author": "刘慈欣",
        "user_intro": "我想分享我的读后感"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/interview/start", json=start_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 访谈开始成功: {result}")
            session_id = result.get("session_id")
            
            # 2. 测试发送消息
            print("\n2. 测试发送消息...")
            message_data = {
                "session_id": session_id,
                "message": "我觉得这本书的科幻设定很震撼"
            }
            
            response = requests.post(f"{BASE_URL}/api/interview/message", json=message_data)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 消息发送成功: {result}")
                
                # 3. 测试生成播客
                print("\n3. 测试生成播客...")
                podcast_data = {
                    "session_id": session_id
                }
                
                response = requests.post(f"{BASE_URL}/api/interview/generate-podcast", json=podcast_data)
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ 播客生成成功")
                    print(f"   标题: {result.get('podcast_structure', {}).get('title', 'N/A')}")
                    print(f"   总时长: {result.get('podcast_structure', {}).get('total_duration', 0)}秒")
                else:
                    print(f"❌ 播客生成失败: {response.status_code}")
            else:
                print(f"❌ 消息发送失败: {response.status_code}")
        else:
            print(f"❌ 访谈开始失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_interview_functionality()