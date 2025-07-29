"""
测试前端分类显示功能
"""
import asyncio
import httpx
import json

async def test_frontend_category_display():
    """测试前端分类显示功能"""
    print("🧪 测试前端分类显示功能")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # 1. 测试API返回分类信息
        print("\n1️⃣ 测试API返回分类信息...")
        try:
            response = await client.get(f"{base_url}/api/generated-ppts?limit=5")
            if response.status_code == 200:
                data = response.json()
                ppts = data.get('ppts', [])
                print(f"✅ API返回 {len(ppts)} 个PPT")
                
                for i, ppt in enumerate(ppts):
                    print(f"   📖 《{ppt.get('title', 'N/A')}》")
                    print(f"      📅 创建时间: {ppt.get('created_time', 'N/A')}")
                    print(f"      🏷️ 分类: {ppt.get('category_name', 'N/A')} {ppt.get('category_icon', '')}")
                    print(f"      🎨 颜色: {ppt.get('category_color', 'N/A')}")
                    print(f"      🔗 链接: {ppt.get('html_path', 'N/A')}")
                    if i < len(ppts) - 1:
                        print()
            else:
                print(f"❌ API请求失败: {response.status_code}")
        except Exception as e:
            print(f"❌ API测试错误: {e}")
        
        # 2. 测试分类统计API
        print("\n2️⃣ 测试分类统计API...")
        try:
            response = await client.get(f"{base_url}/api/categories")
            if response.status_code == 200:
                data = response.json()
                categories = data.get('categories', {})
                print("✅ 分类统计:")
                for category_id, info in categories.items():
                    print(f"   {info['icon']} {info['name']}: {info['count']} 本")
            else:
                print(f"❌ 分类统计API失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 分类统计API错误: {e}")
        
        # 3. 测试按分类筛选
        print("\n3️⃣ 测试按分类筛选...")
        try:
            response = await client.get(f"{base_url}/api/books?category_id=efficiency")
            if response.status_code == 200:
                data = response.json()
                books = data.get('books', [])
                print(f"✅ 效率提升类书籍 ({len(books)} 本):")
                for book in books:
                    print(f"   ⚡ 《{book.get('title', 'N/A')}》- {book.get('author', 'N/A')}")
            else:
                print(f"❌ 分类筛选API失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 分类筛选API错误: {e}")
        
        # 4. 检查前端页面
        print("\n4️⃣ 检查前端页面...")
        try:
            # 检查首页
            response = await client.get(f"{base_url}/")
            if response.status_code == 200:
                print("✅ 首页可访问")
                # 检查是否包含分类相关的CSS类
                content = response.text
                if "category-badge" in content or "showcase-ppt-card" in content:
                    print("✅ 首页包含分类相关元素")
                else:
                    print("⚠️ 首页可能不包含分类元素")
            else:
                print(f"❌ 首页访问失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 首页检查错误: {e}")
        
        # 5. 检查图书馆页面
        print("\n5️⃣ 检查图书馆页面...")
        try:
            response = await client.get(f"{base_url}/library")
            if response.status_code == 200:
                print("✅ 图书馆页面可访问")
                content = response.text
                if "ppt-card" in content or "library-ppt-card" in content:
                    print("✅ 图书馆页面包含PPT卡片元素")
                else:
                    print("⚠️ 图书馆页面可能不包含PPT卡片元素")
            else:
                print(f"❌ 图书馆页面访问失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 图书馆页面检查错误: {e}")

if __name__ == "__main__":
    print("⚠️ 请确保服务器已启动 (python appbook.py)")
    print("然后运行此测试脚本...")
    
    # 询问是否继续
    response = input("是否继续测试? (y/n): ")
    if response.lower() == 'y':
        asyncio.run(test_frontend_category_display())
    else:
        print("测试已取消") 