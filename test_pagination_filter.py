"""
测试分页和筛选功能
"""
import asyncio
import httpx
import json

async def test_pagination_and_filter():
    """测试分页和筛选功能"""
    print("🧪 测试分页和筛选功能")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # 1. 测试基本分页
        print("\n1️⃣ 测试基本分页...")
        try:
            response = await client.get(f"{base_url}/api/generated-ppts?limit=3&page=1")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 第1页返回 {len(data.get('ppts', []))} 个PPT")
                if 'pagination' in data:
                    pagination = data['pagination']
                    print(f"   总页数: {pagination.get('total_pages', 'N/A')}")
                    print(f"   总数量: {pagination.get('total_count', 'N/A')}")
                    print(f"   当前页: {pagination.get('current_page', 'N/A')}")
                    print(f"   每页数量: {pagination.get('per_page', 'N/A')}")
                else:
                    print("⚠️ 没有分页信息")
            else:
                print(f"❌ 分页API失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 分页测试错误: {e}")
        
        # 2. 测试分类筛选
        print("\n2️⃣ 测试分类筛选...")
        try:
            response = await client.get(f"{base_url}/api/generated-ppts?category_id=efficiency&limit=5")
            if response.status_code == 200:
                data = response.json()
                ppts = data.get('ppts', [])
                print(f"✅ 效率提升类找到 {len(ppts)} 个PPT")
                for ppt in ppts:
                    print(f"   ⚡ 《{ppt.get('title', 'N/A')}》- {ppt.get('category_name', 'N/A')}")
            else:
                print(f"❌ 分类筛选API失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 分类筛选测试错误: {e}")
        
        # 3. 测试搜索功能
        print("\n3️⃣ 测试搜索功能...")
        try:
            response = await client.get(f"{base_url}/api/generated-ppts?search=时间&limit=5")
            if response.status_code == 200:
                data = response.json()
                ppts = data.get('ppts', [])
                print(f"✅ 搜索'时间'找到 {len(ppts)} 个PPT")
                for ppt in ppts:
                    print(f"   📖 《{ppt.get('title', 'N/A')}》")
            else:
                print(f"❌ 搜索API失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 搜索测试错误: {e}")
        
        # 4. 测试组合筛选
        print("\n4️⃣ 测试组合筛选...")
        try:
            response = await client.get(f"{base_url}/api/generated-ppts?category_id=efficiency&search=管理&limit=3&page=1")
            if response.status_code == 200:
                data = response.json()
                ppts = data.get('ppts', [])
                print(f"✅ 效率提升类 + 搜索'管理'找到 {len(ppts)} 个PPT")
                for ppt in ppts:
                    print(f"   ⚡ 《{ppt.get('title', 'N/A')}》- {ppt.get('category_name', 'N/A')}")
            else:
                print(f"❌ 组合筛选API失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 组合筛选测试错误: {e}")
        
        # 5. 测试分页边界
        print("\n5️⃣ 测试分页边界...")
        try:
            # 测试第2页
            response = await client.get(f"{base_url}/api/generated-ppts?limit=3&page=2")
            if response.status_code == 200:
                data = response.json()
                ppts = data.get('ppts', [])
                print(f"✅ 第2页返回 {len(ppts)} 个PPT")
                if 'pagination' in data:
                    pagination = data['pagination']
                    print(f"   当前页: {pagination.get('current_page', 'N/A')}")
                    print(f"   总页数: {pagination.get('total_pages', 'N/A')}")
            else:
                print(f"❌ 第2页API失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 分页边界测试错误: {e}")
        
        # 6. 测试空结果
        print("\n6️⃣ 测试空结果...")
        try:
            response = await client.get(f"{base_url}/api/generated-ppts?search=不存在的书&limit=5")
            if response.status_code == 200:
                data = response.json()
                ppts = data.get('ppts', [])
                print(f"✅ 搜索'不存在的书'返回 {len(ppts)} 个结果 (应该为0)")
                if len(ppts) == 0:
                    print("✅ 空结果处理正确")
                else:
                    print("⚠️ 空结果处理可能有问题")
            else:
                print(f"❌ 空结果API失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 空结果测试错误: {e}")

if __name__ == "__main__":
    print("⚠️ 请确保服务器已启动 (python appbook.py)")
    print("然后运行此测试脚本...")
    
    # 询问是否继续
    response = input("是否继续测试? (y/n): ")
    if response.lower() == 'y':
        asyncio.run(test_pagination_and_filter())
    else:
        print("测试已取消") 