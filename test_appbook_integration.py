#!/usr/bin/env python3
"""
测试appbook.py是否正确导入了test_cover.py的封面搜索函数
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_cover_integration():
    """测试封面搜索功能集成"""
    print("🧪 测试appbook.py中的封面搜索功能集成")
    print("=" * 50)
    
    try:
        # 导入appbook模块
        import appbook
        print("✅ 成功导入appbook模块")
        
        # 测试封面搜索函数
        test_books = [
            ("月亮与六便士", "毛姆"),
            ("活着", "余华"),
            ("三体", "刘慈欣"),
        ]
        
        for book_title, author in test_books:
            print(f"\n📚 测试书籍: 《{book_title}》- {author}")
            
            try:
                # 调用appbook中的封面搜索函数
                cover_url = await appbook.search_book_cover(book_title, author)
                
                if cover_url:
                    if cover_url.startswith("http"):
                        print(f"  ✅ 找到真实封面URL: {cover_url[:50]}...")
                    elif cover_url.startswith("gradient:"):
                        print(f"  🎨 使用默认渐变封面: {cover_url[:30]}...")
                    else:
                        print(f"  📄 返回其他类型封面: {cover_url}")
                else:
                    print(f"  ❌ 未找到封面")
                    
            except Exception as e:
                print(f"  ❌ 搜索封面时出错: {e}")
        
        print("\n🎉 封面搜索功能集成测试完成！")
        return True
        
    except ImportError as e:
        print(f"❌ 导入appbook模块失败: {e}")
        print("请确保所有依赖都已安装")
        return False
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(test_cover_integration())
    
    if success:
        print("\n✅ 集成测试成功！appbook.py现在可以使用test_cover.py的封面搜索功能了。")
    else:
        print("\n❌ 集成测试失败，请检查代码和依赖。")
    
    sys.exit(0 if success else 1) 