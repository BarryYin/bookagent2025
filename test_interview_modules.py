#!/usr/bin/env python3
"""
测试访谈功能的简单脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_interview_modules():
    """测试访谈模块导入"""
    try:
        print("正在测试访谈模块...")
        
        # 测试用户模型模块
        from interview_user_model import UserReadingProfile, InterviewSession, create_new_session
        print("✅ interview_user_model 模块导入成功")
        
        # 测试对话模块
        from interview_dialogue import get_dialogue_engine
        print("✅ interview_dialogue 模块导入成功")
        
        # 测试内容处理模块
        from interview_content_processor import get_podcast_generator
        print("✅ interview_content_processor 模块导入成功")
        
        # 测试音频生成模块
        from podcast_audio_generator import get_podcast_audio_generator
        print("✅ podcast_audio_generator 模块导入成功")
        
        # 创建一个测试会话
        session = create_new_session("我是一个大学生，刚读完三体", "三体", "刘慈欣")
        print(f"✅ 创建测试会话成功: {session.session_id}")
        print(f"   用户画像: {session.user_profile.age_group}, {session.user_profile.profession}")
        print(f"   当前阶段: {session.current_stage}")
        
        # 测试对话引擎
        engine = get_dialogue_engine()
        print("✅ 对话引擎初始化成功")
        
        print("\n🎉 所有访谈功能模块测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_interview_modules()
    sys.exit(0 if success else 1)