#!/usr/bin/env python3
"""专门测试Step3旁白生成的百度ERNIE模型调用"""

import asyncio
import json
import re
import os
import sys

# 确保使用当前目录的配置
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from openai import AsyncOpenAI
# 导入appbook中的配置
if __name__ == "__main__":
    # API配置
    BAIDU_API_KEY = "bce-v3/ALTAK-IlAGWrpPIFAMJ3g8kbD4I/f17c0a909b891c89b0dce53d913448d86a87bad9"
    BAIDU_BASE_URL = "https://qianfan.baidubce.com/v2"
    BAIDU_MODEL = "ernie-4.5-turbo-32k"

# 验证标记
FALLBACK_MARKERS = [
    "深受读者喜爱的经典作品",
    "通过生动的故事情节",
    "具有很高的文学价值",
    "让我们先来了解一下",
    "一位值得尊敬的作家"
]

# 模拟appbook.py中的方法定义
METHODOLOGY_STYLES = {
    "dongyu_literature": """## 董宇辉式文学作品解说风格：

### 特色：
- 个人化称呼（"你"）、情感化表达
- 大量古今中外的引用对比
- 深层的文化和价值观探讨
- 哲理性的金句总结

### 语言特征：【温暖、共鸣、引经据典、哲理性】""",

    "dongyu_autobiography": """## 董宇辉式自传体解说风格：

### 特色：
- 第一人称的叙述视角和心路历程
- 通过真实的情感渲染和人生故事引发共鸣
- 深挖事件背后的深层心理学意义与人生哲理
- 金句和总结富含价值观和人生观的升华""",

    "luozhenyu_efficiency": """## 罗振宇式效率提升解说风格：

### 特色：
- 用大量的数据和研究报告支撑观点
- 强调时代背景和竞争压力\强调认知升级的重要性
- 价值观工具化和方法化
- 用紧迫感营造行动动机"""
}

async def test_step3_baidu_narration():
    """验证Step3确实调用了百度ERNIE模型生成旁白"""

    print("🎯 ===== Step3 百度ERNIE旁白生成测试 ===== ")
    print(f"测试目标: 验证是否能成功调用 {BAIDU_MODEL} 生成旁白词")
    print()

    # 模拟输入数据
    slides_data = [
        {
            "slide_number": 1,
            "title": "开场引入 - 金钱启蒙教育",
            "main_content": [
                "《小狗钱钱》通过童话形式传授基础理财知识",
                "一只会说话的小狗钱钱成为理财导师",
                "小女孩吉娅通过设定目标和行动获得成功"
            ],
            "visual_elements": {"background": "温暖的童话风格"}
        },
        {
            "slide_number": 2,
            "title": "核心要义 - 梦想应有具体形式",
            "main_content": [
                "书中的'梦想相册'让抽象目标具像化",
                "明确的目标图片化过程增强实现的动力",
                "吉娅为提高英语水平采取的目标视觉化行动"
            ],
            "visual_elements": {"chart_type": "对比图表"}
        }
    ]

    book_data = {
        "book_title": "小狗钱钱",
        "author": "博多·舍费尔",
        "category_name": "财经投资类",
        "core_summary": "一本通过童话故事教授基础理财和投资观念的儿童读物"
    }

    methodology = "dongyu_literature"

    # 构建Step3的系统提示（来自appbook.py中的内容）
    narration_style = METHODOLOGY_STYLES.get(methodology, "")

    system_prompt = f"""基于以下PPT画面结构和书籍数据，为每页PPT创建指定方法论风格的深度解说词。请生成丰富、有深度的解说内容。

书籍数据：
{json.dumps(book_data, ensure_ascii=False, indent=2)}

PPT画面结构：
{json.dumps(slides_data, ensure_ascii=False, indent=2)}

{narration_style}

每页解说词包含以下详细结构：
- slide_number: 页面编号
- opening: 开场白（2-3句话，体现方法论特色）
- main_narration: 主要解说内容（2-3分钟，必须包含德鲁宇辉式的具体分析和引用）
- key_emphasis: 重点强调的内容（核心观点或金句）
- transition: 过渡语（连接下一页，保持连贯性）
- tone_style: 语调风格和情感色彩

**重要要求：**
1. 必须具体到《小狗钱钱》这本书的内容
2. 严格按照"董宇辉式"的表达风格要求
3. 结合PPT的具体内容进行解说
4. main_narration要包含具体的例子和深入分析
5. 语言要体现温暖、共鸣、引经据典、哲理性风格
6. 每段解说要能支撑2-3分钟的讲解
7. 不能只是笼统地介绍

请以JSON数组格式返回（严格JSON），确保每页解说都完全符合董宇辉风格。
"""

    try:
        # 创建客户端
        print("🤖 初始化百度ERNIE客户端...")
        client = AsyncOpenAI(api_key=BAIDU_API_KEY, base_url=BAIDU_BASE_URL)

        # 直接调用API（模拟实际的Step3过程）
        print(f"\n📡 调用百度ERNIE模型: {BAIDU_MODEL}")
        print("💬 系统提示长度:", len(system_prompt))

        start_time = asyncio.get_event_loop().time()

        response = await client.chat.completions.create(
            model=BAIDU_MODEL,
            messages=[{"role": "user", "content": system_prompt}],
            temperature=0.8,
            max_tokens=2000
        )

        elapsed = asyncio.get_event_loop().time() - start_time

        # 获取响应
        result = response.choices[0].message.content

        print("\n" + "="*60)
        print(f"✅ API调用成功!")
        print(f"📊 响应时间: {elapsed:.2f}秒")
        print(f"📄 总长度: {len(result)}字符")
        print(f"🆔 响应ID: {response.id}")
        print(f"🤖 使用的模型: {response.model}")
        print(f"💰 令牌统计: {response.usage}")
        print("="*60)

        # 验证内容质量
        print("\n🔍 内容验证:")

        # 检查是否是备用模板内容
        has_fallback = any(marker in result for marker in FALLBACK_MARKERS)
        if has_fallback:
            print("⚠️ 警告: 包含备用模板内容关键词")
        else:
            print("✅ 内容看起来是动态生成的")

        # 检查是否包含具体细节
        specific_terms = ["博多", "舍费尔", "梦想相册", "钱钱", "储蓄罐", "理财启蒙"]
        found_terms = [term for term in specific_terms if term in result]
        print(f"✅ 找到 {len(found_terms)} 个《小狗钱钱》独有元素: {found_terms}")

        # 检查董宇辉风格特征
        style_features = {
            "第一人称": "你" in result or "我们" in result,
            "情感化": any(word in result for word in ["温暖", "感动", "共鸣"]),
            "古典引用": any(text in result for text in ["《论语》", "孟子", "老子"]) or any(text in result for text in ["牵牛织女", "诗经", "论语"]),
            "故事引用": "故事" in result,
            "哲理表达": any(phrase in result for phrase in ["正如", "古人", "智慧", "人生"])
        }

        print("\n🎨 风格验证:")
        for feature, found in style_features.items():
            status = "✅" if found else "❌"
            print(f"   {status} {feature}")

        # 输出响应样本
        print(f"\n📝 响应样本（前400字符）:\n{result[:400]}...")

        # 尝试JSON解析
        try:
            if "```json" in result:
                json_match = re.search(r'```json\s*\n(.*?)\n```', result, re.DOTALL, re.DOTALL)
                if json_match:
                    narrations = json.loads(json_match.group(1))
                else:
                    json_match = re.search(r'\[(.*?)\]', result, re.DOTALL)
                    narrations = json.loads('[' + json_match.group(1) + ']')
            else:
                # 尝试从数组括号匹配
                narrations = json.loads(result)

            print(f"\n✅ JSON解析成功!")
            print(f"📊 旁白数量: {len(narrations)}")

            # 详细展示每个旁白
            for i, narration in enumerate(narrations[:2], 1):
                print(f"\n🎬 第{i}页旁白:")
                print(f"   开场: {narration.get('opening', '无')[:60]}...")
                print(f"   长度: {len(narration.get('main_narration', ''))}字符")
                print(f"   风格: {narration.get('tone_style', '未标明')}")

        except Exception as e:
            print(f"⚠️ JSON解析失败: {e}")
            print("原始响应格式:", result[:200])

        print("\n" + "="*60)
        print("🎉 测试结论:")

        # 评估结论
        api_success = len(found_terms) >= 2
        quality_score = sum(style_features.values()) / len(style_features)

        if api_success and quality_score >= 0.5:
            print("✅ SUCCESS: 百度ERNIE模型调用成功，生成了个性化的旁白内容")
        elif not api_success:
            print("❌ FAILED: 生成的内容可能过于通用，缺乏个性化特征")
        else:
            print("⚠️ PARTIAL: 调用成功但风格特征不明显")

    except Exception as e:
        print("\n" + "="*60)
        print("❌ 测试失败")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误详情: {str(e)}")

        # 常见错误类型分析
        error_info = str(e)
        if "401" in error_info or "invalid_model" in error_info:
            print("\n🔍 错误分析:")
            print("   1. API Key 可能已过期或权限不足")
            print("   2. 模型名称可能存在拼写错误")
            print("   3. 需要检查百度千帆平台的模型开通状态")
            print("   4. 可能需要切换到其他可用模型")

            print("\n🔨 建议解决方案:")
            print("   a) 登录 https://console.bce.baidu.com/ 查看API状态")
            print("   b) 尝试使用'ernie-4.5'替代'ernie-4.5-turbo-32k'")
            print("   c) 检查API Key是否有调用权限")

if __name__ == "__main__":
    asyncio.run(test_step3_baidu_narration())