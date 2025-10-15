import base64
from openai import OpenAI

# 读取图片并转换为base64
with open('/Users/mac/Documents/GitHub/bookagent_baidu/book1.jpeg', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

client = OpenAI(
    base_url='https://qianfan.baidubce.com/v2',
    api_key='bce-v3/ALTAK-IlAGWrpPIFAMJ3g8kbD4I/f17c0a909b891c89b0dce53d913448d86a87bad9'
)

response = client.chat.completions.create(
    model="ernie-4.5-turbo-vl-latest", 
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}"
                    }
                },
                {
                    "type": "text",
                    "text": "请识别这张书籍封面图片中的书名和作者信息"
                }
            ]
        }
    ], 
    temperature=0.2, 
    top_p=0.8
)
print(response.choices[0].message.content)