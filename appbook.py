import asyncio
import json
from datetime import datetime
from typing import AsyncGenerator, List, Optional

import pytz
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI, OpenAIError
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from google import genai

# -----------------------------------------------------------------------
# 0. 配置
# -----------------------------------------------------------------------
shanghai_tz = pytz.timezone("Asia/Shanghai")

credentials = json.load(open("credentials.json"))
API_KEY = credentials["API_KEY"]
BASE_URL = credentials.get("BASE_URL", "")

if API_KEY.startswith("sk-"):
    client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)
    USE_GEMINI = False
else:
    import os
    os.environ["GEMINI_API_KEY"] = API_KEY
    gemini_client = genai.Client()
    USE_GEMINI = True

if API_KEY.startswith("sk-REPLACE_ME"):
    raise RuntimeError("请在环境变量里配置 API_KEY")

templates = Jinja2Templates(directory="templates")

# -----------------------------------------------------------------------
# 1. FastAPI 初始化
# -----------------------------------------------------------------------
app = FastAPI(title="AI Animation Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatRequest(BaseModel):
    topic: str
    history: Optional[List[dict]] = None
    step: Optional[int] = None  # 可选：指定执行特定步骤

class BookData(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    summary: Optional[str] = None
    key_points: Optional[List[str]] = None
    target_audience: Optional[str] = None
    value: Optional[str] = None
    chapters: Optional[List[str]] = None

# -----------------------------------------------------------------------
# 2. 核心处理函数：分为4个步骤
# -----------------------------------------------------------------------

async def step1_extract_book_data(topic: str) -> dict:
    """
    第1步：提取书本基本数据
    """
    system_prompt = f"""你是一位专业的图书分析师。请对《{topic}》这本书进行基本数据提取和分析。

请提取以下信息：
1. 书名和作者
2. 主要内容概述（3-5句话）
3. 核心观点或理论（3-5个要点）
4. 目标读者群体
5. 书籍的价值和意义
6. 适合制作PPT的关键章节或主题（5-8个）

请以JSON格式返回结果。
"""

    if USE_GEMINI:
        response = await asyncio.get_event_loop().run_in_executor(
            None, 
            lambda: gemini_client.models.generate_content(
                model="gemini-2.0-flash-exp", 
                contents=system_prompt
            )
        )
        result = response.text
    else:
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": system_prompt}],
            temperature=0.7
        )
        result = response.choices[0].message.content

    try:
        return json.loads(result)
    except:
        return {"raw_content": result}

async def step2_create_ppt_slides(book_data: dict) -> list:
    """
    第2步：创建PPT画面结构
    """
    system_prompt = f"""基于以下书籍数据，设计PPT的画面结构：

{json.dumps(book_data, ensure_ascii=False, indent=2)}

请为这本书设计6-10页PPT的画面结构，每页包含：
1. 页面标题
2. 主要视觉元素描述
3. 布局建议
4. 关键信息点

请以JSON数组格式返回，每个元素代表一页PPT。
"""

    if USE_GEMINI:
        response = await asyncio.get_event_loop().run_in_executor(
            None, 
            lambda: gemini_client.models.generate_content(
                model="gemini-2.0-flash-exp", 
                contents=system_prompt
            )
        )
        result = response.text
    else:
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": system_prompt}],
            temperature=0.8
        )
        result = response.choices[0].message.content

    try:
        return json.loads(result)
    except:
        return [{"raw_content": result}]

async def step3_create_narration(slides: list, book_data: dict) -> list:
    """
    第3步：为每页PPT创建解说词
    """
    system_prompt = f"""基于以下PPT画面结构和书籍数据，为每页PPT创建解说词：

书籍数据：
{json.dumps(book_data, ensure_ascii=False, indent=2)}

PPT画面结构：
{json.dumps(slides, ensure_ascii=False, indent=2)}

请为每页PPT创建：
1. 开场白（吸引注意力）
2. 核心内容解说（2-3分钟）
3. 过渡语（连接下一页）

解说词要求：
- 生动有趣，易于理解
- 结合书中具体例子
- 语言流畅自然
- 适合口语表达

请以JSON数组格式返回。
"""

    if USE_GEMINI:
        response = await asyncio.get_event_loop().run_in_executor(
            None, 
            lambda: gemini_client.models.generate_content(
                model="gemini-2.0-flash-exp", 
                contents=system_prompt
            )
        )
        result = response.text
    else:
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": system_prompt}],
            temperature=0.8
        )
        result = response.choices[0].message.content

    try:
        return json.loads(result)
    except:
        return [{"raw_content": result}]

async def step4_generate_html(slides: list, narrations: list, book_data: dict) -> str:
    """
    第4步：将画面和解说词转换为HTML格式
    """
    system_prompt = f"""基于以下数据，生成一个完整的HTML格式PPT：

书籍数据：
{json.dumps(book_data, ensure_ascii=False, indent=2)}

PPT画面：
{json.dumps(slides, ensure_ascii=False, indent=2)}

解说词：
{json.dumps(narrations, ensure_ascii=False, indent=2)}

请生成一个完整的HTML文件，包含：
1. 现代化的CSS样式
2. 响应式设计
3. 每页PPT的完整布局
4. 解说词显示区域
5. 页面导航功能
6. 美观的视觉效果

HTML要求：
- 使用现代CSS（Flexbox/Grid）
- 包含动画效果
- 移动端友好
- 专业的设计风格
"""

    if USE_GEMINI:
        response = await asyncio.get_event_loop().run_in_executor(
            None, 
            lambda: gemini_client.models.generate_content(
                model="gemini-2.0-flash-exp", 
                contents=system_prompt
            )
        )
        result = response.text
    else:
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": system_prompt}],
            temperature=0.7
        )
        result = response.choices[0].message.content

    return result

async def llm_event_stream(
    topic: str,
    history: Optional[List[dict]] = None,
    model: str = "gemini-2.5-pro",
) -> AsyncGenerator[str, None]:
    """
    主流式生成器：依次执行4个步骤
    """
    history = history or []
    
    try:
        # 步骤1：提取书本数据
        yield f"data: {json.dumps({'status': '正在分析书籍数据...'}, ensure_ascii=False)}\n\n"
        book_data = await step1_extract_book_data(topic)
        yield f"data: {json.dumps({'step1_complete': True, 'book_data': book_data}, ensure_ascii=False)}\n\n"
        
        # 步骤2：创建PPT画面
        yield f"data: {json.dumps({'status': '正在设计PPT画面...'}, ensure_ascii=False)}\n\n"
        slides = await step2_create_ppt_slides(book_data)
        yield f"data: {json.dumps({'step2_complete': True, 'slides': slides}, ensure_ascii=False)}\n\n"
        
        # 步骤3：创建解说词
        yield f"data: {json.dumps({'status': '正在创建解说词...'}, ensure_ascii=False)}\n\n"
        narrations = await step3_create_narration(slides, book_data)
        yield f"data: {json.dumps({'step3_complete': True, 'narrations': narrations}, ensure_ascii=False)}\n\n"
        
        # 步骤4：生成HTML
        yield f"data: {json.dumps({'status': '正在生成HTML...'}, ensure_ascii=False)}\n\n"
        html_content = await step4_generate_html(slides, narrations, book_data)
        
        # 分块输出HTML内容
        chunk_size = 100
        for i in range(0, len(html_content), chunk_size):
            chunk = html_content[i:i+chunk_size]
            payload = json.dumps({"token": chunk}, ensure_ascii=False)
            yield f"data: {payload}\n\n"
            await asyncio.sleep(0.02)
            
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
        return

    yield 'data: {"event":"[DONE]"}\n\n'

# -----------------------------------------------------------------------
# 3. 路由 (CHANGED: Now a POST request)
# -----------------------------------------------------------------------
@app.post("/generate")
async def generate(
    chat_request: ChatRequest,
    request: Request,
):
    """
    Main endpoint: POST /generate
    Accepts a JSON body with "topic" and optional "history".
    Returns an SSE stream with 4-step processing.
    """
    accumulated_response = ""

    async def event_generator():
        nonlocal accumulated_response
        try:
            async for chunk in llm_event_stream(chat_request.topic, chat_request.history):
                accumulated_response += chunk
                if await request.is_disconnected():
                    break
                yield chunk
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    async def wrapped_stream():
        async for chunk in event_generator():
            yield chunk

    headers = {
        "Cache-Control": "no-store",
        "Content-Type": "text/event-stream; charset=utf-8",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(wrapped_stream(), headers=headers)

@app.post("/step/{step_number}")
async def execute_step(step_number: int, chat_request: ChatRequest):
    """
    Execute individual steps:
    1 - Extract book data
    2 - Create PPT slides  
    3 - Create narration
    4 - Generate HTML
    """
    try:
        if step_number == 1:
            result = await step1_extract_book_data(chat_request.topic)
            return {"step": 1, "result": result}
        elif step_number == 2:
            # For step 2, we need book_data from previous step or history
            book_data = chat_request.history[-1] if chat_request.history else {}
            result = await step2_create_ppt_slides(book_data)
            return {"step": 2, "result": result}
        elif step_number == 3:
            # For step 3, we need both book_data and slides
            if len(chat_request.history) >= 2:
                book_data = chat_request.history[-2]
                slides = chat_request.history[-1]
                result = await step3_create_narration(slides, book_data)
                return {"step": 3, "result": result}
            else:
                return {"error": "需要前面步骤的数据"}
        elif step_number == 4:
            # For step 4, we need book_data, slides, and narrations
            if len(chat_request.history) >= 3:
                book_data = chat_request.history[-3]
                slides = chat_request.history[-2] 
                narrations = chat_request.history[-1]
                result = await step4_generate_html(slides, narrations, book_data)
                return {"step": 4, "result": result}
            else:
                return {"error": "需要前面步骤的数据"}
        else:
            return {"error": "无效的步骤号，请使用1-4"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse(
        "index.html", {
            "request": request,
            "time": datetime.now(shanghai_tz).strftime("%Y%m%d%H%M%S")})

# -----------------------------------------------------------------------
# 4. 本地启动命令
# -----------------------------------------------------------------------
# uvicorn app:app --reload --host 0.0.0.0 --port 8000


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
