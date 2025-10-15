#!/usr/bin/env python3
import json

def extract_json_from_response(raw_content: str):
    """从LLM响应中提取JSON数据"""
    import re

    # 尝试从Markdown代码块中提取
    json_match = re.search(r'```json\s*\n(.*?)\n```', raw_content, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # 尝试从纯文本中提取
    try:
        return json.loads(raw_content)
    except json.JSONDecodeError:
        pass

    # 如果都失败，返回原始内容
    return {"raw_content": raw_content}

# 测试百度ERNIE模型返回的内容
test_response = '''```json
{
    "书名和作者": {
        "书名": "《小狗钱钱》",
        "作者": "博多·舍费尔（Bodo Schäfer）"
    },
    "主要内容概述": [
        "《小狗钱钱》是一部面向青少年及初学者的理财启蒙读物"
    ]
}
```'''

print("解析前内容长度:", len(test_response))
print("解析前内容预览:", test_response[:50])

result = extract_json_from_response(test_response)
print("\n解析后结果:", result)

# 如果是字典且true_json_data存在，使用它
if isinstance(result, dict):
    true_json = result.get('true_json_data', result)
    print("\n提取的JSON数据:", true_json)