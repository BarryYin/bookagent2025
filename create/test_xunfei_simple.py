#!/usr/bin/env python3
"""
简单测试讯飞TTS API是否能正常工作
"""

import sys
import os
from pathlib import Path
sys.path.append('/Users/mac/Documents/GitHub/bookagent/create')

from ppt_voice_generator import XunfeiTTS

def test_xunfei_direct():
    print("=== 直接测试讯飞TTS类 ===")
    
    # 创建XunfeiTTS实例
    xunfei = XunfeiTTS()
    print(f"App ID: {xunfei.app_id}")
    print(f"API Key: {xunfei.api_key[:10]}...")
    print(f"API Secret: {xunfei.api_secret[:10]}...")
    
    # 测试文本
    test_text = "这是一个讯飞语音合成测试。"
    
    try:
        # 测试语音合成
        print("正在生成语音...")
        result = xunfei.post_to_xunfei(test_text)
        
        if result and 'task_id' in result:
            print(f"✅ 任务创建成功，Task ID: {result['task_id']}")
            return True
        else:
            print(f"❌ 任务创建失败: {result}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_xunfei_synthesis():
    print("\n=== 测试完整的语音合成流程 ===")
    
    # 创建测试HTML内容
    test_html = '''
    <div data-speech="欢迎来到我们的演示">幻灯片1</div>
    <div data-speech="这是第二张幻灯片的内容">幻灯片2</div>
    '''
    
    # 保存到临时文件
    html_file = "/Users/mac/Documents/GitHub/bookagent/create/test_temp.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(f'''<!DOCTYPE html>
<html>
<head><title>测试</title></head>
<body>{test_html}</body>
</html>''')
    
    try:
        # 使用PPTVoiceGenerator测试
        generator = PPTVoiceGenerator(html_file, "test_audio")
        print(f"HTML文件: {generator.html_file}")
        print(f"音频前缀: {generator.audio_prefix}")
        
        # 提取幻灯片数据
        slides = generator.extract_slides()
        print(f"提取到 {len(slides)} 张幻灯片")
        
        if slides:
            # 测试生成第一张幻灯片的音频
            first_slide = slides[0]
            print(f"测试生成音频: {first_slide['text']}")
            
            audio_file = generator.generate_audio_for_slide(first_slide)
            if audio_file and os.path.exists(audio_file):
                file_size = os.path.getsize(audio_file)
                print(f"✅ 音频生成成功: {audio_file} ({file_size} bytes)")
                return True
            else:
                print("❌ 音频生成失败")
                return False
        else:
            print("❌ 没有提取到幻灯片内容")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    finally:
        # 清理临时文件
        if os.path.exists(html_file):
            os.remove(html_file)

if __name__ == "__main__":
    print("开始测试讯飞语音合成...")
    
    direct_success = test_xunfei_direct()
    synthesis_success = test_xunfei_synthesis()
    
    print("\n=== 测试结果 ===")
    print(f"直接API测试: {'✅ 成功' if direct_success else '❌ 失败'}")
    print(f"语音合成测试: {'✅ 成功' if synthesis_success else '❌ 失败'}")
    
    if direct_success and synthesis_success:
        print("\n🎉 讯飞语音合成完全正常！")
    elif direct_success:
        print("\n⚠️ 讯飞API可用，但集成有问题")
    else:
        print("\n❌ 讯飞API不可用")
