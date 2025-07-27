#!/usr/bin/env python3
"""
书籍封面下载演示脚本
演示如何使用 test_cover.py 中的功能下载书籍封面到本地
"""

import asyncio
from test_cover import search_book_cover

async def demo_cover_download():
    """演示封面下载功能"""
    print("📚 书籍封面下载演示")
    print("=" * 50)
    
    # 示例书籍列表
    books = [
        {"title": "月亮与六便士", "author": "毛姆"},
        {"title": "百年孤独", "author": "加西亚·马尔克斯"},
        {"title": "1984", "author": "乔治·奥威尔"},
        {"title": "三体", "author": "刘慈欣"},
        {"title": "活着", "author": "余华"}
    ]
    
    print(f"📖 准备下载 {len(books)} 本书的封面...")
    print()
    
    results = []
    
    for i, book in enumerate(books, 1):
        print(f"🔍 [{i}/{len(books)}] 搜索《{book['title']}》- {book['author']}")
        
        try:
            # 下载封面
            result = await search_book_cover(book['title'], book['author'], download=True)
            
            if result.startswith("covers/"):
                print(f"✅ 成功下载: {result}")
                results.append({"book": book, "status": "success", "path": result})
            elif result.startswith("http"):
                print(f"⚠️ 找到URL但下载失败: {result}")
                results.append({"book": book, "status": "url_only", "url": result})
            else:
                print(f"❌ 未找到封面")
                results.append({"book": book, "status": "not_found"})
                
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            results.append({"book": book, "status": "error", "error": str(e)})
        
        print()
    
    # 显示总结
    print("📊 下载结果总结:")
    print("=" * 50)
    
    success_count = len([r for r in results if r['status'] == 'success'])
    url_only_count = len([r for r in results if r['status'] == 'url_only'])
    not_found_count = len([r for r in results if r['status'] == 'not_found'])
    error_count = len([r for r in results if r['status'] == 'error'])
    
    print(f"✅ 成功下载: {success_count} 本")
    print(f"⚠️ 仅找到URL: {url_only_count} 本")
    print(f"❌ 未找到封面: {not_found_count} 本")
    print(f"💥 搜索错误: {error_count} 本")
    
    if success_count > 0:
        print(f"\n📁 下载的封面保存在 'covers/' 目录中:")
        for result in results:
            if result['status'] == 'success':
                print(f"  📖 {result['book']['title']} - {result['path']}")

if __name__ == "__main__":
    asyncio.run(demo_cover_download()) 