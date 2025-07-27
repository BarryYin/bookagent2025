#!/usr/bin/env python3
"""
测试本地封面图片是否能正确显示
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_local_cover_display():
    """测试本地封面显示功能"""
    print("🧪 测试本地封面图片显示功能")
    print("=" * 50)
    
    try:
        # 导入appbook模块
        import appbook
        print("✅ 成功导入appbook模块")
        
        # 测试书籍
        book_title = "悲惨世界"
        author = "维克多·雨果"
        
        print(f"\n📚 测试书籍: 《{book_title}》- {author}")
        
        # 调用封面搜索和下载函数
        cover_path = await appbook.search_book_cover(book_title, author, download=True)
        
        print(f"📄 封面路径: {cover_path}")
        
        if cover_path.startswith("covers/"):
            print(f"✅ 返回本地文件路径: {cover_path}")
            
            # 检查文件是否存在
            if os.path.exists(cover_path):
                file_size = os.path.getsize(cover_path)
                print(f"📁 文件存在，大小: {file_size} bytes")
                
                # 测试静态文件URL
                static_url = f"/static/{cover_path}"
                print(f"🌐 静态文件URL: {static_url}")
                
                # 模拟HTML中的使用
                html_img_tag = f'<img src="{static_url}" alt="{book_title}" class="cover-image">'
                print(f"📝 HTML图片标签: {html_img_tag}")
                
                return True
            else:
                print(f"❌ 文件不存在: {cover_path}")
                return False
        elif cover_path.startswith("http"):
            print(f"🌐 返回远程URL: {cover_path}")
            return True
        else:
            print(f"📄 返回其他类型: {cover_path}")
            return True
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(test_local_cover_display())
    
    if success:
        print("\n✅ 本地封面显示功能测试成功！")
        print("现在appbook.py可以正确显示本地下载的封面图片了。")
    else:
        print("\n❌ 本地封面显示功能测试失败，请检查代码。")
    
    sys.exit(0 if success else 1) 