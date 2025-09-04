#!/usr/bin/env python3
"""
改进的书籍封面搜索功能演示 - 测试多种数据源
"""
import asyncio
import logging
from cover_search import search_book_cover

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def demo_improved_cover_search():
    """演示改进的书籍封面搜索功能"""
    print("="*60)
    print("改进的书籍封面搜索功能演示")
    print("支持多种数据源：Google Books、Open Library、ISBN数据库等")
    print("="*60)
    
    # 测试书籍列表 - 包含不同类型的书籍
    test_books = [
        ("活着", "余华", None),
        ("三体", "刘慈欣", None),
        ("哈利·波特与魔法石", "J.K.罗琳", "9787020033119"),  # 带ISBN
        ("1984", "乔治·奥威尔", None),
        ("小王子", "安东尼·德·圣-埃克苏佩里", None),
        ("百年孤独", "加西亚·马尔克斯", None),
        ("Python编程：从入门到实践", "埃里克·马瑟斯", None),  # 技术书籍
        ("不存在的书籍测试", "不存在的作者", None),  # 测试找不到的情况
    ]
    
    successful_searches = 0
    total_searches = len(test_books)
    source_stats = {}
    
    for i, (title, author, isbn) in enumerate(test_books, 1):
        print(f"\n[{i}/{total_searches}] 搜索: 《{title}》")
        print(f"作者: {author}")
        if isbn:
            print(f"ISBN: {isbn}")
        print("-" * 50)
        
        try:
            result = await search_book_cover(title, author, isbn)
            
            if result:
                cover_url = result.get("cover_url", "")
                source = result.get("source", "未知")
                is_default = result.get("is_default", True)
                metadata = result.get("metadata", {})
                
                # 统计数据源使用情况
                source_stats[source] = source_stats.get(source, 0) + 1
                
                if is_default:
                    print(f"🎨 使用默认封面")
                else:
                    print(f"✅ 搜索成功!")
                    successful_searches += 1
                
                print(f"📷 封面URL: {cover_url[:80]}...")
                print(f"🌐 数据源: {source}")
                
                # 显示额外的元数据
                if metadata:
                    if 'authors' in metadata and metadata['authors']:
                        print(f"👥 作者信息: {', '.join(metadata['authors'])}")
                    if 'publisher' in metadata and metadata['publisher']:
                        print(f"📚 出版社: {metadata['publisher']}")
                    if 'published_date' in metadata and metadata['published_date']:
                        print(f"📅 出版日期: {metadata['published_date']}")
                    if 'query_used' in metadata:
                        print(f"🔍 使用的查询: {metadata['query_used']}")
            else:
                print("❌ 搜索失败: 未找到结果")
                
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
        
        # 添加延迟以避免频繁请求
        if i < total_searches:
            await asyncio.sleep(1)
    
    # 显示统计信息
    print("\n" + "="*60)
    print("搜索结果统计")
    print("="*60)
    print(f"总搜索次数: {total_searches}")
    print(f"成功找到封面: {successful_searches}")
    print(f"成功率: {successful_searches/total_searches*100:.1f}%")
    
    print("\n数据源使用统计:")
    for source, count in sorted(source_stats.items(), key=lambda x: x[1], reverse=True):
        percentage = count/total_searches*100
        print(f"  {source}: {count} 次 ({percentage:.1f}%)")
    
    print("\n建议:")
    if source_stats.get("Google Books", 0) > 0:
        print("✅ Google Books API 工作正常，是主要的可靠数据源")
    if source_stats.get("Open Library", 0) > 0:
        print("✅ Open Library API 可用，提供了额外的封面资源")
    if source_stats.get("Generated Default", 0) > 0:
        print("🎨 对于找不到封面的书籍，系统自动生成了美观的默认封面")
    
    print("="*60)

if __name__ == "__main__":
    asyncio.run(demo_improved_cover_search())
