#!/usr/bin/env python3
"""
简单的TTS测试脚本
测试输入特定文字是否能正确转换为语音
"""

import os
import sys
import time
from pathlib import Path

# 添加create目录到路径
sys.path.append(str(Path(__file__).parent / "create"))

from reliable_voice_generator import WebSocketXunfeiTTS

def test_simple_text():
    """测试简单文本的TTS转换"""
    
    # 测试文本
    test_texts = [
        "一二三四五",              # 5个字符
        "你好世界测试",            # 5个字符
        "这是十个字符测试文本",      # 10个字符
        "简单测试",                # 4个字符
    ]
    
    print("🧪 开始TTS文本转换测试...")
    print("=" * 50)
    
    # 初始化TTS
    tts = WebSocketXunfeiTTS()
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 测试 {i}: '{text}' (长度: {len(text)} 字符)")
        
        output_file = f"test_tts_{i}_{len(text)}chars.wav"
        output_path = Path("ppt_audio") / output_file
        
        print(f"📁 输出文件: {output_path}")
        print(f"🎯 预期内容: {text}")
        
        # 生成语音
        start_time = time.time()
        success = tts.synthesize_to_file(text, str(output_path), timeout=15)
        elapsed = time.time() - start_time
        
        if success and output_path.exists():
            file_size = output_path.stat().st_size
            print(f"✅ 成功生成! 文件大小: {file_size} 字节, 耗时: {elapsed:.2f}s")
            
            # 尝试播放音频进行验证
            print(f"🔊 正在播放音频进行验证...")
            try:
                import subprocess
                # 播放3秒
                subprocess.run(
                    ["afplay", str(output_path)], 
                    timeout=min(10, len(text) * 2)  # 根据文字长度设置播放时间
                )
                print(f"🎵 音频播放完成")
            except Exception as e:
                print(f"⚠️ 播放音频时出错: {e}")
            
            # 手动验证提示
            print(f"❓ 请听音频内容是否为: '{text}'")
            user_input = input("✅ 音频内容正确吗? (y/n): ").strip().lower()
            if user_input == 'y':
                print(f"✅ 测试 {i} 通过!")
            else:
                print(f"❌ 测试 {i} 失败! 音频内容与预期不符")
                actual_content = input("🎧 请输入你听到的实际内容: ").strip()
                print(f"📊 预期: '{text}' vs 实际: '{actual_content}'")
        else:
            print(f"❌ 生成失败! 耗时: {elapsed:.2f}s")
        
        print("-" * 30)

if __name__ == "__main__":
    test_simple_text()
