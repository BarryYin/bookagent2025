#!/usr/bin/env python3
"""
清理HTML文件中的非HTML元素
"""
import os
import glob
import re

def clean_html_file(file_path):
    """清理单个HTML文件"""
    print(f"正在清理: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 移除开头的 ```html 标记
    content = re.sub(r'^```html\s*\n?', '', content, flags=re.MULTILINE)
    
    # 移除结尾的 ``` 标记和后续的所有内容
    content = re.sub(r'\n?```[\s\S]*$', '', content)
    
    # 确保文件以 </html> 结尾
    if not content.strip().endswith('</html>'):
        # 找到最后一个 </html> 标签的位置
        last_html_match = None
        for match in re.finditer(r'</html>', content):
            last_html_match = match
        
        if last_html_match:
            # 截取到最后一个 </html> 标签
            content = content[:last_html_match.end()]
    
    # 移除多余的空行
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    # 确保文件以换行符结尾
    if not content.endswith('\n'):
        content += '\n'
    
    # 检查是否有变化
    if content != original_content:
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ {file_path} 清理完成")
        return True
    else:
        print(f"  - {file_path} 无需清理")
        return False

def clean_all_html_files():
    """清理所有HTML文件"""
    html_files = glob.glob('outputs/*/presentation.html')
    
    if not html_files:
        print("没有找到需要清理的HTML文件")
        return
    
    print(f"找到 {len(html_files)} 个HTML文件需要检查")
    
    cleaned_count = 0
    for html_file in html_files:
        if clean_html_file(html_file):
            cleaned_count += 1
    
    print(f"\n清理完成！共清理了 {cleaned_count} 个文件")
    
    if cleaned_count > 0:
        print("\n文件已清理，现在应该可以正常在浏览器中打开了")

def validate_html_file(file_path):
    """验证HTML文件的完整性"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # 检查基本HTML结构
    if not content.strip().startswith('<!DOCTYPE html>'):
        issues.append("缺少 DOCTYPE 声明")
    
    if '<html' not in content:
        issues.append("缺少 <html> 标签")
    
    if '</html>' not in content:
        issues.append("缺少 </html> 结束标签")
    
    if '<head>' not in content or '</head>' not in content:
        issues.append("缺少 <head> 部分")
    
    if '<body>' not in content or '</body>' not in content:
        issues.append("缺少 <body> 部分")
    
    # 检查是否有代码块标记
    if '```' in content:
        issues.append("包含代码块标记 ```")
    
    return issues

def validate_all_html_files():
    """验证所有HTML文件"""
    html_files = glob.glob('outputs/*/presentation.html')
    
    print("验证HTML文件完整性...")
    
    for html_file in html_files:
        issues = validate_html_file(html_file)
        if issues:
            print(f"❌ {html_file}:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print(f"✅ {html_file}: 结构完整")

if __name__ == "__main__":
    print("=== HTML文件清理工具 ===\n")
    clean_all_html_files()
    print("\n=== 验证清理结果 ===\n")
    validate_all_html_files()