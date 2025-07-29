"""
测试首页的多样化显示功能
"""
import asyncio
import httpx
import json

async def test_diverse_display():
    """测试首页的多样化显示"""
    print("🧪 测试首页多样化显示功能")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # 1. 获取API数据
        print("\n1️⃣ 获取API数据...")
        try:
            response = await client.get(f"{base_url}/api/generated-ppts?limit=20")
            if response.status_code == 200:
                data = response.json()
                ppts = data.get('ppts', [])
                print(f"✅ API返回 {len(ppts)} 个PPT")
                
                # 2. 检查分类分布
                print("\n2️⃣ 检查分类分布...")
                categories = {}
                for ppt in ppts:
                    category = ppt.get('category_name', '未知')
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(ppt['title'])
                
                for category, titles in categories.items():
                    print(f"  📚 {category}: {len(titles)} 个")
                    for title in titles[:3]:  # 显示前3个
                        print(f"    - {title}")
                
                # 3. 模拟多样化选择
                print("\n3️⃣ 模拟多样化选择...")
                diverse_ppts = select_diverse_ppts(ppts, 3)
                
                print("选择的多样化PPT:")
                for i, ppt in enumerate(diverse_ppts):
                    print(f"  {i+1}. 《{ppt['title']}》- {ppt['category_name']}")
                
                # 4. 检查是否有其他分类
                other_categories = [cat for cat in categories.keys() if cat != '文学类']
                if other_categories:
                    print(f"\n✅ 发现其他分类: {', '.join(other_categories)}")
                else:
                    print(f"\n⚠️ 只有文学类，需要更多样化的内容")
                
            else:
                print(f"❌ API失败: {response.status_code}")
        except Exception as e:
            print(f"❌ API错误: {e}")

def select_diverse_ppts(ppts, count):
    """选择多样化的PPT"""
    if len(ppts) <= count:
        return ppts
    
    # 按分类分组
    categories = {}
    for ppt in ppts:
        category = ppt.get('category_name', '文学类')
        if category not in categories:
            categories[category] = []
        categories[category].append(ppt)
    
    # 从每个分类中选择一个，优先选择最新的
    selected = []
    category_names = list(categories.keys())
    
    # 先选择不同分类的PPT
    for i in range(min(len(category_names), count)):
        category = category_names[i]
        if categories[category]:
            selected.append(categories[category][0])  # 选择最新的
    
    # 如果还不够，从剩余中选择最新的
    if len(selected) < count:
        remaining = [ppt for ppt in ppts if ppt not in selected]
        selected.extend(remaining[:count - len(selected)])
    
    return selected[:count]

if __name__ == "__main__":
    print("⚠️ 请确保服务器已启动 (python appbook.py)")
    print("然后运行此测试脚本...")
    
    # 询问是否继续
    response = input("是否继续测试? (y/n): ")
    if response.lower() == 'y':
        asyncio.run(test_diverse_display())
    else:
        print("测试已取消") 