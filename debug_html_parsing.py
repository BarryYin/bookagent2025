#!/usr/bin/env python3
"""
调试HTML解析问题 - 检查从HTML中提取的实际文本
"""

import os
import re
from pathlib import Path

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

def debug_html_parsing(html_file):
    """调试HTML解析，显示实际提取的文本"""
    if not os.path.exists(html_file):
        print(f"❌ HTML文件不存在: {html_file}")
        return
    
    print(f"🔍 调试HTML文件: {html_file}")
    print(f"📚 BeautifulSoup可用: {BS4_AVAILABLE}")
    print()
    
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📄 文件大小: {len(content)} 字符")
        
        # 检查文件编码
        print(f"🔤 文件前100字符: {repr(content[:100])}")
        print()
        
        slides = []
        if BS4_AVAILABLE:
            print("🔧 使用BeautifulSoup解析...")
            soup = BeautifulSoup(content, 'html.parser')
            elements = soup.find_all(attrs={'data-speech': True})
            
            print(f"📊 找到 {len(elements)} 个data-speech元素")
            
            for i, element in enumerate(elements):
                text = element.get('data-speech', '').strip()
                if text:
                    slides.append({
                        'index': i + 1,
                        'text': text
                    })
                    print(f"  [{i+1}] 长度:{len(text)} - {text[:50]}...")
        else:
            print("🔧 使用正则表达式解析...")
            pattern = r'data-speech="([^"]*)"'
            matches = re.findall(pattern, content)
            
            print(f"📊 找到 {len(matches)} 个匹配")
            
            for i, text in enumerate(matches):
                if text.strip():
                    slides.append({
                        'index': i + 1,
                        'text': text.strip()
                    })
                    print(f"  [{i+1}] 长度:{len(text)} - {text[:50]}...")
        
        print()
        print("=" * 60)
        print("📝 完整提取的文本:")
        
        for slide in slides:
            print(f"\n🎯 幻灯片 {slide['index']}:")
            print(f"📏 长度: {len(slide['text'])} 字符")
            print(f"📄 内容: {slide['text']}")
            print("-" * 40)
        
        return slides
        
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    # 测试多个可能的HTML文件
    test_files = [
        "outputs/a00f042c-f472-4844-ad59-fda9b39970fc/presentation.html",
        "outputs/71b7c0aa-a6ad-4702-a5e9-75938984c02d/presentation.html",
        "create/test_ppt.html"
    ]
    
    print("🔍 调试HTML解析问题")
    print("检查从HTML中实际提取的文本内容")
    print()
    
    for html_file in test_files:
        if os.path.exists(html_file):
            print("=" * 80)
            slides = debug_html_parsing(html_file)
            
            if slides:
                # 检查是否包含倾听相关内容
                listening_found = any("倾听" in slide['text'] for slide in slides)
                if listening_found:
                    print("✅ 发现《倾听的艺术》相关内容")
                else:
                    print("⚠️ 未发现《倾听的艺术》相关内容")
            print()
        else:
            print(f"⏭️ 跳过不存在的文件: {html_file}")

if __name__ == "__main__":
    main()
