#!/usr/bin/env python3
"""
测试讯飞语音合成的PPT配音工具
"""

import sys
import os
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    from ppt_voice_generator import PPTVoiceGenerator, XunfeiTTS
    print("✅ 成功导入 PPT 配音工具")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

def test_xunfei_tts():
    """测试讯飞语音合成"""
    print("🧪 测试讯飞语音合成...")
    
    tts = XunfeiTTS()
    test_text = "这是一个测试语音合成的文本。"
    output_file = Path("./test_xunfei.mp3")
    
    success = tts.synthesize_to_file(test_text, str(output_file))
    
    if success and output_file.exists():
        print(f"✅ 讯飞语音合成测试成功，文件保存到: {output_file}")
        print(f"📊 文件大小: {output_file.stat().st_size} 字节")
        return True
    else:
        print("❌ 讯飞语音合成测试失败")
        return False

def test_ppt_generator():
    """测试PPT配音生成器"""
    print("\n🧪 测试PPT配音生成器...")
    
    # 创建测试HTML文件
    test_html = """
    <!DOCTYPE html>
    <html>
    <head><title>测试PPT</title></head>
    <body>
        <div data-speech="欢迎来到第一页测试内容。">第1页</div>
        <div data-speech="这是第二页的测试语音内容。">第2页</div>
    </body>
    </html>
    """
    
    html_file = Path("./test_ppt.html")
    html_file.write_text(test_html, encoding='utf-8')
    
    try:
        generator = PPTVoiceGenerator(str(html_file), "test_slide")
        
        # 提取文本
        speech_texts = generator.extract_speech_texts()
        print(f"📝 提取到 {len(speech_texts)} 页配音文本")
        
        if speech_texts:
            # 生成第一页音频作为测试
            first_slide = speech_texts[0]
            audio_path = generator.generate_audio_for_slide(first_slide)
            
            if audio_path and Path(audio_path).exists():
                print(f"✅ PPT配音生成器测试成功")
                print(f"🎵 生成音频: {audio_path}")
                return True
        
        print("❌ PPT配音生成器测试失败")
        return False
        
    finally:
        # 清理测试文件
        if html_file.exists():
            html_file.unlink()

if __name__ == "__main__":
    print("🎤 讯飞语音PPT配音工具测试")
    print("=" * 50)
    
    # 检查环境变量
    env_vars = ["XUNFEI_APP_ID", "XUNFEI_API_KEY", "XUNFEI_API_SECRET"]
    print("🔧 环境变量检查:")
    for var in env_vars:
        value = os.getenv(var)
        if value:
            masked = value[:8] + "***" if len(value) > 8 else "***"
            print(f"  {var}: {masked}")
        else:
            print(f"  {var}: 使用默认值")
    
    print("\n🧪 开始测试...")
    
    # 测试讯飞TTS
    xunfei_ok = test_xunfei_tts()
    
    # 测试PPT生成器
    ppt_ok = test_ppt_generator()
    
    print("\n📊 测试结果:")
    print(f"  讯飞语音合成: {'✅ 通过' if xunfei_ok else '❌ 失败'}")
    print(f"  PPT配音生成器: {'✅ 通过' if ppt_ok else '❌ 失败'}")
    
    if xunfei_ok and ppt_ok:
        print("\n🎉 所有测试通过！可以使用讯飞语音为PPT配音了。")
    else:
        print("\n⚠️ 部分测试失败，请检查配置和网络连接。")
