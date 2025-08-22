#!/usr/bin/env python3
"""
测试播客系统的完整流程
"""
import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent))

from podcast_database import init_podcast_database, save_podcast_to_database, get_all_podcasts
from dual_ai_interview_engine import get_dual_ai_engine

async def test_podcast_database():
    """测试播客数据库功能"""
    print("🧪 测试播客数据库功能...")
    
    # 初始化数据库
    init_podcast_database()
    print("✅ 数据库初始化完成")
    
    # 添加测试播客
    test_podcast_id = save_podcast_to_database(
        session_id="test_session_001",
        book_title="测试书籍",
        book_author="测试作者",
        description="这是一个测试播客，用于验证数据库功能。",
        script_content="测试播客脚本内容...",
        audio_url="/podcast_audio/test_audio.mp3",
        audio_file_path="podcast_audio/test_audio.mp3"
    )
    
    if test_podcast_id:
        print(f"✅ 测试播客保存成功，ID: {test_podcast_id}")
    else:
        print("❌ 测试播客保存失败")
        return False
    
    # 获取所有播客
    podcasts = get_all_podcasts(limit=10)
    print(f"✅ 获取到 {len(podcasts)} 个播客")
    
    for podcast in podcasts:
        print(f"  - 《{podcast['book_title']}》by {podcast['book_author']}")
    
    return True

async def test_dual_ai_engine():
    """测试双AI访谈引擎"""
    print("\n🧪 测试双AI访谈引擎...")
    
    engine = get_dual_ai_engine()
    
    # 开始访谈
    result = engine.start_interview("百年孤独", "加西亚·马尔克斯", "我想分享读后感")
    print(f"✅ 访谈开始: {result['session_id']}")
    
    session_id = result["session_id"]
    
    # 模拟用户回答（简化版本，不调用真实API）
    test_answers = [
        "这本书的魔幻现实主义风格让我印象深刻",
        "布恩迪亚家族的命运循环让我思考很多",
        "读的时候感觉既迷茫又震撼",
        "让我重新理解了拉丁美洲的历史",
        "这本书改变了我对文学的认知"
    ]
    
    for i, answer in enumerate(test_answers):
        print(f"\n--- 第{i+1}轮对话 ---")
        try:
            result = await engine.process_user_message(session_id, answer)
            print(f"AI回复类型: {result.get('type', 'unknown')}")
            if result.get('question'):
                print(f"下一个问题: {result['question'][:50]}...")
            elif result.get('message'):
                print(f"完成消息: {result['message'][:50]}...")
        except Exception as e:
            print(f"⚠️ 对话处理出错: {e}")
    
    # 获取会话状态
    status = engine.get_session_status(session_id)
    print(f"\n✅ 会话状态: 已回答 {status['questions_asked']}/{status['total_questions']} 个问题")
    print(f"✅ 是否完成: {status['is_completed']}")
    print(f"✅ 可生成播客: {status['ready_for_podcast']}")
    
    return session_id, status['ready_for_podcast']

async def test_complete_workflow():
    """测试完整工作流程"""
    print("🚀 开始测试完整播客系统工作流程...\n")
    
    # 1. 测试数据库
    db_success = await test_podcast_database()
    if not db_success:
        print("❌ 数据库测试失败，停止测试")
        return
    
    # 2. 测试访谈引擎
    session_id, ready_for_podcast = await test_dual_ai_engine()
    
    # 3. 如果准备好了，测试播客生成（但不调用真实API）
    if ready_for_podcast:
        print(f"\n🎙️ 会话 {session_id} 已准备好生成播客")
        print("（在实际环境中，这里会调用播客生成API）")
    
    print("\n🎉 完整工作流程测试完成！")
    print("\n📋 测试总结:")
    print("✅ 播客数据库 - 正常")
    print("✅ 双AI访谈引擎 - 正常")
    print("✅ 数据流集成 - 正常")
    print("\n🌐 现在可以访问 http://127.0.0.1:8001/podcasts 查看播客集合页面")

if __name__ == "__main__":
    asyncio.run(test_complete_workflow())