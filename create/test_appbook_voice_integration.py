#!/usr/bin/env python3
"""
测试 appbook.py 中的可靠语音生成功能
"""

import sys
import os
from pathlib import Path

# 添加路径
sys.path.append('/Users/mac/Documents/GitHub/bookagent')
sys.path.append('/Users/mac/Documents/GitHub/bookagent/create')

def test_appbook_voice_integration():
    """测试 appbook.py 中的语音生成集成"""
    print("=== 测试 appbook.py 语音生成集成 ===")
    
    try:
        # 导入可靠的语音生成器
        from reliable_voice_generator import ReliableVoiceGenerator
        
        print("✅ 成功导入 ReliableVoiceGenerator")
        
        # 创建测试HTML文件
        test_html = '''<!DOCTYPE html>
<html>
<head><title>测试PPT</title></head>
<body>
    <div data-speech="欢迎来到我们的测试演示">幻灯片1</div>
    <div data-speech="这是第二张幻灯片的内容">幻灯片2</div>
    <div data-speech="让我们来看看效果如何">幻灯片3</div>
</body>
</html>'''
        
        # 保存测试文件
        test_file = Path("/Users/mac/Documents/GitHub/bookagent/test_appbook_voice.html")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_html)
        
        print(f"✅ 创建测试HTML文件: {test_file}")
        
        # 初始化语音生成器
        voice_generator = ReliableVoiceGenerator(
            html_file=str(test_file),
            audio_prefix="appbook_test_slide"
        )
        
        print("✅ 成功初始化 ReliableVoiceGenerator")
        
        # 生成语音
        print("🎤 开始生成语音...")
        voice_results = voice_generator.generate_all_audio()
        
        if voice_results:
            print(f"✅ 语音生成成功: {len(voice_results)} 个音频文件")
            
            # 创建播放列表
            playlist = voice_generator.create_playlist(voice_results)
            if playlist:
                print(f"✅ 播放列表创建成功: {playlist}")
            
            # 检查生成的文件
            for result in voice_results:
                audio_file = Path(result['audio_file'])
                if audio_file.exists():
                    size = audio_file.stat().st_size
                    print(f"  📁 {audio_file.name}: {size} bytes")
                else:
                    print(f"  ❌ 文件不存在: {audio_file}")
            
            return True
        else:
            print("❌ 语音生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理测试文件
        if 'test_file' in locals() and test_file.exists():
            test_file.unlink()

def test_import_compatibility():
    """测试导入兼容性"""
    print("\n=== 测试导入兼容性 ===")
    
    try:
        # 测试所有必要的导入
        from reliable_voice_generator import ReliableVoiceGenerator
        print("✅ ReliableVoiceGenerator 导入成功")
        
        from reliable_voice_generator import WebSocketXunfeiTTS
        print("✅ WebSocketXunfeiTTS 导入成功")
        
        from reliable_voice_generator import SystemTTS
        print("✅ SystemTTS 导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试 appbook.py 语音生成集成...\n")
    
    import_success = test_import_compatibility()
    integration_success = test_appbook_voice_integration()
    
    print("\n=== 测试结果 ===")
    print(f"导入兼容性: {'✅ 通过' if import_success else '❌ 失败'}")
    print(f"集成测试: {'✅ 通过' if integration_success else '❌ 失败'}")
    
    if import_success and integration_success:
        print("\n🎉 appbook.py 语音生成集成测试完全成功！")
        print("现在可以在 appbook.py 中使用可靠的语音生成功能了。")
    else:
        print("\n❌ 测试失败，需要检查配置。")
