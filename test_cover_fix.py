#!/usr/bin/env python3
"""
测试修复后的封面搜索功能
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_cover_search_fix():
    """测试修复后的封面搜索功能"""
    print("=" * 60)
    print("🧪 测试修复后的书籍封面搜索功能")
    print("=" * 60)
    
    # 测试书籍列表
    test_books = [
        ("贫穷的本质", "阿比吉特·班纳吉 / 埃斯特·迪弗洛"),
        ("月亮与六便士", "毛姆"),
        ("活着", "余华"),
        ("三体", "刘慈欣"),
    ]
    
    # 首先测试新的封面搜索器
    print("\n🔍 测试新的封面搜索器 (cover_search.py)")
    try:
        from cover_search import book_cover_searcher
        
        for book_title, author in test_books:
            print(f"\n📚 测试书籍: 《{book_title}》- {author}")
            try:
                result = await book_cover_searcher.search_cover(book_title, author)
                
                if result:
                    print(f"  ✅ 搜索成功:")
                    print(f"    📖 来源: {result.get('source', 'Unknown')}")
                    print(f"    🔗 URL: {result.get('cover_url', 'N/A')[:100]}...")
                    print(f"    🎯 是否默认: {result.get('is_default', False)}")
                else:
                    print(f"  ❌ 搜索失败")
                    
            except Exception as e:
                print(f"  ❌ 搜索出错: {e}")
                
    except ImportError as e:
        print(f"❌ 无法导入新的封面搜索器: {e}")
    
    # 然后测试旧的搜索方法
    print(f"\n🔍 测试旧的封面搜索方法 (test_cover.py)")
    try:
        from test_cover import search_book_cover
        
        for book_title, author in test_books:
            print(f"\n📚 测试书籍: 《{book_title}》- {author}")
            try:
                result = await search_book_cover(book_title, author, download=False)
                
                if result and result != "default_cover":
                    print(f"  ✅ 搜索成功: {result[:100]}...")
                else:
                    print(f"  ❌ 搜索失败，返回默认封面")
                    
            except Exception as e:
                print(f"  ❌ 搜索出错: {e}")
                
    except ImportError as e:
        print(f"❌ 无法导入旧的封面搜索器: {e}")
    
    # 测试集成的搜索函数
    print(f"\n🔍 测试集成的封面搜索函数 (appbook.py)")
    try:
        from appbook import search_book_cover as integrated_search
        
        for book_title, author in test_books:
            print(f"\n📚 测试书籍: 《{book_title}》- {author}")
            try:
                result = await integrated_search(book_title, author, download=False)
                
                if result and not result.startswith("gradient:"):
                    print(f"  ✅ 搜索成功: {result[:100]}...")
                else:
                    print(f"  ❌ 搜索失败，返回默认封面")
                    
            except Exception as e:
                print(f"  ❌ 搜索出错: {e}")
                
    except ImportError as e:
        print(f"❌ 无法导入集成的封面搜索器: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_cover_search_fix())