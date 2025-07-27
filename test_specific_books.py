#!/usr/bin/env python3
"""
测试特定书籍的封面搜索，验证改进后的搜索逻辑
"""

import asyncio
from test_cover import search_book_cover

async def test_specific_books():
    """测试之前下载错误的书籍"""
    print("🔍 测试特定书籍的封面搜索")
    print("=" * 60)
    
    # 之前下载错误的书籍
    books = [
        {"title": "活着", "author": "余华"},
        {"title": "三体", "author": "刘慈欣"},
        {"title": "百年孤独", "author": "加西亚·马尔克斯"},
    ]
    
    for i, book in enumerate(books, 1):
        print(f"\n📚 [{i}/{len(books)}] 测试《{book['title']}》- {book['author']}")
        print("-" * 40)
        
        try:
            result = await search_book_cover(book['title'], book['author'], download=True)
            
            if result.startswith("covers/"):
                print(f"✅ 成功下载: {result}")
            elif result.startswith("http"):
                print(f"⚠️ 找到URL但下载失败: {result}")
            else:
                print(f"❌ 未找到封面: {result}")
                
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
        
        print()

if __name__ == "__main__":
    asyncio.run(test_specific_books()) 