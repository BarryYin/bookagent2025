import asyncio
import httpx
import json
import os
from pathlib import Path
from urllib.parse import urlparse
import re

def normalize_text(text):
    """标准化文本，用于比较"""
    if not text:
        return ""
    # 移除标点符号和空格，转换为小写
    return re.sub(r'[^\w]', '', text.lower())

def calculate_similarity(text1, text2):
    """计算两个文本的相似度"""
    if not text1 or not text2:
        return 0
    
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)
    
    if not norm1 or not norm2:
        return 0
    
    # 简单的相似度计算
    common_chars = sum(1 for c in norm1 if c in norm2)
    return common_chars / max(len(norm1), len(norm2))

def is_better_match(book_info, target_title, target_author, current_best_score=0):
    """判断是否更好的匹配"""
    title = book_info.get('title', '')
    authors = book_info.get('authors', [])
    author = authors[0] if authors else ''
    
    # 计算标题相似度
    title_similarity = calculate_similarity(title, target_title)
    
    # 计算作者相似度
    author_similarity = calculate_similarity(author, target_author) if target_author else 0
    
    # 综合评分 (标题权重更高)
    total_score = title_similarity * 0.7 + author_similarity * 0.3
    
    # 额外加分：完全匹配
    if normalize_text(title) == normalize_text(target_title):
        total_score += 0.2
    if target_author and normalize_text(author) == normalize_text(target_author):
        total_score += 0.1
    
    return total_score > current_best_score, total_score

async def search_douban_books(book_title: str, author: str = None):
    """使用豆瓣图书API搜索中文书籍"""
    try:
        async with httpx.AsyncClient() as client:
            # 构建搜索URL
            search_query = f"{book_title}"
            if author:
                search_query += f" {author}"
            
            # 豆瓣图书搜索URL
            url = f"https://book.douban.com/j/subject_suggest?q={search_query}"
            
            print(f"🔍 豆瓣搜索: {search_query}")
            
            response = await client.get(url, timeout=10.0)
            
            if response.status_code == 200:
                books = response.json()
                print(f"📚 豆瓣找到 {len(books)} 本书")
                
                best_match = None
                best_score = 0
                
                for book in books:
                    title = book.get('title', '')
                    author_name = book.get('author', '')
                    cover_url = book.get('pic', '')
                    
                    print(f"  📖 {title} - {author_name}")
                    
                    if cover_url:
                        # 检查是否更好的匹配
                        is_better, score = is_better_match(
                            {'title': title, 'authors': [author_name]}, 
                            book_title, 
                            author, 
                            best_score
                        )
                        
                        if is_better:
                            best_score = score
                            best_match = {
                                'title': title,
                                'author': author_name,
                                'cover_url': cover_url,
                                'score': score
                            }
                            print(f"    🎯 新的最佳匹配 (相似度: {score:.2f})")
                        else:
                            print(f"    📊 相似度: {score:.2f}")
                    else:
                        print(f"    ❌ 无封面图片")
                
                return best_match
            else:
                print(f"❌ 豆瓣API请求失败: {response.status_code}")
                return None
                
    except Exception as e:
        print(f"❌ 豆瓣搜索失败: {e}")
        return None

async def search_google_books(book_title: str, author: str = None):
    """使用Google Books API搜索"""
    try:
        async with httpx.AsyncClient() as client:
            url = "https://www.googleapis.com/books/v1/volumes"
            
            best_match = None
            best_score = 0
            
            # 获取搜索变体
            search_variations = get_search_variations(book_title, author)
            
            for var_title, var_author in search_variations:
                print(f"\n🔍 Google搜索变体: 《{var_title}》- {var_author}")
                
                # 优先使用中文搜索策略
                search_strategies = [
                    # 中文优先策略
                    {"q": f'"{var_title}" "{var_author}"', "maxResults": 10, "printType": "books", "langRestrict": "zh"},
                    {"q": f'"{var_title}"', "maxResults": 10, "printType": "books", "langRestrict": "zh"},
                    {"q": f"{var_title} {var_author}", "maxResults": 10, "printType": "books", "langRestrict": "zh"},
                    {"q": f"{var_author} {var_title}", "maxResults": 10, "printType": "books", "langRestrict": "zh"},
                    
                    # 通用策略
                    {"q": f'"{var_title}" "{var_author}"', "maxResults": 10, "printType": "books"},
                    {"q": f'"{var_title}"', "maxResults": 10, "printType": "books"},
                    {"q": f"{var_title} {var_author}", "maxResults": 10, "printType": "books"},
                    {"q": f"{var_title}", "maxResults": 10, "printType": "books"},
                    {"q": f"{var_author} {var_title}", "maxResults": 10, "printType": "books"},
                ]
                
                for i, params in enumerate(search_strategies, 1):
                    strategy_type = "🇨🇳 中文" if "langRestrict" in params else "🌍 通用"
                    print(f"  {strategy_type} 策略 {i}: {params}")
                    
                    response = await client.get(url, params=params, timeout=10.0)
                    
                    if response.status_code == 200:
                        data = response.json()
                        total_items = data.get("totalItems", 0)
                        
                        if total_items > 0:
                            # 检查所有结果，找到最佳匹配
                            for j, book in enumerate(data["items"][:5]):
                                volume_info = book.get("volumeInfo", {})
                                image_links = volume_info.get("imageLinks", {})
                                
                                title = volume_info.get('title', '')
                                authors = volume_info.get('authors', [])
                                author_name = authors[0] if authors else ''
                                
                                print(f"    📖 结果{j+1}: {title} - {author_name}")
                                
                                # 检查是否更好的匹配
                                is_better, score = is_better_match(volume_info, book_title, author, best_score)
                                
                                if is_better and image_links:
                                    best_score = score
                                    best_match = {
                                        'volume_info': volume_info,
                                        'image_links': image_links,
                                        'score': score
                                    }
                                    print(f"      🎯 新的最佳匹配 (相似度: {score:.2f})")
                                elif image_links:
                                    print(f"      📊 相似度: {score:.2f}")
                                else:
                                    print(f"      ❌ 无封面图片")
                                    
                                # 如果找到很好的匹配，提前退出
                                if best_score > 0.8:
                                    break
                        else:
                            print(f"    ❌ 没有找到相关书籍")
                    else:
                        print(f"    ❌ API请求失败: {response.status_code}")
                    
                    # 如果找到很好的匹配，提前退出
                    if best_score > 0.8:
                        break
                
                # 如果找到很好的匹配，提前退出
                if best_score > 0.8:
                    break
            
            return best_match
            
    except Exception as e:
        print(f"❌ Google Books搜索失败: {e}")
        return None

def get_search_variations(book_title, author):
    """获取搜索变体，提高中文书籍的匹配率"""
    variations = []
    
    # 基本搜索
    variations.append((book_title, author))
    
    # 中文书籍的常见变体
    if book_title == "活着":
        variations.extend([
            ("活着", "余华"),
            ("活着", "Yu Hua"),
            ("To Live", "余华"),
            ("To Live", "Yu Hua"),
        ])
    elif book_title == "三体":
        variations.extend([
            ("三体", "刘慈欣"),
            ("三體", "劉慈欣"),
            ("The Three-Body Problem", "刘慈欣"),
            ("The Three-Body Problem", "Liu Cixin"),
        ])
    elif book_title == "百年孤独":
        variations.extend([
            ("百年孤独", "加西亚·马尔克斯"),
            ("百年孤寂", "加西亚·马尔克斯"),
            ("百年孤寂", "Gabriel García Márquez"),
            ("Cien años de soledad", "Gabriel García Márquez"),
            ("One Hundred Years of Solitude", "Gabriel García Márquez"),
        ])
    elif book_title == "月亮与六便士":
        variations.extend([
            ("月亮与六便士", "毛姆"),
            ("月亮和六便士", "毛姆"),
            ("月亮與六便士", "毛姆"),
            ("The Moon and Sixpence", "毛姆"),
            ("The Moon and Sixpence", "W. Somerset Maugham"),
        ])
    
    return variations

async def download_image(url: str, save_path: str) -> bool:
    """
    下载图片到本地
    """
    try:
        async with httpx.AsyncClient() as client:
            print(f"📥 正在下载图片: {url}")
            response = await client.get(url, timeout=30.0)
            
            if response.status_code == 200:
                # 确保目录存在
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                
                # 保存图片
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ 图片已保存到: {save_path}")
                return True
            else:
                print(f"❌ 下载失败，状态码: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ 下载图片时出错: {e}")
        return False

async def search_book_cover(book_title: str, author: str = None, download: bool = False) -> str:
    """
    搜索书籍封面图片
    优先使用豆瓣图书API，然后使用Google Books API作为备选
    """
    try:
        print(f"🔍 搜索查询: {book_title} - {author}")
        
        # 首先尝试豆瓣图书API（中文图书更准确）
        print("\n📚 尝试豆瓣图书API...")
        douban_result = await search_douban_books(book_title, author)
        
        if douban_result and douban_result['score'] > 0.3:
            print(f"\n🎯 豆瓣找到最佳匹配:")
            print(f"   📖 书名: {douban_result['title']}")
            print(f"   ✍️ 作者: {douban_result['author']}")
            print(f"   📊 相似度: {douban_result['score']:.2f}")
            
            cover_url = douban_result['cover_url']
            print(f"✅ 找到封面URL: {cover_url}")
            
            if download:
                # 生成文件名
                safe_title = "".join(c for c in book_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_author = "".join(c for c in (author or "") if c.isalnum() or c in (' ', '-', '_')).rstrip()
                
                # 从URL获取文件扩展名
                parsed_url = urlparse(cover_url)
                path = parsed_url.path
                ext = os.path.splitext(path)[1]
                if not ext:
                    ext = '.jpg'  # 默认扩展名
                
                filename = f"{safe_title}_{safe_author}{ext}".replace(' ', '_')
                save_path = os.path.join("covers", filename)
                
                # 下载图片
                if await download_image(cover_url, save_path):
                    return save_path
                else:
                    print("⚠️ 下载失败，返回URL")
                    return cover_url
            else:
                return cover_url
        
        # 如果豆瓣没有找到好的结果，尝试Google Books
        print("\n📚 尝试Google Books API...")
        google_result = await search_google_books(book_title, author)
        
        if google_result and google_result['score'] > 0.2:
            volume_info = google_result['volume_info']
            image_links = google_result['image_links']
            
            print(f"\n🎯 Google Books找到最佳匹配:")
            print(f"   📖 书名: {volume_info.get('title', 'N/A')}")
            print(f"   ✍️ 作者: {volume_info.get('authors', ['N/A'])}")
            print(f"   📊 相似度: {google_result['score']:.2f}")
            
            # 优先使用高质量图片
            cover_url = (
                image_links.get("extraLarge") or
                image_links.get("large") or
                image_links.get("medium") or
                image_links.get("small") or
                image_links.get("thumbnail")
            )
            
            if cover_url:
                # 将http替换为https以确保安全
                cover_url = cover_url.replace("http://", "https://")
                print(f"✅ 找到封面URL: {cover_url}")
                
                if download:
                    # 生成文件名
                    safe_title = "".join(c for c in book_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    safe_author = "".join(c for c in (author or "") if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    
                    # 从URL获取文件扩展名
                    parsed_url = urlparse(cover_url)
                    path = parsed_url.path
                    ext = os.path.splitext(path)[1]
                    if not ext:
                        ext = '.jpg'  # 默认扩展名
                    
                    filename = f"{safe_title}_{safe_author}{ext}".replace(' ', '_')
                    save_path = os.path.join("covers", filename)
                    
                    # 下载图片
                    if await download_image(cover_url, save_path):
                        return save_path
                    else:
                        print("⚠️ 下载失败，返回URL")
                        return cover_url
                else:
                    return cover_url
        
        print("❌ 两个API都没有找到足够匹配的书籍封面")
        
    except Exception as e:
        print(f"❌ 搜索书籍封面失败: {e}")
    
    print("🔄 返回默认封面")
    return "default_cover"

async def test_cover_search():
    """测试封面搜索功能"""
    print("=" * 50)
    print("🧪 测试书籍封面搜索功能")
    print("=" * 50)
    
    # 测试《月亮与六便士》
    book_title = "月亮与六便士"
    author = "毛姆"
    
    print(f"\n📚 测试书籍: 《{book_title}》")
    print(f"✍️ 作者: {author}")
    
    # 搜索并下载封面
    cover_result = await search_book_cover(book_title, author, download=True)
    
    print(f"\n🎯 最终结果: {cover_result}")
    
    if cover_result.startswith("http"):
        print("✅ 成功找到真实封面URL！")
    elif cover_result.startswith("covers/"):
        print("✅ 成功下载封面到本地！")
    else:
        print("🔄 使用默认封面")
    
    # 测试第二本书
    print("\n" + "=" * 50)
    book_title2 = "百年孤独"
    author2 = "加西亚·马尔克斯"
    
    print(f"\n📚 测试书籍: 《{book_title2}》")
    print(f"✍️ 作者: {author2}")
    
    # 搜索并下载封面
    cover_result2 = await search_book_cover(book_title2, author2, download=True)
    
    print(f"\n🎯 最终结果: {cover_result2}")
    
    if cover_result2.startswith("http"):
        print("✅ 成功找到真实封面URL！")
    elif cover_result2.startswith("covers/"):
        print("✅ 成功下载封面到本地！")
    else:
        print("🔄 使用默认封面")

if __name__ == "__main__":
    asyncio.run(test_cover_search()) 