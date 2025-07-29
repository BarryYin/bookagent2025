"""
简单的前端功能测试
"""
import asyncio
import httpx
import json

async def test_frontend():
    """测试前端功能"""
    print("🧪 测试前端功能")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # 1. 测试API
        print("\n1️⃣ 测试API...")
        try:
            response = await client.get(f"{base_url}/api/generated-ppts?limit=3")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API正常，返回 {len(data.get('ppts', []))} 个PPT")
                for ppt in data.get('ppts', []):
                    print(f"   📖 《{ppt.get('title', 'N/A')}》- {ppt.get('category_name', 'N/A')}")
            else:
                print(f"❌ API失败: {response.status_code}")
        except Exception as e:
            print(f"❌ API错误: {e}")
        
        # 2. 测试首页
        print("\n2️⃣ 测试首页...")
        try:
            response = await client.get(f"{base_url}/")
            if response.status_code == 200:
                html = response.text
                if "ppt-showcase-grid" in html:
                    print("✅ 首页包含PPT展示区域")
                else:
                    print("❌ 首页缺少PPT展示区域")
                
                if "script.js" in html:
                    print("✅ 首页加载了script.js")
                else:
                    print("❌ 首页没有加载script.js")
            else:
                print(f"❌ 首页访问失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 首页错误: {e}")
        
        # 3. 测试图书馆页面
        print("\n3️⃣ 测试图书馆页面...")
        try:
            response = await client.get(f"{base_url}/library")
            if response.status_code == 200:
                html = response.text
                if "ppt-library-grid" in html:
                    print("✅ 图书馆页面包含PPT网格")
                else:
                    print("❌ 图书馆页面缺少PPT网格")
                
                if "library-filters" in html:
                    print("✅ 图书馆页面包含筛选功能")
                else:
                    print("❌ 图书馆页面缺少筛选功能")
            else:
                print(f"❌ 图书馆页面访问失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 图书馆页面错误: {e}")

if __name__ == "__main__":
    print("⚠️ 请确保服务器已启动 (python appbook.py)")
    print("然后运行此测试脚本...")
    
    # 询问是否继续
    response = input("是否继续测试? (y/n): ")
    if response.lower() == 'y':
        asyncio.run(test_frontend())
    else:
        print("测试已取消") 