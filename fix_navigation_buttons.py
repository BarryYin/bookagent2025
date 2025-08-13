#!/usr/bin/env python3
"""
批量修复所有PPT HTML文件的导航按钮z-index问题
"""

import os
import re
import glob

def fix_navigation_zindex(file_path):
    """修复单个HTML文件的导航按钮z-index"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找并替换导航样式的z-index
        # 匹配 .navigation { ... z-index: 1000; ... }
        pattern = r'(\.navigation\s*\{[^}]*?)z-index:\s*1000;([^}]*\})'
        replacement = r'\1z-index: 1001;\2'
        
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        # 检查是否有修改
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        return False
        
    except Exception as e:
        print(f"错误处理文件 {file_path}: {e}")
        return False

def main():
    """主函数：批量修复所有presentation.html文件"""
    
    # 查找所有presentation.html文件
    pattern = "outputs/*/presentation.html"
    html_files = glob.glob(pattern)
    
    print(f"找到 {len(html_files)} 个PPT HTML文件")
    
    fixed_count = 0
    
    for file_path in html_files:
        print(f"正在处理: {file_path}")
        if fix_navigation_zindex(file_path):
            fixed_count += 1
            print(f"  ✅ 已修复导航按钮z-index")
        else:
            print(f"  ⏭️  无需修复或已修复")
    
    print(f"\n修复完成！共修复了 {fixed_count} 个文件")
    print("所有PPT的导航按钮现在应该可以正常显示了。")

if __name__ == "__main__":
    main()
