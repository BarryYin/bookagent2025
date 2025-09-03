#!/usr/bin/env python3
"""
豆瓣书籍封面搜索功能演示
"""
import asyncio
import logging
from cover_search import search_book_cover

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def demo_cover_search():
    """演示书籍封面搜索功能"""
    print("="*60)
    print("豆瓣书籍封面搜索功能演示")
    print("="*60)
    
    # 测试书籍列表
    test_books = [
        ("活着", "余华"),
        ("三体", "刘慈欣"),
        ("红楼梦", "曹雪芹"),
        ("白夜行", "东野圭吾"),
        ("解忧杂货店", "东野圭吾"),
        ("平凡的世界", "路遥"),
        ("围城", "钱钟书"),
        ("百年孤独", "加西亚·马尔克斯"),
    ]
    
    successful_searches = 0
    total_searches = len(test_books)
    
    for i, (title, author) in enumerate(test_books, 1):
        print(f"\n[{i}/{total_searches}] 搜索: 《{title}》 - {author}")
        print("-" * 50)
        
        try:
            result = await search_book_cover(title, author)
            
            if result:
                cover_url = result.get("cover_url", "")
                source = result.get("source", "未知")
                is_default = result.get("is_default", True)
                metadata = result.get("metadata", {})
                
                print(f"✅ 搜索成功!")
                print(f"📷 封面URL: {cover_url}")
                print(f"🌐 数据源: {source}")
                print(f"🎨 默认封面: {'是' if is_default else '否'}")
                
                if metadata:
                    if 'rating' in metadata:
                        rating = metadata['rating']
                        if isinstance(rating, dict) and 'value' in rating:
                            print(f"⭐ 评分: {rating['value']}")
                    
                    if 'abstract' in metadata:
                        print(f"📝 简介: {metadata['abstract']}")
                
                if not is_default:
                    successful_searches += 1
            else:
                print("❌ 搜索失败: 未找到结果")
                
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
        
        # 添加延迟以避免频繁请求
        if i < total_searches:
            await asyncio.sleep(1)
    
    print("\n" + "="*60)
    print(f"搜索完成! 成功率: {successful_searches}/{total_searches} ({successful_searches/total_searches*100:.1f}%)")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(demo_cover_search())
