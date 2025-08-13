import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("httpx").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)

from openai import OpenAI

client = OpenAI(
    base_url='https://api-inference.modelscope.cn/v1/',  # 去掉末尾斜杠，便于路径拼接
    api_key='ms-9ff035d4-50cb-4adf-afe0-89788293e19e', # ModelScope Token
)

response = client.chat.completions.create(
    model='Qwen/Qwen3-Coder-480B-A35B-Instruct', # ModelScope Model-Id
    messages=[
        {
            'role': 'system',
            'content': 'You are a helpful assistant.'
        },
        {
            'role': 'user',
            'content': '你好'
        }
    ],
    stream=True
)

for chunk in response:
    print(chunk.choices[0].delta.content, end='', flush=True)