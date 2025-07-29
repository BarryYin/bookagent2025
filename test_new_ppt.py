"""
测试生成新PPT并验证分类功能
"""
import asyncio
import json
from appbook import step1_extract_book_data, step2_create_ppt_slides, step3_create_narration, step4_generate_html, save_generated_content
import uuid

async def test_new_ppt_with_category():
    """测试生成新PPT并验证分类功能"""
    print("🧪 测试生成新PPT并验证分类功能")
    print("=" * 60)
    
    # 测试书籍
    test_book = "时间管理大师"
    
    try:
        print(f"📖 开始处理书籍: 《{test_book}》")
        
        # Step 1: 提取书籍数据（包含分类）
        print("\n1️⃣ Step 1: 提取书籍数据...")
        book_data = await step1_extract_book_data(test_book)
        
        # 显示分类结果
        print(f"\n📚 分类结果:")
        print(f"   分类ID: {book_data.get('category_id', 'N/A')}")
        print(f"   分类名称: {book_data.get('category_name', 'N/A')}")
        print(f"   分类颜色: {book_data.get('category_color', 'N/A')}")
        print(f"   分类图标: {book_data.get('category_icon', 'N/A')}")
        print(f"   置信度: {book_data.get('category_confidence', 0):.1f}")
        
        # Step 2: 创建PPT幻灯片
        print("\n2️⃣ Step 2: 创建PPT幻灯片...")
        slides = await step2_create_ppt_slides(book_data)
        
        # Step 3: 创建演讲稿
        print("\n3️⃣ Step 3: 创建演讲稿...")
        narrations = await step3_create_narration(slides, book_data)
        
        # Step 4: 生成HTML
        print("\n4️⃣ Step 4: 生成HTML...")
        html_content = await step4_generate_html(slides, narrations, book_data)
        
        # 保存内容
        session_id = str(uuid.uuid4())
        content = {
            "topic": test_book,
            "book_data": book_data,
            "slides": slides,
            "narrations": narrations,
            "html_content": html_content
        }
        
        await save_generated_content(session_id, content)
        
        print(f"\n✅ 生成完成!")
        print(f"   Session ID: {session_id}")
        print(f"   分类: {book_data.get('category_name', '未知')}")
        print(f"   文件位置: outputs/{session_id}/")
        
        # 验证数据文件中的分类信息
        import os
        data_file = f"outputs/{session_id}/data.json"
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
                saved_book_data = saved_data.get('book_data', {})
                print(f"\n📋 保存的数据验证:")
                print(f"   分类ID: {saved_book_data.get('category_id', 'N/A')}")
                print(f"   分类名称: {saved_book_data.get('category_name', 'N/A')}")
                print(f"   分类颜色: {saved_book_data.get('category_color', 'N/A')}")
                print(f"   分类图标: {saved_book_data.get('category_icon', 'N/A')}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_new_ppt_with_category()) 