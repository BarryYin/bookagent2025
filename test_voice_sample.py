#!/usr/bin/env python3
"""
测试讯飞TTS生成音频样本
"""
import sys
import os
from pathlib import Path

# 添加create目录到路径
sys.path.insert(0, str(Path(__file__).parent / "create"))

def test_voice_samples():
    """生成几个音频样本测试"""
    print("🎵 测试讯飞TTS音频生成")
    print("=" * 50)
    
    try:
        from reliable_voice_generator import WebSocketXunfeiTTS
        
        # 创建TTS实例
        tts = WebSocketXunfeiTTS()
        
        # 测试样本
        samples = [
            ("欢迎使用讯飞语音合成技术，这是一个测试音频。", "sample1_welcome.mp3"),
            ("今天天气很好，适合出门散步。", "sample2_weather.mp3"),
            ("人工智能正在改变我们的生活方式。", "sample3_ai.mp3")
        ]
        
        success_count = 0
        
        for i, (text, filename) in enumerate(samples, 1):
            print(f"\n🎤 生成样本 {i}/3: {filename}")
            print(f"📝 文本: {text}")
            
            success = tts.synthesize_to_file(text, filename)
            
            if success and os.path.exists(filename):
                file_size = os.path.getsize(filename)
                print(f"✅ 生成成功: {file_size} 字节")
                success_count += 1
            else:
                print(f"❌ 生成失败")
        
        print(f"\n📊 测试结果: {success_count}/{len(samples)} 成功")
        
        if success_count > 0:
            print(f"\n🎧 生成的音频文件:")
            for text, filename in samples:
                if os.path.exists(filename):
                    file_size = os.path.getsize(filename)
                    print(f"  🎵 {filename} ({file_size} 字节)")
            
            print(f"\n💡 你可以播放这些文件来测试音质:")
            print(f"   macOS: open sample1_welcome.mp3")
            print(f"   或直接双击文件播放")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_voice_samples()