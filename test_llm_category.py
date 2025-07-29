"""
测试LLM分类功能
"""
import asyncio
from appbook import step1_extract_book_data

async def test_llm_category():
    """测试LLM分类功能"""
    print("🧠 测试LLM分类功能")
    print("=" * 50)
    
    # 测试书籍列表
    test_books = [
        "活着",
        "时间管理大师", 
        "三体",
        "乔布斯传",
        "高等数学"
    ]
    
    for i, book_title in enumerate(test_books, 1):
        print(f"\n{i}. 测试书籍: 《{book_title}》")
        print("-" * 30)
        
        try:
            # 调用step1函数
            book_data = await step1_extract_book_data(book_title)
            
            # 显示分类结果
            print(f"📚 书名: {book_data.get('book_title', book_title)}")
            print(f"✍️  作者: {book_data.get('author', '未知')}")
            print(f"🏷️  分类: {book_data.get('category_name', '未知')}")
            print(f"🎨 颜色: {book_data.get('category_color', '#4A90E2')}")
            print(f"📌 图标: {book_data.get('category_icon', '📚')}")
            print(f"📊 置信度: {book_data.get('category_confidence', 0):.1f}")
            
            # 显示描述
            description = book_data.get('description', '')
            if description:
                print(f"📝 描述: {description[:100]}...")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_llm_category()) 