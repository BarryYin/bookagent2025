#!/usr/bin/env python3
"""
测试workflow模型集成
验证新的对话API是否正常工作
"""

import asyncio
import json
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_workflow_chat():
    """测试workflow对话功能"""
    print("🚀 开始测试workflow对话集成...")
    
    try:
        from workflow_chat_api import WorkflowChatEngine, handle_recommendation_chat
        
        # 测试基本连接
        engine = WorkflowChatEngine()
        print("✅ Workflow引擎初始化成功")
        
        # 测试简单对话
        print("\n📝 测试1: 基本对话")
        response = await engine.send_message("你好，我是一个读书爱好者")
        print(f"响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
        
        # 测试推荐相关对话
        print("\n📚 测试2: 书籍推荐对话")
        rec_response = await handle_recommendation_chat(
            user_input="能帮我推荐几本科幻小说吗？",
            user_id="test_user_123"
        )
        print(f"推荐响应: {json.dumps(rec_response, ensure_ascii=False, indent=2)}")
        
        # 测试带历史的对话
        print("\n💬 测试3: 带历史的对话")
        history = [
            {"role": "user", "content": "我喜欢科幻小说"},
            {"role": "assistant", "content": "很好，科幻小说有很多经典作品"}
        ]
        
        context_response = await handle_recommendation_chat(
            user_input="能推荐一些比较新的科幻作品吗？",
            user_id="test_user_123",
            history=history
        )
        print(f"上下文响应: {json.dumps(context_response, ensure_ascii=False, indent=2)}")
        
        print("\n✅ 所有测试完成！")
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保workflow_chat_api.py文件存在并且语法正确")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

async def test_api_integration():
    """测试API集成"""
    print("\n🔌 测试API集成...")
    
    try:
        # 模拟API请求数据
        mock_request_data = {
            "message": "推荐几本好书给我",
            "history": [
                {"role": "user", "content": "你好"},
                {"role": "assistant", "content": "你好！我是你的阅读顾问"}
            ]
        }
        
        from workflow_chat_api import handle_recommendation_chat
        
        response = await handle_recommendation_chat(
            user_input=mock_request_data["message"],
            user_id="api_test_user",
            history=mock_request_data["history"]
        )
        
        print(f"API集成测试响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
        
        # 验证响应格式
        required_fields = ["success", "message", "timestamp"]
        for field in required_fields:
            if field not in response:
                print(f"⚠️ 警告: 响应中缺少字段 '{field}'")
            else:
                print(f"✅ 字段 '{field}' 存在")
                
    except Exception as e:
        print(f"❌ API集成测试失败: {e}")

if __name__ == "__main__":
    print("🎯 Workflow集成测试开始")
    print("=" * 50)
    
    # 运行测试
    asyncio.run(test_workflow_chat())
    asyncio.run(test_api_integration())
    
    print("\n" + "=" * 50)
    print("🏁 测试完成")


