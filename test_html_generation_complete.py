#!/usr/bin/env python3
"""
测试HTML生成的完整性
"""
import asyncio
import json
import sys
import os

# 添加当前目录到路径
sys.path.append('.')

async def test_complete_generation():
    """测试完整的HTML生成"""
    
    # 模拟完整的生成过程
    from appbook import step1_extract_book_data, step2_create_ppt_slides, step3_create_narration, step4_generate_html, clean_html_content
    
    topic = "活着"
    
    try:
        print("开始测试完整生成过程...")
        
        # 步骤1：提取书本数据
        print("1. 提取书本数据...")
        book_data = await step1_extract_book_data(topic)
        print(f"   书本数据: {json.dumps(book_data, ensure_ascii=False, indent=2)[:200]}...")
        
        # 步骤2：创建PPT画面
        print("2. 创建PPT画面...")
        slides = await step2_create_ppt_slides(book_data)
        print(f"   生成了 {len(slides) if isinstance(slides, list) else 'N/A'} 页PPT")
        
        # 步骤3：创建解说词
        print("3. 创建解说词...")
        narrations = await step3_create_narration(slides, book_data)
        print(f"   生成了 {len(narrations) if isinstance(narrations, list) else 'N/A'} 段解说词")
        
        # 步骤4：生成HTML
        print("4. 生成HTML...")
        html_content = await step4_generate_html(slides, narrations, book_data)
        
        # 清理HTML内容
        html_content = clean_html_content(html_content)
        
        # 验证HTML完整性
        print("5. 验证HTML完整性...")
        issues = []
        
        if not html_content.strip().startswith('<!DOCTYPE html>'):
            issues.append("缺少 DOCTYPE 声明")
        
        if not html_content.strip().endswith('</html>'):
            issues.append("缺少 </html> 结束标签")
        
        if '<head>' not in html_content or '</head>' not in html_content:
            issues.append("缺少完整的 <head> 部分")
        
        if '<body>' not in html_content or '</body>' not in html_content:
            issues.append("缺少完整的 <body> 部分")
        
        if '<script>' not in html_content or '</script>' not in html_content:
            issues.append("缺少 JavaScript 代码")
        
        if 'showSlide' not in html_content:
            issues.append("缺少关键的 JavaScript 函数")
        
        if '```' in html_content:
            issues.append("包含代码块标记")
        
        # 检查HTML长度
        html_length = len(html_content)
        print(f"   HTML长度: {html_length} 字符")
        
        if html_length < 1000:
            issues.append(f"HTML内容过短 ({html_length} 字符)")
        
        # 输出结果
        if issues:
            print("❌ HTML验证失败:")
            for issue in issues:
                print(f"   - {issue}")
            
            # 保存问题HTML用于调试
            with open('debug_html.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            print("   问题HTML已保存到 debug_html.html")
            
        else:
            print("✅ HTML验证通过!")
            
            # 保存测试HTML
            with open('test_complete.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            print("   测试HTML已保存到 test_complete.html")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_complete_generation())
    print(f"\n测试结果: {'通过' if result else '失败'}")