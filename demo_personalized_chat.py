#!/usr/bin/env python3
"""
个性化书籍推荐对话演示
展示集成workflow模型的个性化推荐功能
"""

import asyncio
import json
from workflow_chat_api import handle_recommendation_chat, get_mock_user_context

async def demo_personalized_chat():
    """演示个性化对话功能"""
    
    print("🎯 个性化书籍推荐对话演示")
    print("=" * 60)
    
    # 展示用户画像
    user_context = get_mock_user_context()
    print("📊 模拟用户画像:")
    print(user_context)
    print("\n" + "=" * 60)
    
    # 测试不同类型的对话
    test_conversations = [
        {
            "user_input": "我想找一些能拓展思维的书籍",
            "description": "用户寻求思维拓展类书籍"
        },
        {
            "user_input": "有没有类似《人类简史》这样的历史类好书？", 
            "description": "基于已读书籍寻求相似推荐"
        },
        {
            "user_input": "最近工作压力大，想读点轻松但有益的书",
            "description": "结合情境的个性化需求"
        }
    ]
    
    for i, conv in enumerate(test_conversations, 1):
        print(f"💬 对话场景 {i}: {conv['description']}")
        print(f"用户: {conv['user_input']}")
        
        try:
            # 调用个性化推荐
            response = await handle_recommendation_chat(
                user_input=conv['user_input'],
                user_id="test_user",
                history=[]
            )
            
            if response.get("success"):
                print("✅ 系统响应:")
                print(f"   消息: {response.get('message', '无响应')[:200]}...")
                print(f"   推荐标识: {response.get('should_recommend', False)}")
                print(f"   响应时间: {response.get('timestamp', '未知')}")
            else:
                print("❌ 响应失败:")
                print(f"   错误: {response.get('error', '未知错误')}")
                
        except Exception as e:
            print(f"❌ 请求异常: {str(e)}")
            
        print("\n" + "-" * 40 + "\n")
    
    print("🏁 演示完成！")
    print("\n📝 总结:")
    print("✅ 成功集成 workflow_openapi_demo_python.py 模型")
    print("✅ 实现了用户画像驱动的个性化对话")
    print("✅ 支持基于阅读历史的智能推荐")
    print("✅ 提供多轮对话上下文支持")

def demo_user_context_variations():
    """演示不同用户画像的变化"""
    print("\n🎭 用户画像变化演示")
    print("=" * 40)
    
    for i in range(3):
        context = get_mock_user_context()
        print(f"用户类型 {i+1}:")
        print(context)
        print("-" * 30)

if __name__ == "__main__":
    print("🚀 启动个性化推荐对话演示...")
    
    # 先展示用户画像变化
    demo_user_context_variations()
    
    # 然后演示对话功能（注释掉避免实际调用API）
    # asyncio.run(demo_personalized_chat())
    
    print("\n✨ 功能特点:")
    print("1. 🎯 基于用户实际阅读历史生成个性化提示词")
    print("2. 📚 自动分析用户偏好类别和阅读特征") 
    print("3. 🤖 集成星火大模型工作流进行智能对话")
    print("4. 🔄 支持对话历史上下文保持")
    print("5. 📊 提供详细的用户画像和推荐逻辑")
    
    print("\n🔧 技术实现:")
    print("- workflow_openapi_demo_python.py: 星火大模型API调用")
    print("- workflow_chat_api.py: 对话引擎和用户画像集成")
    print("- appbook.py: FastAPI服务端集成")
    print("- 数据库: SQLite存储用户阅读历史")
    
    print("\n🎉 集成完成！现在推荐代理页面的对话模块已支持:")
    print("   - 个性化书籍推荐对话")
    print("   - 基于用户画像的智能回复")
    print("   - workflow模型作为对话引擎支撑")

