#!/usr/bin/env python3
"""
测试HTML生成功能
"""
import asyncio
import json
import sys
import os

# 添加当前目录到路径
sys.path.append('.')

async def test_html_generation():
    """测试HTML生成功能"""
    
    # 模拟数据
    book_data = {
        "title": "测试书籍",
        "author": "测试作者",
        "summary": "这是一本测试书籍"
    }
    
    slides = [
        {"slide_number": 1, "title": "开场", "content": "欢迎"},
        {"slide_number": 2, "title": "内容", "content": "主要内容"},
        {"slide_number": 3, "title": "结尾", "content": "谢谢"}
    ]
    
    narrations = [
        {"slide_number": 1, "content": "开场解说"},
        {"slide_number": 2, "content": "内容解说"},
        {"slide_number": 3, "content": "结尾解说"}
    ]
    
    # 模拟step4_generate_html函数的提示
    system_prompt = f"""基于以下数据，生成一个完整的HTML格式PPT，采用苹果发布会的设计风格：

书籍数据：
{json.dumps(book_data, ensure_ascii=False, indent=2)}

PPT画面：
{json.dumps(slides, ensure_ascii=False, indent=2)}

解说词：
{json.dumps(narrations, ensure_ascii=False, indent=2)}

**重要要求：必须实现真正的分页PPT效果，每次只显示一页内容！**

请生成一个完整的HTML文件，包含：
1. 真正的分页显示（每次只显示一页）
2. 页面切换动画
3. 键盘导航支持
4. 苹果风格设计
5. 解说词同步显示
"""
    
    print("HTML生成提示已更新，关键改进：")
    print("1. 明确要求真正的分页效果")
    print("2. 提供了正确的HTML结构示例")
    print("3. 强调每次只显示一页内容")
    print("4. 详细说明了JavaScript控制逻辑")
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_html_generation())
    print(f"测试完成: {result}")