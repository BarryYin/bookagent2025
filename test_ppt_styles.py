#!/usr/bin/env python3
"""
测试三种PPT风格生成
"""
import asyncio
import json
from appbook import generate_reliable_ppt_html_internal

# 测试数据
test_slides = [
    {"title": "小王子", "content": "欢迎来到《小王子》的精彩解读"},
    {"title": "作者介绍", "content": "安东尼·德·圣-埃克苏佩里，法国作家和飞行员"},
    {"title": "核心主题", "content": ["成长与纯真", "友谊与爱情", "责任与担当"]},
    {"title": "经典语录", "content": "真正重要的东西，用眼睛是看不见的"},
    {"title": "现实意义", "content": "在成人世界中保持童心的重要性"}
]

test_narrations = [
    "欢迎大家，今天我们来分享《小王子》这部经典作品",
    "让我们先了解一下这位传奇作家的人生经历",
    "这本书探讨了许多深刻的人生主题",
    "书中有许多令人难忘的经典语句",
    "最后让我们思考这本书对现代人的启发意义"
]

test_book_data = {
    "title": "小王子",
    "author": "安东尼·德·圣-埃克苏佩里",
    "cover_url": "default_cover"
}

def test_style(style_name, video_style):
    """测试单个风格"""
    print(f"\n=== 测试 {style_name} 风格 ===")
    
    try:
        html_content = generate_reliable_ppt_html_internal(
            test_slides, 
            test_narrations, 
            test_book_data, 
            "小王子",
            video_style
        )
        
        # 保存HTML文件
        filename = f"test_ppt_{video_style}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ {style_name} 风格生成成功")
        print(f"📁 文件保存为: {filename}")
        print(f"📏 HTML长度: {len(html_content)} 字符")
        
        # 检查关键样式特征
        if video_style == "storytelling" and "#FF9800" in html_content:
            print("🎨 检测到故事风格的橙色主题")
        elif video_style == "modern_presentation" and "#2196F3" in html_content:
            print("🎨 检测到现代风格的蓝色主题")
        elif video_style == "classic_ppt" and "#1565C0" in html_content:
            print("🎨 检测到经典风格的商务蓝色")
            
    except Exception as e:
        print(f"❌ {style_name} 风格生成失败: {e}")

def main():
    """主测试函数"""
    print("🚀 开始测试三种PPT风格生成...")
    
    # 测试三种风格
    styles = [
        ("经典商务", "classic_ppt"),
        ("故事叙述", "storytelling"), 
        ("现代演示", "modern_presentation")
    ]
    
    for style_name, video_style in styles:
        test_style(style_name, video_style)
    
    print(f"\n🎉 测试完成！生成了 {len(styles)} 个不同风格的PPT文件")
    print("💡 你可以在浏览器中打开这些HTML文件查看效果")

if __name__ == "__main__":
    main()