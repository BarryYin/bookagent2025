#!/usr/bin/env python3
"""
测试Qwen模型在appbook.py中的集成
"""

import asyncio
import json
from openai import AsyncOpenAI

# 配置Qwen模型客户端
QWEN_BASE_URL = "https://api-inference.modelscope.cn/v1/"
QWEN_API_KEY = "ms-076e7668-1000-4ce8-be4e-f475ddfeead7"  # ModelScope Token
QWEN_MODEL = "Qwen/Qwen3-Coder-480B-A35B-Instruct"

async def test_qwen_model():
    """测试Qwen模型的基本功能"""
    print("🧪 开始测试Qwen模型集成...")
    
    # 创建客户端
    client = AsyncOpenAI(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL)
    
    try:
        # 测试简单的对话
        response = await client.chat.completions.create(
            model=QWEN_MODEL,
            messages=[
                {"role": "system", "content": "你是一个有用的助手。"},
                {"role": "user", "content": "请简单介绍一下你自己。"}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        result = response.choices[0].message.content
        print(f"✅ Qwen模型响应成功:")
        print(f"📝 响应内容: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Qwen模型测试失败: {e}")
        return False

async def test_book_analysis():
    """测试书籍分析功能（模拟appbook.py中的step1）"""
    print("\n📚 测试书籍分析功能...")
    
    client = AsyncOpenAI(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL)
    
    system_prompt = """请分析以下书籍的基本信息，并以JSON格式返回：

书籍：《活着》

请提供以下信息：
1. 书名
2. 作者
3. 书籍简介（100字以内）
4. 核心观点（3-5个要点）
5. 目标读者群体
6. 书籍的价值和意义
7. 适合制作PPT的关键章节或主题（5-8个）

请以JSON格式返回结果。
"""

    try:
        response = await client.chat.completions.create(
            model=QWEN_MODEL,
            messages=[{"role": "user", "content": system_prompt}],
            temperature=0.7
        )
        
        result = response.choices[0].message.content
        print(f"✅ 书籍分析成功:")
        print(f"📝 分析结果: {result}")
        
        # 尝试解析JSON
        try:
            book_data = json.loads(result)
            print(f"✅ JSON解析成功，包含 {len(book_data)} 个字段")
        except:
            print("⚠️ JSON解析失败，但响应内容正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 书籍分析测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 开始Qwen模型集成测试")
    print("=" * 50)
    
    # 测试1: 基本模型功能
    test1_result = await test_qwen_model()
    
    # 测试2: 书籍分析功能
    test2_result = await test_book_analysis()
    
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    print(f"✅ 基本模型功能: {'通过' if test1_result else '失败'}")
    print(f"✅ 书籍分析功能: {'通过' if test2_result else '失败'}")
    
    if test1_result and test2_result:
        print("\n🎉 所有测试通过！Qwen模型集成成功！")
    else:
        print("\n⚠️ 部分测试失败，请检查配置。")

if __name__ == "__main__":
    asyncio.run(main()) 