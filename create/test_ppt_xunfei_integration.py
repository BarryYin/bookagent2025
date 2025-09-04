#!/usr/bin/env python3
"""
测试讯飞TTS在PPT语音生成中是否正常工作
"""

import sys
import os
from pathlib import Path
sys.path.append('/Users/mac/Documents/GitHub/bookagent/create')

from ppt_voice_generator import XunfeiTTS, PPTVoiceGenerator

def test_xunfei_in_ppt_context():
    print("=== 测试讯飞TTS在PPT语音生成中的表现 ===")
    
    # 创建测试文本
    test_text = "这是一个PPT语音生成测试，验证讯飞API是否能正常工作。"
    output_file = "/Users/mac/Documents/GitHub/bookagent/create/test_ppt_xunfei.mp3"
    
    # 测试讯飞TTS类
    print("1. 测试XunfeiTTS类...")
    xunfei = XunfeiTTS()
    print(f"   App ID: {xunfei.app_id}")
    print(f"   API Key: {xunfei.api_key[:10]}...")
    print(f"   API Secret: {xunfei.api_secret[:10]}...")
    
    # 测试语音生成
    print("2. 测试语音生成...")
    try:
        success = generate_audio_for_text(test_text, output_file, voice_engine="xunfei")
        if success and os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"✅ 语音生成成功！文件大小: {file_size} bytes")
            print(f"   输出文件: {output_file}")
            return True
        else:
            print("❌ 语音生成失败")
            return False
    except Exception as e:
        print(f"❌ 语音生成出错: {e}")
        return False

def test_fallback_mechanism():
    print("\n=== 测试语音生成回退机制 ===")
    
    test_text = "测试回退机制是否正常工作。"
    output_file = "/Users/mac/Documents/GitHub/bookagent/create/test_fallback.mp3"
    
    try:
        # 测试自动选择最佳语音引擎
        success = generate_audio_for_text(test_text, output_file)
        if success and os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"✅ 回退机制正常！文件大小: {file_size} bytes")
            return True
        else:
            print("❌ 回退机制失败")
            return False
    except Exception as e:
        print(f"❌ 回退机制出错: {e}")
        return False

if __name__ == "__main__":
    xunfei_success = test_xunfei_in_ppt_context()
    fallback_success = test_fallback_mechanism()
    
    print("\n=== 测试结果 ===")
    print(f"讯飞TTS: {'✅ 成功' if xunfei_success else '❌ 失败'}")
    print(f"回退机制: {'✅ 成功' if fallback_success else '❌ 失败'}")
    
    if xunfei_success:
        print("\n🎉 讯飞API现在可以正常工作了！")
    else:
        print("\n⚠️ 讯飞API仍有问题，但回退机制应该能保证语音生成正常工作")
