#!/usr/bin/env python3
"""
修复现有PPT文件的工具
"""
import os
import re
import glob

def fix_ppt_file(file_path):
    """修复单个PPT文件"""
    print(f"正在修复: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否需要修复
    if 'showSlide(0);' in content and 'updateNavigationButtons();' in content:
        print(f"  ✓ {file_path} 已经包含必要的功能")
        return False
    
    # 修复JavaScript初始化
    js_fix = """
        // 确保初始化
        document.addEventListener('DOMContentLoaded', function() {
            console.log('PPT初始化开始...');
            updateDots(currentSlide);
            updateNarration(currentSlide);
            updateNavigationButtons();
            console.log('PPT初始化完成，当前页:', currentSlide + 1, '/', totalSlides);
        });
    """
    
    # 在</script>标签前插入修复代码
    if '</script>' in content:
        content = content.replace('</script>', js_fix + '\n    </script>')
    
    # 确保CSS正确
    css_fixes = """
        /* 确保分页显示正确 */
        .slide {
            position: absolute !important;
            width: 100% !important;
            height: 100% !important;
            opacity: 0 !important;
            transform: translateX(100%) !important;
            transition: all 0.5s ease !important;
        }
        
        .slide.active {
            opacity: 1 !important;
            transform: translateX(0) !important;
        }
        
        .navigation {
            z-index: 9999 !important;
        }
        
        .narration-panel {
            z-index: 9999 !important;
        }
    """
    
    # 在</style>标签前插入CSS修复
    if '</style>' in content:
        content = content.replace('</style>', css_fixes + '\n    </style>')
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✓ {file_path} 修复完成")
    return True

def fix_all_ppt_files():
    """修复所有现有的PPT文件"""
    output_dirs = glob.glob('outputs/*/presentation.html')
    
    if not output_dirs:
        print("没有找到需要修复的PPT文件")
        return
    
    print(f"找到 {len(output_dirs)} 个PPT文件需要检查")
    
    fixed_count = 0
    for ppt_file in output_dirs:
        if fix_ppt_file(ppt_file):
            fixed_count += 1
    
    print(f"\n修复完成！共修复了 {fixed_count} 个文件")
    
    if fixed_count > 0:
        print("\n请刷新浏览器页面查看修复效果")
        print("如果仍有问题，请按 Ctrl+F5 强制刷新清除缓存")

if __name__ == "__main__":
    fix_all_ppt_files()