"""
测试分类管理器功能
"""
from book_category_manager import category_manager

def test_category_manager():
    """测试分类管理器的各项功能"""
    print("🧪 测试分类管理器功能")
    print("=" * 50)
    
    # 1. 更新现有书籍到分类数据库
    print("\n1️⃣ 更新现有书籍到分类数据库...")
    category_manager.update_existing_books()
    
    # 2. 查看所有书籍
    print("\n2️⃣ 查看所有书籍分类信息...")
    all_books = category_manager.get_all_books()
    print(f"📚 总共有 {len(all_books)} 本书籍:")
    for book in all_books:
        print(f"   📖 《{book['title']}》- {book['author']} | {book['category_name']} {book['category_icon']}")
    
    # 3. 查看分类统计
    print("\n3️⃣ 分类统计信息...")
    categories = category_manager.get_categories_summary()
    for category_id, info in categories.items():
        print(f"   {info['icon']} {info['name']}: {info['count']} 本")
    
    # 4. 按分类筛选
    print("\n4️⃣ 按分类筛选书籍...")
    efficiency_books = category_manager.get_books_by_category('efficiency')
    print(f"⚡ 效率提升类书籍 ({len(efficiency_books)} 本):")
    for book in efficiency_books:
        print(f"   📖 《{book['title']}》- {book['author']}")
    
    # 5. 搜索功能
    print("\n5️⃣ 搜索功能测试...")
    search_results = category_manager.search_books("时间")
    print(f"🔍 搜索'时间'的结果 ({len(search_results)} 本):")
    for book in search_results:
        print(f"   📖 《{book['title']}》- {book['author']} | {book['category_name']}")
    
    # 6. 显示CSV文件内容
    print("\n6️⃣ CSV文件内容预览...")
    try:
        with open('books_categories.csv', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print("📄 CSV文件前5行:")
            for i, line in enumerate(lines[:5]):
                print(f"   {i+1}: {line.strip()}")
    except FileNotFoundError:
        print("❌ CSV文件不存在")

if __name__ == "__main__":
    test_category_manager() 