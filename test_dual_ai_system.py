#!/usr/bin/env python3
"""
测试双AI协作访谈系统
"""
import asyncio
import json
import requests
import time

BASE_URL = "http://127.0.0.1:8001"

async def test_dual_ai_interview():
    """测试完整的双AI协作访谈流程"""
    print("🚀 开始测试双AI协作访谈系统...")
    
    # 1. 开始访谈
    print("\n📚 1. 开始访谈...")
    start_data = {
        "book_title": "三体",
        "book_author": "刘慈欣",
        "user_intro": "我想分享我对这本书的读后感"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/interview/start", json=start_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 访谈开始成功!")
            print(f"   会话ID: {result.get('session_id')}")
            print(f"   开场白: {result.get('opening_message')}")
            print(f"   总问题数: {result.get('total_questions')}")
            session_id = result.get("session_id")
        else:
            print(f"❌ 访谈开始失败: {response.status_code} - {response.text}")
            return
            
    except Exception as e:
        print(f"❌ 访谈开始异常: {e}")
        return
    
    # 2. 模拟用户回答问题
    print(f"\n💬 2. 模拟用户回答（对话AI提问）...")
    test_answers = [
        "这本书让我对宇宙有了全新的认识，特别是黑暗森林法则",
        "叶文洁这个角色很复杂，她的选择让我思考人性的复杂",
        "读的时候既震撼又恐惧，科幻设定太宏大了",
        "让我重新思考人类文明的脆弱性和傲慢",
        "我觉得这本书会影响我对科学和宇宙的看法"
    ]
    
    question_count = 0
    for i, answer in enumerate(test_answers):
        print(f"\n   第{i+1}轮对话:")
        
        # 如果是第一轮，先获取第一个问题
        if i == 0:
            message_data = {
                "session_id": session_id,
                "message": "开始访谈"
            }
        else:
            message_data = {
                "session_id": session_id,
                "message": answer
            }
        
        try:
            response = requests.post(f"{BASE_URL}/api/interview/message", json=message_data)
            if response.status_code == 200:
                result = response.json()
                print(f"   API响应类型: {result.get('type', '未知')}")
                
                if result.get('type') == 'question':
                    print(f"   💬 对话AI问题: {result.get('question')}")
                    print(f"   📊 进度: {result.get('current_question')}/{result.get('total_questions')}")
                    question_count = result.get('current_question', 0)
                    
                elif result.get('type') == 'completion':
                    print(f"   ✅ 访谈完成: {result.get('message')}")
                    print(f"   🎙️ 准备生成播客: {result.get('ready_for_podcast')}")
                    break
                    
                elif result.get('error'):
                    print(f"   ❌ 错误: {result.get('error')}")
                    
                else:
                    print(f"   ⚠️ 未知响应格式: {result}")
                    
            else:
                print(f"   ❌ 消息发送失败: {response.status_code} - {response.text}")
                break
                
        except Exception as e:
            print(f"   ❌ 消息发送异常: {e}")
            break
        
        # 如果获得了问题，需要再发送答案
        if i == 0 and result.get('type') == 'question':
            print(f"   👤 用户回答: {answer}")
            answer_data = {
                "session_id": session_id,
                "message": answer
            }
            
            try:
                response = requests.post(f"{BASE_URL}/api/interview/message", json=answer_data)
                if response.status_code == 200:
                    result = response.json()
                    if result.get('type') == 'question':
                        print(f"   💬 下个问题: {result.get('question')}")
                        print(f"   📊 进度: {result.get('current_question')}/{result.get('total_questions')}")
                    elif result.get('type') == 'completion':
                        print(f"   ✅ 访谈完成: {result.get('message')}")
                        print(f"   🎙️ 准备生成播客: {result.get('ready_for_podcast')}")
                        break
            except Exception as e:
                print(f"   ❌ 回答发送异常: {e}")
                break
        
        time.sleep(1)  # 避免请求过快
    
    # 3. 生成播客
    print(f"\n🎙️ 3. 生成播客（播客AI工作）...")
    try:
        podcast_data = {
            "session_id": session_id
        }
        
        print("   📻 调用播客生成API...")
        response = requests.post(f"{BASE_URL}/api/interview/generate-podcast", json=podcast_data)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print(f"   ✅ 播客生成成功!")
                print(f"   📖 书籍: 《{result.get('book_title')}》- {result.get('book_author')}")
                print(f"   🎵 音频URL: {result.get('audio_url')}")
                print(f"   💾 本地文件: {result.get('local_file')}")
                print(f"   📝 脚本长度: {len(result.get('script', '')) if result.get('script') else 0} 字符")
                
            else:
                print(f"   ❌ 播客生成失败: {result.get('error')}")
                
        else:
            print(f"   ❌ 播客生成请求失败: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   ❌ 播客生成异常: {e}")
    
    # 4. 检查会话状态
    print(f"\n📊 4. 检查最终会话状态...")
    try:
        response = requests.get(f"{BASE_URL}/api/interview/session/{session_id}")
        if response.status_code == 200:
            result = response.json()
            print(f"   📚 书籍: 《{result.get('book_title')}》")
            print(f"   ❓ 已问问题: {result.get('questions_asked')}/{result.get('total_questions')}")
            print(f"   ✅ 访谈完成: {result.get('is_completed')}")
            print(f"   🎙️ 播客生成: {result.get('podcast_generated')}")
            print(f"   💬 对话历史: {len(result.get('conversation_history', []))} 条")
        else:
            print(f"   ❌ 获取会话状态失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 获取会话状态异常: {e}")
    
    print(f"\n🎉 双AI协作访谈系统测试完成!")

if __name__ == "__main__":
    asyncio.run(test_dual_ai_interview())
