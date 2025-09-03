#!/usr/bin/env python3
"""
完整视频生成测试
生成一个完整的PPT视频用于测试效果
"""
import sys
import os
from pathlib import Path

# 添加create目录到路径
sys.path.append(str(Path(__file__).parent / "create"))

def test_full_video():
    """测试完整视频生成"""
    print("🎬 完整PPT视频生成测试")
    print("=" * 50)
    
    # 查找测试文件
    outputs_dir = Path("outputs")
    html_files = []
    for session_dir in outputs_dir.iterdir():
        if session_dir.is_dir():
            html_file = session_dir / "presentation.html"
            if html_file.exists():
                html_files.append(html_file)
    
    if not html_files:
        print("❌ 未找到可测试的HTML文件")
        return False
    
    # 选择最新的文件
    html_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    html_file = html_files[0]
    
    print(f"📄 测试文件: {html_file}")
    
    try:
        from universal_ppt_video_generator import UniversalPPTVideoGenerator
        
        # 创建生成器
        generator = UniversalPPTVideoGenerator(
            html_file=str(html_file),
            audio_prefix="slide"
        )
        
        print("🚀 开始生成完整视频...")
        result = generator.generate_video()
        
        if result:
            print(f"\n🎉 视频生成成功！")
            print(f"📁 文件: {result}")
            
            # 获取文件信息
            file_size = result.stat().st_size / (1024 * 1024)  # MB
            print(f"📊 大小: {file_size:.1f} MB")
            
            # 尝试获取视频时长
            try:
                import subprocess
                duration_result = subprocess.run([
                    "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                    "-of", "csv=p=0", str(result)
                ], capture_output=True, text=True)
                if duration_result.returncode == 0:
                    duration = float(duration_result.stdout.strip())
                    print(f"⏱️  时长: {duration:.1f} 秒")
            except:
                pass
            
            # 自动打开视频
            try:
                subprocess.run(["open", str(result)])
                print("📺 视频已自动打开")
            except:
                print("📺 请手动打开视频文件")
            
            return True
        else:
            print("❌ 视频生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        return False

if __name__ == "__main__":
    success = test_full_video()
    if success:
        print("\n✅ 完整视频测试成功！")
    else:
        print("\n❌ 完整视频测试失败")