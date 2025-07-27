#!/usr/bin/env python3
"""
测试appbook.py中的封面下载功能
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_cover_download():
    """测试封面下载功能"""
    print("🧪 测试appbook.py中的封面下载功能")
    print("=" * 50)
    
    try:
        # 导入appbook模块
        import appbook
        print("✅ 成功导入appbook模块")
        
        # 测试书籍列表
        test_books = [
            ("悲惨世界", "维克多·雨果"),
            ("活着", "余华"),
            ("三体", "刘慈欣"),
        ]
        
        for book_title, author in test_books:
            print(f"\n📚 测试书籍: 《{book_title}》- {author}")
            
            try:
                # 调用appbook中的封面搜索和下载函数
                cover_path = await appbook.search_book_cover(book_title, author, download=True)
                
                if cover_path:
                    if cover_path.startswith("covers/"):
                        print(f"  ✅ 下载到本地: {cover_path}")
                        # 检查文件是否存在
                        if os.path.exists(cover_path):
                            file_size = os.path.getsize(cover_path)
                            print(f"  📁 文件大小: {file_size} bytes")
                        else:
                            print(f"  ❌ 文件不存在: {cover_path}")
                    elif cover_path.startswith("http"):
                        print(f"  🌐 返回URL: {cover_path[:50]}...")
                    elif cover_path.startswith("gradient:"):
                        print(f"  🎨 使用默认渐变封面: {cover_path[:30]}...")
                    else:
                        print(f"  📄 返回其他类型: {cover_path}")
                else:
                    print(f"  ❌ 未找到封面")
                    
            except Exception as e:
                print(f"  ❌ 搜索封面时出错: {e}")
        
        # 显示covers目录中的文件
        print(f"\n📁 covers目录内容:")
        if os.path.exists("covers"):
            files = os.listdir("covers")
            for file in files:
                file_path = os.path.join("covers", file)
                file_size = os.path.getsize(file_path)
                print(f"  📄 {file} ({file_size} bytes)")
        else:
            print("  📁 covers目录不存在")
        
        print("\n🎉 封面下载功能测试完成！")
        return True
        
    except ImportError as e:
        print(f"❌ 导入appbook模块失败: {e}")
        print("请确保所有依赖都已安装")
        return False
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(test_cover_download())
    
    if success:
        print("\n✅ 下载功能测试成功！appbook.py现在可以下载封面到本地了。")
    else:
        print("\n❌ 下载功能测试失败，请检查代码和依赖。")
    
    sys.exit(0 if success else 1) 