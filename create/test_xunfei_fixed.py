#!/usr/bin/env python3
"""
测试修复后的讯飞TTS功能
"""

import sys
import os
from pathlib import Path
sys.path.append('/Users/mac/Documents/GitHub/bookagent/create')

from ppt_voice_generator import XunfeiTTS

def test_xunfei_fixed():
    print("=== 测试修复后的讯飞TTS ===")
    
    # 创建XunfeiTTS实例
    xunfei = XunfeiTTS()
    print(f"App ID: {xunfei.app_id}")
    print(f"API Key: {xunfei.api_key[:10]}...")
    print(f"API Secret: {xunfei.api_secret[:10]}...")
    
    # 测试文本
    test_text = "这是一个修复后的讯飞语音合成测试。"
    output_file = "/Users/mac/Documents/GitHub/bookagent/create/test_fixed_xunfei.mp3"
    
    print(f"测试文本: {test_text}")
    print(f"输出文件: {output_file}")
    
    try:
        # 测试语音合成
        print("正在调用讯飞API生成语音...")
        
        # 先测试创建任务
        create_result = xunfei.create_task(test_text)
        print(f"创建任务结果: {create_result}")
        
        if not create_result:
            print("❌ 创建任务失败")
            return False
            
        success = xunfei.synthesize_to_file(test_text, output_file)
        
        if success and os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"✅ 讯飞语音合成成功！")
            print(f"   文件大小: {file_size} bytes")
            print(f"   输出文件: {output_file}")
            return True
        else:
            print("❌ 讯飞语音合成失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_xunfei_fixed()
    
    if success:
        print("\n🎉 讯飞TTS修复成功！现在可以正常使用了。")
    else:
        print("\n❌ 讯飞TTS仍有问题，请检查API凭证或网络连接。")
