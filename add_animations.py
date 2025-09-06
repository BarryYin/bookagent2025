#!/usr/bin/env python3
"""
为PPT添加动画效果
"""

def add_animations_to_html(html_content):
    """在HTML中添加动画CSS"""
    animation_css = """
                @keyframes float {
                    0%, 100% {
                        transform: translateY(0px);
                    }
                    50% {
                        transform: translateY(-20px);
                    }
                }
                
                @keyframes pulse {
                    0%, 100% {
                        transform: scale(1);
                    }
                    50% {
                        transform: scale(1.05);
                    }
                }
                
                @keyframes slideInFromLeft {
                    from {
                        opacity: 0;
                        transform: translateX(-50px);
                    }
                    to {
                        opacity: 1;
                        transform: translateX(0);
                    }
                }
                
                @keyframes slideInFromRight {
                    from {
                        opacity: 0;
                        transform: translateX(50px);
                    }
                    to {
                        opacity: 1;
                        transform: translateX(0);
                    }
                }
    """
    
    # 在</style>标签前插入动画CSS
    if "</style>" in html_content:
        html_content = html_content.replace("</style>", animation_css + "\n                </style>")
    
    return html_content

# 更新三个测试文件
files = ["test_ppt_classic_ppt.html", "test_ppt_storytelling.html", "test_ppt_modern_presentation.html"]

for filename in files:
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        updated_content = add_animations_to_html(content)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"✅ 已为 {filename} 添加动画效果")
    except Exception as e:
        print(f"❌ 处理 {filename} 失败: {e}")

print("🎉 动画效果添加完成！")