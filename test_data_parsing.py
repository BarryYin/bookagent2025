#!/usr/bin/env python3
"""
测试数据解析功能
"""
import json
import sys
sys.path.append('.')

from appbook import parse_ai_response, extract_book_title, process_slides_data, process_narrations_data, generate_reliable_ppt_html_internal

def test_data_parsing():
    """测试数据解析功能"""
    
    # 使用真实的生成数据
    with open('outputs/de0626f9-0de0-456c-8973-f4ca65650e82/data.json', 'r', encoding='utf-8') as f:
        real_data = json.load(f)
    
    print("=== 测试数据解析 ===")
    
    # 测试book_data解析
    book_data = real_data['book_data']
    parsed_book_data = parse_ai_response(book_data)
    book_title = extract_book_title(parsed_book_data)
    print(f"书籍标题: {book_title}")
    
    # 测试slides解析
    slides_data = real_data['slides']
    parsed_slides = parse_ai_response(slides_data)
    processed_slides = process_slides_data(parsed_slides, book_title)
    print(f"处理后的幻灯片数量: {len(processed_slides)}")
    for i, slide in enumerate(processed_slides[:3]):  # 只显示前3个
        print(f"  幻灯片{i+1}: {slide['title']} - {slide['subtitle']}")
    
    # 测试narrations解析
    narrations_data = real_data['narrations']
    parsed_narrations = parse_ai_response(narrations_data)
    processed_narrations = process_narrations_data(parsed_narrations, book_title)
    print(f"处理后的解说词数量: {len(processed_narrations)}")
    for i, narration in enumerate(processed_narrations[:3]):  # 只显示前3个
        print(f"  解说词{i+1}: {narration[:50]}...")
    
    # 测试HTML生成
    print("\n=== 测试HTML生成 ===")
    html_content = generate_reliable_ppt_html_internal(slides_data, narrations_data, book_data)
    
    print(f"HTML长度: {len(html_content)} 字符")
    print(f"HTML开头: {html_content[:100]}...")
    print(f"HTML结尾: ...{html_content[-100:]}")
    
    # 验证HTML完整性
    issues = []
    if not html_content.strip().startswith('<!DOCTYPE html>'):
        issues.append("缺少 DOCTYPE 声明")
    if not html_content.strip().endswith('</html>'):
        issues.append("缺少 </html> 结束标签")
    if '<script>' not in html_content or '</script>' not in html_content:
        issues.append("缺少 JavaScript 代码")
    if 'showSlide' not in html_content:
        issues.append("缺少关键的 JavaScript 函数")
    
    if issues:
        print("❌ HTML验证失败:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("✅ HTML验证通过!")
        
        # 保存测试HTML
        with open('test_parsed_data.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("   测试HTML已保存到 test_parsed_data.html")
        return True

if __name__ == "__main__":
    result = test_data_parsing()
    print(f"\n测试结果: {'通过' if result else '失败'}")