#!/usr/bin/env python3
"""
测试书籍信息API的脚本
"""
import requests
import json
import urllib.parse

def test_book_info_api():
    """测试书籍信息API"""
    base_url = "http://localhost:8001"  # 根据你的服务器地址调整
    
    # 测试用例
    test_cases = [
        {"title": "乌合之众", "author": None},
        {"title": "乌合之众", "author": "古斯塔夫·勒庞"},
        {"title": "三体", "author": "刘慈欣"},
        {"title": "百年孤独", "author": None},
    ]
    
    print("🔍 开始测试书籍信息API...")
    print(f"📡 服务器地址: {base_url}")
    print("-" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        title = test_case["title"]
        author = test_case["author"]
        
        print(f"\n📚 测试用例 {i}: 《{title}》")
        if author:
            print(f"👤 作者: {author}")
        
        # 构建请求URL
        params = {"title": title}
        if author:
            params["author"] = author
        
        url = f"{base_url}/api/book-info"
        
        try:
            # 发送请求
            response = requests.get(url, params=params, timeout=10)
            
            print(f"🌐 请求URL: {response.url}")
            print(f"📊 状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 响应成功!")
                print("📋 返回数据:")
                print(json.dumps(data, ensure_ascii=False, indent=2))
                
                # 验证关键字段
                required_fields = ["title", "author", "category", "description"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    print(f"⚠️  缺少字段: {missing_fields}")
                else:
                    print("✅ 所有必需字段都存在")
                    
                # 检查作者信息是否正确
                if data.get("author") == "未知作者" and title == "乌合之众":
                    print("❌ 《乌合之众》的作者应该是'古斯塔夫·勒庞'，但返回了'未知作者'")
                elif data.get("author") != "未知作者":
                    print(f"✅ 作者信息正确: {data.get('author')}")
                    
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ 连接失败: 无法连接到服务器")
            print("💡 请确保服务器正在运行在 http://localhost:8001")
            break
        except requests.exceptions.Timeout:
            print("❌ 请求超时")
        except Exception as e:
            print(f"❌ 请求异常: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 测试完成")

def test_direct_function():
    """直接测试函数（如果可以导入的话）"""
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # 尝试直接导入和测试函数
        from appbook import get_book_info
        print("\n🔧 直接函数测试:")
        
        # 这里需要模拟FastAPI的Request对象，比较复杂
        print("💡 直接函数测试需要复杂的模拟环境，建议使用API测试")
        
    except ImportError as e:
        print(f"⚠️  无法导入模块进行直接测试: {e}")

if __name__ == "__main__":
    test_book_info_api()
    test_direct_function()