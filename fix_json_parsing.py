#!/usr/bin/env python3
"""批量修复JSON解析逻辑的脚本"""

import re

# 读取文件内容
with open('/Users/mac/Documents/GitHub/bookagent_baidu/appbook.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 需要修复的JSON解析模式 - 找到return json.loads(result)的模式
template = '''    try:
            return json.loads(result)
        except:
            return [{"raw_content": result}]'''

new_template = '''    try:
            # 尝试直接解析JSON
            return json.loads(result)
        except:
            # 如果直接解析失败，尝试从markdown代码块中提取JSON
            try:
                import re
                json_match = re.search(r'```json\\s*\\n(.*?)\\n```', result, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(1))
                else:
                    # 尝试其他形式的代码块
                    json_match = re.search(r'```\\s*\\n(.*?)\\n```', result, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group(1))
                    else:
                        # 如果都无法解析，返回原始内容
                        return [{"raw_content": result}]
            except:
                # 所有解析方式都失败
                return [{"raw_content": result}]'''

# 替换所有的匹配项（除了第一个book_data的，已经修复过）
# 找到所有匹配项的计数
matches = re.findall(r'        try:\s*\n\s*return json\.loads\(result\)\s*\n\s*except:\s*\n\s*return \[\{.*raw_content.*\}\]', content, re.DOTALL)
print(f"找到 {len(matches)} 个需要修复的JSON解析位置")

# 手动替换第2个和第3个匹配位置（第1个是book_data，已修复）
# Step 2 - 幻灯片生成 (around line 979)
content = content.replace(
    '''        try:
            return json.loads(result)
        except:
            return [{"raw_content": result}]''',
    new_template,
    1  # 只替换第一个出现（即Step 2）
)

# Step 3 - 旁白生成 (around line 1201)
content = content.replace(
    '''        try:
            return json.loads(result)
        except:
            return [{"raw_content": result}]''',
    new_template,
    1  # 只替换第一个出现（即Step 3，现在只剩这一个了）
)

# 写回文件
with open('/Users/mac/Documents/GitHub/bookagent_baidu/appbook.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ JSON解析逻辑修复完成！")