"""
测试分类API功能
"""
import asyncio
import httpx
import json

async def test_category_api():
    """测试分类API的各项功能"""
    print("🧪 测试分类API功能")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # 1. 测试获取分类统计
        print("\n1️⃣ 测试获取分类统计...")
        try:
            response = await client.get(f"{base_url}/api/categories")
            if response.status_code == 200:
                data = response.json()
                print("✅ 分类统计API正常")
                categories = data.get('categories', {})
                for category_id, info in categories.items():
                    print(f"   {info['icon']} {info['name']}: {info['count']} 本")
            else:
                print(f"❌ 分类统计API失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 分类统计API错误: {e}")
        
        # 2. 测试获取所有书籍
        print("\n2️⃣ 测试获取所有书籍...")
        try:
            response = await client.get(f"{base_url}/api/books")
            if response.status_code == 200:
                data = response.json()
                books = data.get('books', [])
                print(f"✅ 获取所有书籍API正常，共 {len(books)} 本")
                for book in books[:5]:  # 只显示前5本
                    print(f"   📖 《{book['title']}》- {book['author']} | {book['category_name']}")
            else:
                print(f"❌ 获取所有书籍API失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 获取所有书籍API错误: {e}")
        
        # 3. 测试按分类筛选
        print("\n3️⃣ 测试按分类筛选...")
        try:
            response = await client.get(f"{base_url}/api/books?category_id=efficiency")
            if response.status_code == 200:
                data = response.json()
                books = data.get('books', [])
                print(f"✅ 效率提升类书籍筛选正常，共 {len(books)} 本")
                for book in books:
                    print(f"   ⚡ 《{book['title']}》- {book['author']}")
            else:
                print(f"❌ 按分类筛选API失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 按分类筛选API错误: {e}")
        
        # 4. 测试搜索功能
        print("\n4️⃣ 测试搜索功能...")
        try:
            response = await client.get(f"{base_url}/api/books?search=时间")
            if response.status_code == 200:
                data = response.json()
                books = data.get('books', [])
                print(f"✅ 搜索功能正常，找到 {len(books)} 本相关书籍")
                for book in books:
                    print(f"   🔍 《{book['title']}》- {book['author']} | {book['category_name']}")
            else:
                print(f"❌ 搜索API失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 搜索API错误: {e}")
        
        # 5. 测试直接分类端点
        print("\n5️⃣ 测试直接分类端点...")
        try:
            response = await client.get(f"{base_url}/api/categories/efficiency/books")
            if response.status_code == 200:
                data = response.json()
                books = data.get('books', [])
                print(f"✅ 直接分类端点正常，效率提升类共 {len(books)} 本")
                for book in books:
                    print(f"   ⚡ 《{book['title']}》- {book['author']}")
            else:
                print(f"❌ 直接分类端点失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 直接分类端点错误: {e}")

if __name__ == "__main__":
    print("⚠️ 请确保服务器已启动 (python appbook.py)")
    print("然后运行此测试脚本...")
    
    # 询问是否继续
    response = input("是否继续测试? (y/n): ")
    if response.lower() == 'y':
        asyncio.run(test_category_api())
    else:
        print("测试已取消") 