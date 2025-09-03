"""
书籍封面搜索模块
支持多种API和备用方案
"""
import asyncio
import httpx
import json
import hashlib
import base64
from typing import Optional, Dict, Any
import logging
import re
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class BookCoverSearcher:
    """书籍封面搜索器"""
    
    def __init__(self):
        self.timeout = 15.0  # 增加超时以应对网络波动
        self.max_retries = 2
    
    async def search_cover(self, title: str, author: str = None, isbn: str = None) -> Dict[str, Any]:
        """
        搜索书籍封面
        返回格式: {
            "cover_url": str,
            "source": str,
            "is_default": bool,
            "metadata": dict
        }
        """
        logger.info(f"开始搜索书籍封面: {title} by {author}")
        
        # 按优先级尝试不同的搜索方法，优先使用豆瓣网页抓取
        search_methods = [
            self._search_douban_scrape,
            self._search_google_books,
            self._search_open_library,
            self._search_douban_books, # 旧的API方法作为最后备用
        ]
        
        for method in search_methods:
            try:
                result = await method(title, author, isbn)
                if result and result.get("cover_url"):
                    logger.info(f"找到封面: {result['source']}")
                    return result
            except Exception as e:
                logger.warning(f"搜索方法 {method.__name__} 失败: {e}")
                continue
        
        # 如果所有方法都失败，返回默认封面
        logger.info("未找到封面，使用默认封面")
        return self._generate_default_cover(title, author)

    async def _search_douban_scrape(self, title: str, author: str = None, isbn: str = None) -> Optional[Dict[str, Any]]:
        """通过抓取豆瓣搜索页面并解析其内置JSON数据来查找封面"""
        logger.info(f"尝试通过解析豆瓣网页JSON搜索: {title}")
        try:
            search_text = title
            # 豆瓣搜索对作者的权重不高，有时反而影响结果，所以优先只用标题
            # if author:
            #     search_text += f" {author}"
            
            url = "https://search.douban.com/book/subject_search"
            params = {"search_text": search_text, "cat": "1001"}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
            }

            async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
                response = await client.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                html_content = response.text

                # 使用正则表达式提取页面内嵌的JSON数据
                match = re.search(r'window\.__DATA__ = (\{.*?\});', html_content)
                if not match:
                    logger.warning("在豆瓣页面中未找到 window.__DATA__ JSON数据")
                    return None

                data = json.loads(match.group(1))
                items = data.get('items', [])
                if not items:
                    logger.info("豆瓣返回的JSON数据中没有搜索结果 (items)")
                    return None

                # 寻找最佳匹配
                best_match = self._find_best_douban_match(items, title, author)
                if not best_match:
                    logger.info(f"在豆瓣返回的 {len(items)} 个结果中未找到'{title}'的匹配项")
                    return None

                cover_url = best_match.get('cover_url')
                if not cover_url:
                    logger.info("找到的豆瓣匹配项中没有封面URL")
                    return None

                # 豆瓣的图片URL有时是小图(m/s)，替换为大图(l)
                cover_url = cover_url.replace("/m/", "/l/").replace("/s/", "/l/")

                return {
                    "cover_url": cover_url,
                    "source": "Douban (JSON)",
                    "is_default": False,
                    "metadata": {
                        "title": best_match.get('title'),
                        "abstract": best_match.get('abstract'),
                        "rating": best_match.get('rating'),
                        "douban_id": best_match.get('id')
                    }
                }
        except json.JSONDecodeError as e:
            logger.error(f"解析豆瓣JSON数据失败: {e}")
            return None
        except Exception as e:
            logger.error(f"豆瓣网页解析过程失败: {e}")
            return None

    def _find_best_douban_match(self, items: list, target_title: str, target_author: str = None) -> Optional[dict]:
        """在从豆瓣JSON返回的列表中找到最匹配的书籍"""
        # 移除所有非中文字符以便更准确地匹配
        clean_target_title = re.sub(r'[\W_a-zA-Z0-9]', '', target_title)

        for item in items:
            if item.get('tpl_name') != 'search_subject':
                continue

            title = item.get('title', '')
            abstract = item.get('abstract', '')

            # 同样清理豆瓣结果的标题
            clean_title = re.sub(r'[\W_a-zA-Z0-9]', '', title)

            # 检查标题是否足够匹配
            if clean_target_title in clean_title:
                # 如果提供了作者，进一步检查作者是否匹配
                if target_author:
                    if target_author in abstract:
                        return item # 标题和作者都匹配
                else:
                    return item # 只提供了标题，且匹配
        
        # 如果精确匹配失败，退而求其次，返回第一个看起来像书的结果
        for item in items:
            if item.get('tpl_name') == 'search_subject':
                return item

        return None
    
    async def _search_google_books(self, title: str, author: str = None, isbn: str = None) -> Optional[Dict[str, Any]]:
        """使用Google Books API搜索"""
        try:
            query = title
            if author:
                query += f" {author}"
            if isbn:
                query = f"isbn:{isbn}"
            
            async with httpx.AsyncClient() as client:
                url = "https://www.googleapis.com/books/v1/volumes"
                params = {
                    "q": query,
                    "maxResults": 5,
                    "printType": "books",
                    "langRestrict": "zh"  # 优先中文
                }
                
                response = await client.get(url, params=params, timeout=self.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("totalItems", 0) > 0:
                        # 寻找最匹配的书籍
                        best_match = self._find_best_match(data["items"], title, author)
                        if best_match:
                            volume_info = best_match.get("volumeInfo", {})
                            image_links = volume_info.get("imageLinks", {})
                            
                            # 优先使用高质量图片
                            cover_url = (
                                image_links.get("extraLarge") or
                                image_links.get("large") or
                                image_links.get("medium") or
                                image_links.get("small") or
                                image_links.get("thumbnail")
                            )
                            
                            if cover_url:
                                # 确保使用HTTPS
                                cover_url = cover_url.replace("http://", "https://")
                                return {
                                    "cover_url": cover_url,
                                    "source": "Google Books",
                                    "is_default": False,
                                    "metadata": {
                                        "title": volume_info.get("title"),
                                        "authors": volume_info.get("authors", []),
                                        "publisher": volume_info.get("publisher"),
                                        "published_date": volume_info.get("publishedDate"),
                                        "page_count": volume_info.get("pageCount"),
                                        "categories": volume_info.get("categories", [])
                                    }
                                }
        except Exception as e:
            logger.error(f"Google Books API搜索失败: {e}")
            return None
    
    async def _search_douban_books(self, title: str, author: str = None, isbn: str = None) -> Optional[Dict[str, Any]]:
        """使用豆瓣API搜索（注意：豆瓣API可能有限制）"""
        try:
            # 豆瓣API已经不太稳定，这里主要作为备用方案
            # 实际使用时可能需要其他方法
            query = title
            if author:
                query += f" {author}"
            
            async with httpx.AsyncClient() as client:
                # 尝试多个豆瓣API接口
                api_urls = [
                    "https://book.douban.com/j/subject_suggest",
                    "https://api.douban.com/v2/book/search"
                ]
                
                for api_url in api_urls:
                    try:
                        if "subject_suggest" in api_url:
                            params = {"q": query}
                        else:
                            params = {"q": query, "count": 5}
                        
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                            'Accept': 'application/json, text/plain, */*',
                            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                            'Referer': 'https://book.douban.com/'
                        }
                        
                        response = await client.get(api_url, params=params, headers=headers, timeout=self.timeout)
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            if "subject_suggest" in api_url:
                                # 处理 subject_suggest 接口的响应
                                books = data if isinstance(data, list) else []
                                if books:
                                    book = books[0]  # 取第一个结果
                                    cover_url = book.get("pic")
                                    if cover_url and cover_url != "https://img1.doubanio.com/f/shire/e1454c9d8b9fce83e2a40b883d3fbf36c8e7e2b9/pics/book-default-lpic.gif":
                                        return {
                                            "cover_url": cover_url,
                                            "source": "Douban (suggest)",
                                            "is_default": False,
                                            "metadata": {
                                                "title": book.get("title"),
                                                "author": book.get("author_name"),
                                                "douban_id": book.get("id")
                                            }
                                        }
                            else:
                                # 处理 v2/book/search 接口的响应
                                books = data.get("books", [])
                                if books:
                                    book = books[0]
                                    cover_url = book.get("image")
                                    if cover_url and cover_url != "https://img1.doubanio.com/f/shire/e1454c9d8b9fce83e2a40b883d3fbf36c8e7e2b9/pics/book-default-lpic.gif":
                                        return {
                                            "cover_url": cover_url,
                                            "source": "Douban (API)",
                                            "is_default": False,
                                            "metadata": {
                                                "title": book.get("title"),
                                                "authors": [author.get("name") for author in book.get("author", [])],
                                                "publisher": book.get("publisher"),
                                                "published_date": book.get("pubdate"),
                                                "rating": book.get("rating", {}).get("average"),
                                                "tags": [tag.get("name") for tag in book.get("tags", [])]
                                            }
                                        }
                        elif response.status_code == 418:
                            logger.warning(f"豆瓣API返回418 (反爬虫机制): {api_url}")
                            continue
                        else:
                            logger.warning(f"豆瓣API请求失败 {response.status_code}: {api_url}")
                            continue
                            
                    except Exception as e:
                        logger.warning(f"豆瓣API接口 {api_url} 失败: {e}")
                        continue
                
                return None
                
        except Exception as e:
            logger.error(f"豆瓣API搜索失败: {e}")
            return None
    
    async def _search_open_library(self, title: str, author: str = None, isbn: str = None) -> Optional[Dict[str, Any]]:
        """使用Open Library API搜索"""
        try:
            async with httpx.AsyncClient() as client:
                if isbn:
                    # 使用ISBN搜索
                    url = f"https://openlibrary.org/api/books"
                    params = {
                        "bibkeys": f"ISBN:{isbn}",
                        "jscmd": "data",
                        "format": "json"
                    }
                else:
                    # 使用标题和作者搜索
                    url = "https://openlibrary.org/search.json"
                    query = title
                    if author:
                        query += f" {author}"
                    params = {
                        "q": query,
                        "limit": 5
                    }
                
                response = await client.get(url, params=params, timeout=self.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if isbn and f"ISBN:{isbn}" in data:
                        # ISBN搜索结果
                        book_data = data[f"ISBN:{isbn}"]
                        cover_url = book_data.get("cover", {}).get("large")
                        if cover_url:
                            return {
                                "cover_url": cover_url,
                                "source": "Open Library",
                                "is_default": False,
                                "metadata": {
                                    "title": book_data.get("title"),
                                    "authors": [author.get("name") for author in book_data.get("authors", [])],
                                    "publisher": book_data.get("publishers", [{}])[0].get("name") if book_data.get("publishers") else None,
                                    "published_date": book_data.get("publish_date")
                                }
                            }
                    elif "docs" in data and data["docs"]:
                        # 标题搜索结果
                        book = data["docs"][0]
                        cover_id = book.get("cover_i")
                        if cover_id:
                            cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
                            return {
                                "cover_url": cover_url,
                                "source": "Open Library",
                                "is_default": False,
                                "metadata": {
                                    "title": book.get("title"),
                                    "authors": book.get("author_name", []),
                                    "publisher": book.get("publisher", [None])[0] if book.get("publisher") else None,
                                    "published_date": book.get("first_publish_year")
                                }
                            }
        except Exception as e:
            logger.error(f"Open Library API搜索失败: {e}")
            return None
    
    def _find_best_match(self, books: list, target_title: str, target_author: str = None) -> Optional[dict]:
        """在搜索结果中找到最佳匹配"""
        best_match = None
        best_score = 0
        
        for book in books:
            volume_info = book.get("volumeInfo", {})
            title = volume_info.get("title", "")
            authors = volume_info.get("authors", [])
            
            # 计算匹配分数
            score = 0
            
            # 标题匹配
            if target_title.lower() in title.lower() or title.lower() in target_title.lower():
                score += 3
            
            # 作者匹配
            if target_author:
                for author in authors:
                    if target_author.lower() in author.lower() or author.lower() in target_author.lower():
                        score += 2
                        break
            
            # 检查是否有封面图片
            if volume_info.get("imageLinks"):
                score += 1
            
            if score > best_score:
                best_score = score
                best_match = book
        
        return best_match if best_score > 0 else books[0] if books else None
    
    def _generate_default_cover(self, title: str, author: str = None) -> Dict[str, Any]:
        """生成默认书籍封面"""
        # 预定义的渐变色方案
        gradients = [
            "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
            "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
            "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
            "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
            "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)",
            "linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)",
            "linear-gradient(135deg, #ff8a80 0%, #ea4c89 100%)",
            "linear-gradient(135deg, #8fd3f4 0%, #84fab0 100%)",
            "linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)",
            "linear-gradient(135deg, #fad0c4 0%, #ffd1ff 100%)",
            "linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)"
        ]
        
        # 根据书名哈希选择渐变
        title_hash = hashlib.md5(title.encode('utf-8')).hexdigest()
        gradient_index = int(title_hash[:2], 16) % len(gradients)
        gradient = gradients[gradient_index]
        
        # 生成SVG封面
        svg_cover = self._generate_svg_cover(title, author, gradient)
        
        return {
            "cover_url": f"data:image/svg+xml;base64,{base64.b64encode(svg_cover.encode('utf-8')).decode('utf-8')}",
            "source": "Generated Default",
            "is_default": True,
            "metadata": {
                "title": title,
                "author": author,
                "gradient": gradient,
                "type": "svg_generated"
            }
        }
    
    def _generate_svg_cover(self, title: str, author: str = None, gradient: str = None) -> str:
        """生成SVG格式的默认封面"""
        # 处理长标题
        title_lines = self._split_title(title, max_length=12)
        
        # 选择字体大小
        title_font_size = 28 if len(title) <= 10 else 24 if len(title) <= 20 else 20
        
        svg = f'''<svg width="300" height="400" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:{self._extract_color_from_gradient(gradient, 0)};stop-opacity:1" />
            <stop offset="100%" style="stop-color:{self._extract_color_from_gradient(gradient, 1)};stop-opacity:1" />
        </linearGradient>
        <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="2" dy="2" stdDeviation="3" flood-color="rgba(0,0,0,0.3)"/>
        </filter>
    </defs>
    
    <!-- 背景 -->
    <rect width="300" height="400" fill="url(#bg)" rx="8" ry="8"/>
    
    <!-- 装饰线条 -->
    <line x1="30" y1="60" x2="270" y2="60" stroke="rgba(255,255,255,0.3)" stroke-width="1"/>
    <line x1="30" y1="340" x2="270" y2="340" stroke="rgba(255,255,255,0.3)" stroke-width="1"/>
    
    <!-- 书名 -->
    <text x="150" y="200" text-anchor="middle" fill="white" font-family="serif" font-size="{title_font_size}" font-weight="bold" filter="url(#shadow)">'''
        
        # 添加标题行
        y_offset = 0
        for line in title_lines:
            svg += f'''
        <tspan x="150" dy="{y_offset}">{line}</tspan>'''
            y_offset = 35
        
        svg += '''
    </text>'''
        
        # 添加作者
        if author:
            svg += f'''
    <text x="150" y="280" text-anchor="middle" fill="rgba(255,255,255,0.9)" font-family="sans-serif" font-size="16" filter="url(#shadow)">
        {author}
    </text>'''
        
        # 添加装饰图案
        svg += '''
    <!-- 装饰图案 -->
    <circle cx="150" cy="100" r="20" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="2"/>
    <circle cx="150" cy="100" r="15" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="1"/>
    
</svg>'''
        
        return svg
    
    def _split_title(self, title: str, max_length: int = 12) -> list:
        """将长标题分行"""
        if len(title) <= max_length:
            return [title]
        
        words = title.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + word) <= max_length:
                current_line += word + " "
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        # 限制最多3行
        return lines[:3]
    
    def _extract_color_from_gradient(self, gradient: str, position: int) -> str:
        """从渐变字符串中提取颜色"""
        # 简单的颜色提取，实际实现可能需要更复杂的解析
        colors = ["#667eea", "#764ba2"]  # 默认颜色
        
        if gradient:
            import re
            color_matches = re.findall(r'#[0-9a-fA-F]{6}', gradient)
            if len(color_matches) >= 2:
                colors = color_matches[:2]
        
        return colors[position] if position < len(colors) else colors[0]

# 全局实例
book_cover_searcher = BookCoverSearcher()

async def search_book_cover(title: str, author: str = None, isbn: str = None) -> Dict[str, Any]:
    """便捷函数：搜索书籍封面"""
    return await book_cover_searcher.search_cover(title, author, isbn)