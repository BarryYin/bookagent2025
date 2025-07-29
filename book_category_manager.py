"""
书籍分类管理器
使用CSV文件统一管理所有书籍的分类信息
"""
import csv
import os
import json
from datetime import datetime
from typing import List, Dict, Optional

class BookCategoryManager:
    def __init__(self, csv_file: str = "books_categories.csv"):
        self.csv_file = csv_file
        self.ensure_csv_exists()
    
    def ensure_csv_exists(self):
        """确保CSV文件存在，如果不存在则创建"""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'title', 'author', 'category_id', 'category_name', 
                    'category_color', 'category_icon', 'created_at', 'ppt_path'
                ])
    
    def add_book(self, title: str, author: str, category_info: Dict, ppt_path: str):
        """添加新书籍到分类数据库"""
        book_data = {
            'title': title,
            'author': author,
            'category_id': category_info.get('category_id', ''),
            'category_name': category_info.get('category_name', ''),
            'category_color': category_info.get('category_color', ''),
            'category_icon': category_info.get('category_icon', ''),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'ppt_path': ppt_path
        }
        
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=book_data.keys())
            writer.writerow(book_data)
        
        print(f"✅ 已添加书籍《{title}》到分类数据库")
    
    def get_all_books(self) -> List[Dict]:
        """获取所有书籍分类信息"""
        books = []
        if os.path.exists(self.csv_file):
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    books.append(row)
        return books
    
    def get_books_by_category(self, category_id: str) -> List[Dict]:
        """根据分类ID获取书籍"""
        all_books = self.get_all_books()
        return [book for book in all_books if book['category_id'] == category_id]
    
    def get_categories_summary(self) -> Dict:
        """获取分类统计信息"""
        books = self.get_all_books()
        categories = {}
        
        for book in books:
            category_id = book['category_id']
            if category_id not in categories:
                categories[category_id] = {
                    'name': book['category_name'],
                    'color': book['category_color'],
                    'icon': book['category_icon'],
                    'count': 0
                }
            categories[category_id]['count'] += 1
        
        return categories
    
    def search_books(self, keyword: str) -> List[Dict]:
        """搜索书籍（按书名或作者）"""
        books = self.get_all_books()
        results = []
        keyword = keyword.lower()
        
        for book in books:
            if (keyword in book['title'].lower() or 
                keyword in book['author'].lower()):
                results.append(book)
        
        return results
    
    def update_existing_books(self):
        """从现有的outputs文件夹更新分类数据库"""
        print("🔄 正在扫描现有PPT并更新分类数据库...")
        
        # 获取所有现有的书籍数据
        existing_books = self.get_all_books()
        existing_titles = {book['title'] for book in existing_books}
        
        # 扫描outputs文件夹
        outputs_dir = "outputs"
        if not os.path.exists(outputs_dir):
            print("❌ outputs文件夹不存在")
            return
        
        updated_count = 0
        for folder in os.listdir(outputs_dir):
            folder_path = os.path.join(outputs_dir, folder)
            if os.path.isdir(folder_path):
                data_file = os.path.join(folder_path, "data.json")
                if os.path.exists(data_file):
                    try:
                        with open(data_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        title = data.get('topic', '')
                        book_data = data.get('book_data', {})
                        
                        # 检查是否已存在
                        if title and title not in existing_titles:
                            # 提取作者信息
                            raw_content = book_data.get('raw_content', '')
                            author = self.extract_author_from_raw(raw_content)
                            
                            # 提取分类信息
                            category_info = {
                                'category_id': book_data.get('category_id', 'literature'),
                                'category_name': book_data.get('category_name', '文学类'),
                                'category_color': book_data.get('category_color', '#E74C3C'),
                                'category_icon': book_data.get('category_icon', '📖')
                            }
                            
                            # 添加到数据库
                            self.add_book(title, author, category_info, folder)
                            updated_count += 1
                            
                    except Exception as e:
                        print(f"❌ 处理 {folder} 时出错: {e}")
        
        print(f"✅ 更新完成，新增 {updated_count} 本书籍")
    
    def extract_author_from_raw(self, raw_content: str) -> str:
        """从原始内容中提取作者信息"""
        try:
            # 尝试从JSON中提取作者
            if '"author"' in raw_content:
                import re
                author_match = re.search(r'"author"\s*:\s*"([^"]+)"', raw_content)
                if author_match:
                    return author_match.group(1)
            
            # 如果无法提取，返回默认值
            return "未知作者"
        except:
            return "未知作者"

# 全局实例
category_manager = BookCategoryManager()

def add_book_to_category(title: str, author: str, category_info: Dict, ppt_path: str):
    """添加书籍到分类数据库的便捷函数"""
    category_manager.add_book(title, author, category_info, ppt_path)

def get_all_books_with_categories() -> List[Dict]:
    """获取所有带分类信息的书籍"""
    return category_manager.get_all_books()

def get_books_by_category_id(category_id: str) -> List[Dict]:
    """根据分类ID获取书籍"""
    return category_manager.get_books_by_category_id(category_id)

def get_categories_summary() -> Dict:
    """获取分类统计信息"""
    return category_manager.get_categories_summary()

def search_books_by_keyword(keyword: str) -> List[Dict]:
    """搜索书籍"""
    return category_manager.search_books(keyword) 