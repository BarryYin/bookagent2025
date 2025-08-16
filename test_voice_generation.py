#!/usr/bin/env python3
"""
测试语音生成功能
"""
import sys
import asyncio
from pathlib import Path

# 添加create目录到路径
sys.path.append(str(Path(__file__).parent / "create"))

async def test_voice_generation():
    """测试语音生成功能"""
    try:
        from ppt_voice_generator import PPTVoiceGenerator
        
        # 创建一个简单的测试HTML文件
        test_html = """
<!DOCTYPE html>
<html>
<head>
    <title>测试PPT</title>
</head>
<body>
    <div class="slide" data-slide="0" data-speech="你有没有发现，在这个财富差距越来越大的时代，那些懂得理财的人和不懂理财的人之间的差距，正在以一种可怕的速度拉大？">
        <h1>财富认知觉醒</h1>
        <h2>从《小狗钱钱》看理财思维</h2>
    </div>
    
    <div class="slide" data-slide="1" data-speech="答案很残酷：这背后的本质差距，是财商思维的差距。博多·舍费尔在《小狗钱钱》这本书里，用最简单的故事告诉我们一个颠覆性的认知：理财不是有钱人的特权，而是每个人都必须掌握的生存技能。">
        <h1>认知升级</h1>
        <h2>财商思维的重要性</h2>
    </div>
    
    <div class="slide" data-slide="2" data-speech="但是，这本书真正厉害的地方不在于教你具体的理财技巧，而在于它揭示了一个被大多数人忽视的底层逻辑：成功的理财来自于正确的金钱观念和持续的行动力。">
        <h1>底层逻辑</h1>
        <h2>理财成功的真正秘密</h2>
    </div>
</body>
</html>
        """
        
        # 保存测试文件
        test_file = Path("test_voice.html")
        test_file.write_text(test_html, encoding='utf-8')
        
        print("🎵 开始测试语音生成...")
        
        # 初始化语音生成器
        voice_generator = PPTVoiceGenerator(
            html_file=str(test_file),
            audio_prefix="test_slide"
        )
        
        # 测试提取文本
        print("\n📝 测试文本提取...")
        slides = voice_generator.extract_speech_texts()
        if slides:
            print(f"✅ 成功提取 {len(slides)} 页文本:")
            for slide in slides:
                print(f"  第{slide['index']}页: {slide['text'][:50]}...")
        else:
            print("❌ 未能提取到文本")
            return False
        
        # 测试语音生成（只生成第一页以节省时间）
        print("\n🎙️ 测试语音生成...")
        if slides:
            first_slide = slides[0]
            audio_path = voice_generator.generate_audio_for_slide(first_slide, use_fish_audio=True)
            if audio_path:
                print(f"✅ 语音生成成功: {audio_path}")
                # 检查文件大小
                audio_file = Path(audio_path)
                if audio_file.exists():
                    size = audio_file.stat().st_size
                    print(f"📊 音频文件大小: {size} 字节")
                    if size > 1000:  # 如果文件大于1KB，认为生成成功
                        print("✅ 语音功能正常工作!")
                        return True
                    else:
                        print("⚠️ 音频文件过小，可能生成失败")
                else:
                    print("❌ 音频文件不存在")
            else:
                print("❌ 语音生成失败")
        
        return False
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保安装了必要的依赖包")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    finally:
        # 清理测试文件
        test_file = Path("test_voice.html")
        if test_file.exists():
            test_file.unlink()
            print("🧹 清理测试文件")

async def main():
    """主函数"""
    print("=" * 60)
    print("🔊 语音生成功能测试")
    print("=" * 60)
    
    success = await test_voice_generation()
    
    if success:
        print("\n🎉 语音功能测试通过!")
        print("📝 建议：")
        print("  1. 确保Fish Audio API密钥正确配置")
        print("  2. 检查网络连接")
        print("  3. 在生成PPT时选择启用语音功能")
    else:
        print("\n❌ 语音功能测试失败")
        print("📝 可能的解决方案：")
        print("  1. 检查Fish Audio SDK是否正确安装: pip install fish-audio-sdk")
        print("  2. 检查API密钥是否有效")
        print("  3. 检查系统是否支持macOS的say命令")
        print("  4. 查看详细错误信息进行调试")

if __name__ == "__main__":
    asyncio.run(main())
