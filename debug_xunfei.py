#!/usr/bin/env python3
"""
调试讯飞语音合成问题
"""

import os
import sys
import json
from pathlib import Path

# 添加create目录到路径
sys.path.insert(0, str(Path(__file__).parent / "create"))

from ppt_voice_generator import XunfeiTTS

def debug_xunfei():
    """详细调试讯飞语音合成"""
    print("🔍 讯飞语音合成详细调试")
    print("=" * 50)
    
    # 打印配置信息
    tts = XunfeiTTS()
    print(f"🏷️  APP_ID: {tts.app_id}")
    print(f"🔑 API_KEY: {tts.api_key[:8]}***")
    print(f"🔐 API_SECRET: {tts.api_secret[:8]}***")
    print(f"🌐 HOST: {tts.host}")
    
    # 测试创建任务
    test_text = "这是一个测试。"
    print(f"\n📝 测试文本: {test_text}")
    
    try:
        print("\n🚀 创建语音合成任务...")
        result = tts.create_task(test_text)
        print(f"📊 创建任务结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result:
            header = result.get('header', {})
            code = header.get('code')
            message = header.get('message')
            task_id = header.get('task_id')
            
            print(f"\n📋 任务状态:")
            print(f"  ✓ 返回码: {code}")
            print(f"  ✓ 消息: {message}")
            print(f"  ✓ 任务ID: {task_id}")
            
            if code == 0 and task_id:
                print(f"\n🔄 查询任务状态...")
                query_result = tts.query_task(task_id)
                print(f"📊 查询结果: {json.dumps(query_result, indent=2, ensure_ascii=False)}")
            else:
                print(f"❌ 任务创建失败，错误码: {code}, 消息: {message}")
        else:
            print("❌ 任务创建返回空结果")
            
    except Exception as e:
        print(f"❌ 发生异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_xunfei()
