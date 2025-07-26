from dwspark.config import Config
import json
import requests
import re
import os

# 清除可能的环境变量缓存
if 'SPARKAI_APP_ID' in os.environ:
    del os.environ['SPARKAI_APP_ID']
if 'SPARKAI_API_KEY' in os.environ:
    del os.environ['SPARKAI_API_KEY']
if 'SPARKAI_API_SECRET' in os.environ:
    del os.environ['SPARKAI_API_SECRET']

# 加载系统环境变量：SPARKAI_APP_ID、SPARKAI_API_KEY、SPARKAI_API_SECRET
config = Config('c2362e20', '58f2884ea601cb7dd053502547011208','MzUxZjg4Nzg2NTI4NzdhZDQ1ZTQ0NTFl')

# SDK引入模型
from dwspark.models import ChatModel, Text2Img, ImageUnderstanding, Text2Audio, Audio2Text, EmebddingModel
# 讯飞消息对象
from sparkai.core.messages import ChatMessage
# 日志
from loguru import logger

def promptajust(text,style,sign):  #这里用智能体会好一些，加油
        userinput = text + "," + "风格是："+style+ "," + "签名是：" + sign
        
        # 调试信息
        print(f"Config object: {config}")
        print("正在尝试连接讯飞星火API...")
        
        # 优先尝试Spark 4.0 Ultra (最强模型)
        models_to_try = [
            "4.0Ultra",              # 星火4.0 Ultra (最强，对应 wss://spark-api.xf-yun.com/v4.0/chat)
            "generalv3.5",           # 星火3.5 (主流版本)
            "generalv3",             # 星火3.0
            "generalv2",             # 星火2.0
            "general",               # 星火1.5 (基础模型)
            "max70-32k",             # 长文本模型 (32k上下文)
            "generalv3.5-preview",   # 星火3.5预览版
            "zhiwen"                 # 知文模型
        ]
        
        model = None
        for domain in models_to_try:
            try:
                print(f"尝试使用模型域: {domain}")
                model = ChatModel(config, stream=False, domain=domain)
                print(f"✅ 成功连接到模型: {domain}")
                break
            except Exception as e:
                print(f"❌ 模型 {domain} 连接失败: {str(e)[:100]}...")
                continue
        
        if model is None:
            print("⚠️ 所有指定模型都连接失败，尝试默认配置")
            try:
                model = ChatModel(config, stream=False)
                print("✅ 使用默认配置成功")
            except Exception as e:
                print(f"❌ 连接完全失败: {e}")
                raise e
        print(f"模型配置: {model}")
        if hasattr(model, 'model_name'):
            print(f"模型名称: {model.model_name}")
        if hasattr(model, 'domain'):
            print(f"模型域: {model.domain}")
        if hasattr(model, 'spark'):
            print(f"Spark配置: {model.spark}")
            if hasattr(model.spark, 'domain'):
                print(f"Spark域: {model.spark.domain}")
            if hasattr(model.spark, 'model'):
                print(f"Spark模型: {model.spark.model}")
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
        try:
            response = model.generate([ChatMessage(role="user", content=question)])
            print(response)
            return response
        except Exception as e:
            print(f"详细错误信息: {e}")
            print(f"错误类型: {type(e)}")
            if hasattr(e, 'error_code'):
                print(f"错误代码: {e.error_code}")
            if hasattr(e, 'error_desc'):
                print(f"错误描述: {e.error_desc}")
            raise e 

promptajust("向日葵", "梵高风格", "aya")