from dwspark.config import Config
import json
import requests
import re
 
 # 加载系统环境变量：SPARKAI_APP_ID、SPARKAI_API_KEY、SPARKAI_API_SECRET
config = Config('3a115b20', '9d1b7a738c3e63a79656df4222d12cef','ZGMyMzA3MGFlM2MzM2UxZWE1YTJhYjgw')

# SDK引入模型
from dwspark.models import ChatModel, Text2Img, ImageUnderstanding, Text2Audio, Audio2Text, EmebddingModel
# 讯飞消息对象
from sparkai.core.messages import ChatMessage
# 日志
from loguru import logger

def promptajust(text,style,sign):  #这里用智能体会好一些，加油
        userinput = text + "," + "风格是："+style+ "," + "签名是：" + sign
        model = ChatModel(config, stream=False)
        question=f'''
                    flux是一个AI艺术生成工具，它的prompt规则通常遵循一些基本的指导原则，以确保生成的艺术作品符合用户的期望。以下是一些编写Flux prompt时应该考虑的要点：

主题描述：明确地描述您想要AI创作的主题，比如“向日葵”。

细节特征：提供关于作品细节的具体描述，如花瓣的形态、颜色的深浅、光线的运用等。

风格指定：指出您希望作品模仿的艺术风格或艺术家，例如“梵高风格”。

媒介和技法：说明作品的创作媒介，如“油画”，以及使用的技法，比如“厚涂法”。

构图方式：描述作品的构图，比如“近距离特写”或“全身像”。

情感氛围：传达您希望作品表达的情感，如“充满希望和活力”。

技术参数：如果适用，可以指定渲染技术，如“Flux AI渲染”。

分辨率和质量：对于数字作品，可以指定分辨率，但对于油画等传统媒介，可以强调作品的质量，如“适合艺术打印的高质量”。

连续性：如果prompt需要继续扩展，保持描述的连贯性和一致性。

简洁性：尽管详细很重要，但也要避免过度复杂化，使prompt易于理解和执行。

举例：

Paint a Van Gogh-inspired 'Sunflowers' oil piece: a close-up composition of vibrant yellow sunflowers in a rustic vase, with deep green leaves. Emulate Van Gogh's thick, expressive brushstrokes and rich color palette. Convey the hopeful vitality of the original. Use Flux AI for a high-resolution, fine art-quality rendering.

一个好的prompt在500字以内，包含了艺术作品的关键元素和风格要求，同时指定了使用Flux AI进行高分辨率渲染。且是英文的。

请将下面的内容描述成flux的prompt，符合要求，且是英文。

"+ {userinput}
                    '''
        response = model.generate([ChatMessage(role="user", content=question)])
        print(response)
        return response 

promptajust("向日葵", "梵高风格", "aya")