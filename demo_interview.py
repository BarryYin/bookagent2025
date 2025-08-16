#!/usr/bin/env python3
"""
简单的访谈功能演示脚本
不需要Web界面，直接测试核心功能
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from interview_user_model import create_new_session
from interview_dialogue import get_dialogue_engine
from interview_content_processor import get_podcast_generator

async def demo_interview():
    """演示访谈功能"""
    print("🎙️ 读后感访谈智能体演示")
    print("=" * 50)
    
    # 创建访谈会话
    book_title = "三体"
    book_author = "刘慈欣"
    user_intro = "我是一个大学生，刚读完三体，感觉非常震撼"
    
    print(f"📚 书籍：《{book_title}》 - {book_author}")
    print(f"👤 用户：{user_intro}")
    print()
    
    # 开始访谈
    engine = get_dialogue_engine()
    result = engine.start_interview(book_title, book_author, user_intro)
    
    session_id = result["session_id"]
    opening_message = result["opening_message"]
    user_profile = result["user_profile"]
    
    print(f"🆔 会话ID：{session_id}")
    print(f"🎭 用户画像：{user_profile['age_group']} - {user_profile['profession']}")
    print(f"🎯 当前阶段：{result['stage']}")
    print()
    print("🤖 AI助手：", opening_message)
    print()
    
    # 模拟几轮对话
    test_messages = [
        "我觉得三体中的黑暗森林法则很有意思，让我对宇宙有了新的认识",
        "叶文洁的选择虽然可以理解，但我认为她太极端了",
        "如果我是罗辑，我可能会做出不同的选择",
        "这本书让我思考了很多关于人性和文明的问题",
        "我觉得最震撼的是三体人的思维透明概念",
        "现在想想，我们地球文明也很幸运"
    ]
    
    print("🔄 开始模拟对话...")
    print("-" * 30)
    
    for i, message in enumerate(test_messages):
        print(f"👤 用户第{i+1}轮：{message}")
        
        # 处理用户消息
        response = await engine.process_user_message(session_id, message)
        
        print(f"🤖 AI回复：{response['response']}")
        print(f"📊 当前阶段：{response['stage']}")
        print()
        
        # 等待一秒模拟真实对话
        await asyncio.sleep(0.5)
    
    print("🎙️ 对话完成，开始生成播客...")
    print("-" * 30)
    
    # 生成播客
    generator = get_podcast_generator()
    try:
        podcast_result = await generator.generate_podcast_content(session_id)
        
        print("✅ 播客生成成功！")
        print(f"📋 播客标题：{podcast_result['podcast_structure']['title']}")
        print(f"📝 播客副标题：{podcast_result['podcast_structure']['subtitle']}")
        print(f"⏱️ 总时长：{podcast_result['podcast_structure']['total_duration']}秒")
        print(f"🎯 目标听众：{podcast_result['podcast_structure']['target_audience']}")
        print(f"🏷️ 关键主题：{', '.join(podcast_result['podcast_structure']['key_themes'])}")
        print()
        
        # 显示播客脚本片段
        script = podcast_result['podcast_script']
        lines = script.split('\n')
        print("📜 播客脚本预览：")
        for i, line in enumerate(lines[:10]):
            print(f"  {line}")
        if len(lines) > 10:
            print(f"  ... (共{len(lines)}行)")
        
        print()
        print("🎵 音频生成：")
        if podcast_result['audio_generation'].get('merged_audio'):
            print(f"  ✅ 合并音频：{podcast_result['audio_generation']['merged_audio']}")
            print(f"  ⏱️ 音频时长：{podcast_result['audio_generation']['total_duration']}秒")
        else:
            print("  ⚠️ 音频生成失败或未配置")
        
    except Exception as e:
        print(f"❌ 播客生成失败：{e}")
    
    print()
    print("🎉 演示完成！")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(demo_interview())