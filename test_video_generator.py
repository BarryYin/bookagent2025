#!/usr/bin/env python3
"""
视频生成器测试工具
快速测试PPT视频生成效果
"""
import sys
import os
from pathlib import Path

# 添加create目录到路径
sys.path.append(str(Path(__file__).parent / "create"))

def find_test_html():
    """查找可用的测试HTML文件"""
    outputs_dir = Path("outputs")
    if not outputs_dir.exists():
        print("❌ outputs目录不存在")
        return None
    
    # 查找最新的HTML文件
    html_files = []
    for session_dir in outputs_dir.iterdir():
        if session_dir.is_dir():
            html_file = session_dir / "presentation.html"
            if html_file.exists():
                html_files.append(html_file)
    
    if not html_files:
        print("❌ 未找到可测试的HTML文件")
        return None
    
    # 按修改时间排序，选择最新的
    html_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return html_files[0]

def test_video_generation():
    """测试视频生成"""
    print("🧪 PPT视频生成测试工具")
    print("=" * 50)
    
    # 查找测试文件
    html_file = find_test_html()
    if not html_file:
        return False
    
    print(f"📄 找到测试文件: {html_file}")
    
    try:
        # 导入视频生成器
        from universal_ppt_video_generator import UniversalPPTVideoGenerator
        
        # 创建生成器实例
        generator = UniversalPPTVideoGenerator(
            html_file=str(html_file),
            audio_prefix="slide"
        )
        
        # 检查依赖
        print("\n🔍 检查系统依赖...")
        if not generator.check_dependencies():
            print("❌ 系统依赖检查失败")
            return False
        
        # 解析HTML内容
        print("\n📄 解析HTML内容...")
        if not generator.parse_html_content():
            print("❌ HTML解析失败")
            return False
        
        print(f"✅ 发现 {len(generator.slides_data)} 页幻灯片")
        
        # 测试截图功能（截取所有页面）
        print("\n📸 测试截图功能...")
        test_slides = generator.slides_data  # 测试所有页面
        
        for i, slide_data in enumerate(test_slides):
            print(f"📷 测试截图第 {i+1} 页...")
            
            screenshot_path = generator.temp_dir / f"test_slide_{i+1:03d}.png"
            
            # 测试精确截图
            success = generator.take_precise_screenshot(html_file, i, screenshot_path)
            
            if success:
                print(f"   ✅ 截图成功: {screenshot_path}")
                # 检查文件大小
                size_kb = screenshot_path.stat().st_size / 1024
                print(f"   📊 文件大小: {size_kb:.1f} KB")
            else:
                print(f"   ❌ 截图失败")
                return False
        
        print("\n🎉 测试完成！")
        print(f"📁 截图文件保存在: {generator.temp_dir}")
        
        # 打开截图目录
        try:
            import subprocess
            subprocess.run(["open", str(generator.temp_dir)])
            print("📂 已自动打开截图目录")
        except:
            print("📂 请手动查看截图目录")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_video_generation()
    if success:
        print("\n✅ 测试成功！可以查看截图效果")
    else:
        print("\n❌ 测试失败")