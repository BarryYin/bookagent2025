#!/usr/bin/env python3
"""
调试截图问题
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "create"))

def debug_screenshot():
    """调试截图功能"""
    print("🔍 调试PPT截图问题")
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
        return
    
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
        
        # 解析HTML内容
        if not generator.parse_html_content():
            print("❌ HTML解析失败")
            return
        
        print(f"📊 应该截取 {len(generator.slides_data)} 页")
        
        # 手动截取每一页
        html_path = Path(html_file).absolute()
        
        for i in range(len(generator.slides_data)):
            print(f"\n📷 手动截取第 {i+1} 页...")
            
            screenshot_path = generator.temp_dir / f"debug_slide_{i+1:03d}.png"
            
            # 尝试两种截图方法
            success1 = generator.take_precise_screenshot(html_path, i, screenshot_path)
            
            if success1:
                size_kb = screenshot_path.stat().st_size / 1024
                print(f"   ✅ 精确截图成功: {size_kb:.1f} KB")
            else:
                print(f"   ❌ 精确截图失败，尝试备用方法...")
                success2 = generator.take_chrome_screenshot(html_path, i, screenshot_path)
                if success2:
                    size_kb = screenshot_path.stat().st_size / 1024
                    print(f"   ✅ 备用截图成功: {size_kb:.1f} KB")
                else:
                    print(f"   ❌ 所有截图方法都失败")
        
        print(f"\n📁 截图保存在: {generator.temp_dir}")
        
        # 检查实际生成的截图数量
        screenshots = list(generator.temp_dir.glob("debug_slide_*.png"))
        print(f"📊 实际生成截图: {len(screenshots)} 张")
        
        for screenshot in screenshots:
            size_kb = screenshot.stat().st_size / 1024
            print(f"   - {screenshot.name}: {size_kb:.1f} KB")
            
    except Exception as e:
        print(f"❌ 调试失败: {e}")

if __name__ == "__main__":
    debug_screenshot()