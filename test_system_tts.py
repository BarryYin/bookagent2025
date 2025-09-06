#!/usr/bin/env python3
"""
系统TTS测试脚本
测试系统语音是否能正确转换
"""

import os
import sys
import time
from pathlib import Path

# 添加create目录到路径
sys.path.append(str(Path(__file__).parent / "create"))

from reliable_voice_generator import SystemTTS

def test_system_tts():
    """测试系统TTS"""
    
    test_texts = [
        "一二三四五",
        "你好世界测试",
        "这是十个字符测试文本",
        "简单测试",
    ]
    
    print("🧪 开始系统TTS测试...")
    print("=" * 50)
    
    # 初始化系统TTS
    system_tts = SystemTTS()
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 测试 {i}: '{text}' (长度: {len(text)} 字符)")
        
        output_file = f"test_system_tts_{i}_{len(text)}chars.mp3"
        output_path = Path("ppt_audio") / output_file
        
        print(f"📁 输出文件: {output_path}")
        print(f"🎯 预期内容: {text}")
        
        # 生成语音
        start_time = time.time()
        success = system_tts.synthesize_to_file(text, str(output_path), timeout=20)
        elapsed = time.time() - start_time
        
        if success and output_path.exists():
            file_size = output_path.stat().st_size
            print(f"✅ 成功生成! 文件大小: {file_size} 字节, 耗时: {elapsed:.2f}s")
            
            # 尝试播放音频进行验证
            print(f"🔊 正在播放音频进行验证...")
            try:
                import subprocess
                # 播放音频
                subprocess.run(
                    ["afplay", str(output_path)], 
                    timeout=min(15, len(text) * 3)
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
    test_system_tts()
