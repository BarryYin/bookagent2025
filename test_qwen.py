from openai import OpenAI

client = OpenAI(
    base_url='https://api-inference.modelscope.cn/v1/',
    api_key='ms-076e7668-1000-4ce8-be4e-f475ddfeead7', # ModelScope Token
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