# 请安装 OpenAI SDK : pip install openai
# apiKey 获取地址： https://console.bce.baidu.com/iam/#/iam/apikey/list
# 支持的模型列表： https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Fm2vrveyu

from openai import OpenAI
client = OpenAI(
    base_url='https://qianfan.baidubce.com/v2',
    api_key='bce-v3/ALTAK-IlAGWrpPIFAMJ3g8kbD4I/f17c0a909b891c89b0dce53d913448d86a87bad9'
)
response = client.chat.completions.create(
    model="ernie-4.5-turbo-32k", 
    messages=[
        {
            "role": "system",
            "content": "你是一个助手，请回答我的问题"
        }    
    ,
    {
        "role": "user",
        "content": "你好，你是谁啊"
    },
    {
        "role": "assistant",
        "content": "我是百度公司研发的知识增强大语言模型，我的中文名是文心一言，英文名是ERNIE Bot。我可以完成知识问答、文本创作、知识推理、数学计算、代码理解与编写、作画、翻译等任务，有什么需要我帮忙的吗？"
    },
     {
        "role": "user",
        "content": "你能做什么"
    },
], 
    temperature=0.8, 
    top_p=0.8,
    extra_body={ 
        "penalty_score":1, 
        "stop":[], 
        "web_search":{
    "enable": False,
    "enable_trace": False
}
    }
)
print(response)

#ChatCompletion(id='as-6dw517ncq0', choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='我能做的事情可不少呢！比如：\n\n1. **回答问题**：无论是科学知识、历史事件，还是生活小窍门，我都能帮你找到答案。\n2. **文本创作**：写故事、写诗歌、写文案，甚至帮你构思文章大纲，我都能胜任。\n3. **知识推理**：对于一些需要逻辑推理的问题，比如数学题、逻辑谜题，我也能帮你分析解答。\n4. **代码理解与编写**：无论是解释代码段的意思，还是帮你编写简单的程序，我都能做到。\n5. **翻译**：中英文互译对我来说轻而易举，其他语种我也能尝试哦。\n6. **作画描述**：虽然我不能直接画画，但我可以描述出画面的内容，帮你激发创作灵感。\n\n怎么样，是不是觉得我很厉害呢？有什么需要我帮忙的，尽管告诉我哦！', refusal=None, role='assistant', annotations=None, audio=None, function_call=None, tool_calls=None), flag=0)], created=1760428035, model='ernie-4.5-turbo-32k', object='chat.completion', service_tier=None, system_fingerprint=None, usage=CompletionUsage(completion_tokens=168, prompt_tokens=61, total_tokens=229, completion_tokens_details=None, prompt_tokens_details=None))