#!/usr/bin/env python3
"""
修复讯飞语音合成问题 - 禁用讯飞API，直接使用备用方案
"""

import sys
import os
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

def patch_xunfei_tts():
    """修补讯飞TTS类，直接返回失败以使用备用方案"""
    
    ppt_voice_file = Path(__file__).parent / "ppt_voice_generator.py"
    
    if not ppt_voice_file.exists():
        print(f"❌ 文件不存在: {ppt_voice_file}")
        return False
    
    # 读取原文件
    with open(ppt_voice_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经修补过
    if "# PATCHED: 讯飞API配额不足，直接跳过" in content:
        print("✅ 已经修补过讯飞TTS，无需重复修补")
        return True
    
    # 查找讯飞TTS的synthesize_to_file方法
    old_method = '''    def synthesize_to_file(self, text, output_file, voice="x4_xiaoguo", max_retries=10):
        """合成语音并保存到文件"""
        # 创建任务
        create_result = self.create_task(text, voice)
        if not create_result or create_result.get('header', {}).get('code') != 0:
            return False'''
    
    # 新的方法实现
    new_method = '''    def synthesize_to_file(self, text, output_file, voice="x4_xiaoguo", max_retries=10):
        """合成语音并保存到文件"""
        # PATCHED: 讯飞API配额不足，直接跳过
        print("⚠️ 讯飞API配额不足，跳过讯飞语音合成")
        return False'''
    
    # 替换方法
    if old_method in content:
        content = content.replace(old_method, new_method)
        
        # 写入修补后的文件
        with open(ppt_voice_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 成功修补讯飞TTS，现在将直接使用Fish Audio或系统语音")
        return True
    else:
        print("❌ 未找到需要修补的方法")
        return False

def test_patched_system():
    """测试修补后的系统"""
    print("\n🧪 测试修补后的系统...")
    
    try:
        from ppt_voice_generator import PPTVoiceGenerator
        
        # 创建测试HTML文件
        test_html = """<!DOCTYPE html>
<html>
<head><title>测试PPT</title></head>
<body>
    <div data-speech="这是修补后的语音合成测试。">第1页</div>
</body>
</html>"""
        
        html_file = Path("./test_patched.html")
        html_file.write_text(test_html, encoding='utf-8')
        
        try:
            generator = PPTVoiceGenerator(str(html_file), "test_patched")
            
            # 提取文本
            speech_texts = generator.extract_speech_texts()
            print(f"📝 提取到 {len(speech_texts)} 页配音文本")
            
            if speech_texts:
                # 生成第一页音频作为测试
                first_slide = speech_texts[0]
                audio_path = generator.generate_audio_for_slide(first_slide)
                
                if audio_path and Path(audio_path).exists():
                    print(f"✅ 修补后的系统测试成功")
                    print(f"🎵 生成音频: {audio_path}")
                    return True
            
            print("❌ 修补后的系统测试失败")
            return False
            
        finally:
            # 清理测试文件
            if html_file.exists():
                html_file.unlink()
                
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

if __name__ == "__main__":
    print("🔧 修复讯飞语音合成问题")
    print("=" * 50)
    
    # 修补讯飞TTS
    patch_success = patch_xunfei_tts()
    
    if patch_success:
        # 测试修补后的系统
        test_success = test_patched_system()
        
        if test_success:
            print("\n🎉 修复完成！现在语音合成将使用Fish Audio或系统语音")
            print("💡 建议: 请联系讯飞更新API配额或使用新的API密钥")
        else:
            print("\n⚠️ 修补成功但测试失败，请检查Fish Audio或系统语音配置")
    else:
        print("\n❌ 修补失败，请手动检查代码")
