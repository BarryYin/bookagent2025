"""
书籍介绍系统 - 主应用
"""
import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, AsyncGenerator

import pytz
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import AsyncOpenAI, OpenAIError

from models import BookInfo, BookIntroductionRequest, GenerationProgress, ProcessContext
from processors import ProcessOrchestrator

try:
    import google.generativeai as genai
except ModuleNotFoundError:
    from google import genai
# -----------------------------------------------------------------------
# 0. 配置
# -----------------------------------------------------------------------
shanghai_tz = pytz.timezone("Asia/Shanghai")

# 加载凭证
try:
    credentials = json.load(open("credentials.json"))
    API_KEY = credentials["API_KEY"]
    BASE_URL = credentials.get("BASE_URL", "")
    MODEL = credentials.get("MODEL", "gemini-2.5-pro")
except (FileNotFoundError, json.JSONDecodeError, KeyError):
    print("警告: credentials.json 文件不存在或格式错误，将使用模拟数据")
    API_KEY = "mock_api_key"
    BASE_URL = ""
    MODEL = "gemini-2.5-pro"

if API_KEY.startswith("sk-"):
    # 为 OpenRouter 添加应用标识
    extra_headers = {}
    if "openrouter.ai" in BASE_URL.lower():
        extra_headers = {
            "HTTP-Referer": "https://github.com/fogsightai/fogsight",
            "X-Title": "Fogsight - AI Animation Generator"
        }
    
    client = AsyncOpenAI(
        api_key=API_KEY, 
        base_url=BASE_URL,
        default_headers=extra_headers
    )
    USE_GEMINI = False
else:
    os.environ["GEMINI_API_KEY"] = API_KEY
    gemini_client = genai.Client()
    USE_GEMINI = True

# 检查API密钥
if API_KEY.startswith("sk-REPLACE_ME"):
    raise RuntimeError("请在环境变量里配置 API_KEY")

# 初始化模板引擎
templates = Jinja2Templates(directory="templates")

# 会话存储
active_sessions: Dict[str, ProcessContext] = {}
session_progress: Dict[str, List[Dict[str, Any]]] = {}

# -----------------------------------------------------------------------
# 1. FastAPI 初始化
# -----------------------------------------------------------------------
app = FastAPI(title="书籍介绍系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

# -----------------------------------------------------------------------
# 2. API模型
# -----------------------------------------------------------------------
class BookRequest(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None
    genre: Optional[str] = None
    publication_year: Optional[int] = None
    description: Optional[str] = None

class GenerationRequest(BaseModel):
    book_info: BookRequest
    style_preference: str = "professional"
    language: str = "zh"

# -----------------------------------------------------------------------
# 3. 核心处理函数
# -----------------------------------------------------------------------
async def generate_book_introduction_stream(
    request: GenerationRequest
) -> AsyncGenerator[str, None]:
    """生成书籍介绍的流式处理函数"""
    
    # 创建书籍信息对象
    book_info = BookInfo(
        title=request.book_info.title,
        author=request.book_info.author,
        isbn=request.book_info.isbn,
        genre=request.book_info.genre,
        publication_year=request.book_info.publication_year,
        description=request.book_info.description
    )
    
    # 创建流程编排器
    orchestrator = ProcessOrchestrator()
    
    try:
        # 开始处理
        yield f"data: {json.dumps({'event': 'start', 'message': '开始生成书籍介绍'}, ensure_ascii=False)}\n\n"
        
        # 处理书籍信息收集
        yield f"data: {json.dumps({'event': 'progress', 'stage': 'info_collection', 'message': '收集书籍信息...'}, ensure_ascii=False)}\n\n"
        context, progress_updates = await orchestrator.process_book_introduction(book_info)
        
        # 保存会话
        active_sessions[context.session_id] = context
        session_progress[context.session_id] = progress_updates
        
        # 返回处理结果
        for update in progress_updates:
            stage = update.get("stage", "unknown")
            output = update.get("output", {})
            message = output.get("message", f"处理阶段: {stage}")
            
            yield f"data: {json.dumps({'event': 'progress', 'stage': stage, 'message': message, 'data': output}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.1)  # 添加小延迟，使流更平滑
        
        # 返回会话ID
        result = {
            "event": "complete",
            "session_id": context.session_id,
            "message": f"书籍 '{book_info.title}' 的介绍生成已完成",
        }
        yield f"data: {json.dumps(result, ensure_ascii=False)}\n\n"
        
    except Exception as e:
        error_message = f"生成过程中发生错误: {str(e)}"
        yield f"data: {json.dumps({'event': 'error', 'message': error_message}, ensure_ascii=False)}\n\n"
    
    yield 'data: {"event":"[DONE]"}\n\n'

async def llm_event_stream(
    topic: str,
    history: Optional[List[dict]] = None,
    agent_type: str = "exploration",  # 新增智能体类型参数
    model: str = None, # Will use MODEL from config if not specified
) -> AsyncGenerator[str, None]:
    """动画生成的流式处理函数"""
    
    # Use configured model if not specified
    if model is None:
        model = MODEL
    
    # 根据智能体类型生成不同的系统提示
    if agent_type == "exploration":
        # 书籍探索智能体（当前功能）
        system_prompt = f"""请你生成一个非常精美的动态动画,讲讲 {topic}
要动态的,要像一个完整的,正在播放的视频。包含一个完整的过程，能把知识点讲清楚。
页面极为精美，好看，有设计感，同时能够很好的传达知识。知识和图像要准确
附带一些旁白式的文字解说,从头到尾讲清楚一个小的知识点
不需要任何互动按钮,直接开始播放
使用和谐好看，广泛采用的浅色配色方案，使用很多的，丰富的视觉元素。双语字幕
**请保证任何一个元素都在一个2k分辨率的容器中被摆在了正确的位置，避免穿模，字幕遮挡，图形位置错误等等问题影响正确的视觉传达**
html+css+js+svg，放进一个html里"""
    elif agent_type == "recommendation":
        # 引导推荐智能体（待开发）
        system_prompt = f"""作为图书推荐智能体，我需要根据用户的需求：{topic}，提供个性化的图书推荐。
请分析用户的阅读偏好，推荐适合的书籍，并提供详细的推荐理由。
目前此功能正在开发中，请返回一个友好的提示信息。"""
    elif agent_type == "interview":
        # 读后感访谈智能体（待开发）
        system_prompt = f"""作为读后感访谈智能体，我需要与用户进行深度的读书交流：{topic}。
请设计互动性的问题，引导用户分享阅读感受，进行深度的文学讨论。
目前此功能正在开发中，请返回一个友好的提示信息。"""
    else:
        # 默认为书籍探索
        system_prompt = f"""请你生成一个非常精美的动态动画,讲讲 {topic}
要动态的,要像一个完整的,正在播放的视频。包含一个完整的过程，能把知识点讲清楚。
页面极为精美，好看，有设计感，同时能够很好的传达知识。知识和图像要准确
附带一些旁白式的文字解说,从头到尾讲清楚一个小的知识点
不需要任何互动按钮,直接开始播放
使用和谐好看，广泛采用的浅色配色方案，使用很多的，丰富的视觉元素。双语字幕
**请保证任何一个元素都在一个2k分辨率的容器中被摆在了正确的位置，避免穿模，字幕遮挡，图形位置错误等等问题影响正确的视觉传达**
html+css+js+svg，放进一个html里"""

    if USE_GEMINI:
        try:
            full_prompt = system_prompt + "\n\n" + topic
            if history:
                history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
                full_prompt = history_text + "\n\n" + full_prompt
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: gemini_client.models.generate_content(
                    model=model, 
                    contents=full_prompt
                )
            )
            
            text = response.text
            chunk_size = 50
            
            for i in range(0, len(text), chunk_size):
                chunk = text[i:i+chunk_size]
                payload = json.dumps({"token": chunk}, ensure_ascii=False)
                yield f"data: {payload}\n\n"
                await asyncio.sleep(0.05)
                
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            return
    else:
        messages = [
            {"role": "system", "content": system_prompt},
            *history,
            {"role": "user", "content": topic},
        ]

        try:
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                temperature=0.8, 
            )
        except OpenAIError as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            return

        async for chunk in response:
            token = chunk.choices[0].delta.content or ""
            if token:
                payload = json.dumps({"token": token}, ensure_ascii=False)
                yield f"data: {payload}\n\n"
                await asyncio.sleep(0.001)

    yield 'data: {"event":"[DONE]"}\n\n'

# -----------------------------------------------------------------------
# 4. API路由
# -----------------------------------------------------------------------
@app.post("/generate-book-introduction")
async def generate_book_introduction(
    request: GenerationRequest,
    http_request: Request,
):
    """
    生成书籍介绍的API端点
    返回SSE流
    """
    async def event_generator():
        try:
            async for chunk in generate_book_introduction_stream(request):
                if await http_request.is_disconnected():
                    break
                yield chunk
        except Exception as e:
            yield f"data: {json.dumps({'event': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

    headers = {
        "Cache-Control": "no-store",
        "Content-Type": "text/event-stream; charset=utf-8",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(event_generator(), headers=headers)

@app.post("/generate")
async def generate_animation(
    request: Request,
):
    """
    生成动画的API端点 (兼容原有接口)
    """
    body = await request.json()
    topic = body.get("topic", "")
    history = body.get("history", [])
    agent_type = body.get("agent_type", "exploration")  # 获取智能体类型，默认为书籍探索
    
    async def event_generator():
        try:
            async for chunk in llm_event_stream(topic, history, agent_type):
                if await request.is_disconnected():
                    break
                yield chunk
        except Exception as e:
            yield f"data: {json.dumps({'event': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

    headers = {
        "Cache-Control": "no-store",
        "Content-Type": "text/event-stream; charset=utf-8",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(event_generator(), headers=headers)

@app.get("/generation-status/{session_id}")
async def get_generation_status(session_id: str):
    """获取生成进度"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    progress = session_progress.get(session_id, [])
    context = active_sessions[session_id]
    
    return {
        "session_id": session_id,
        "book_title": context.book_info.title,
        "progress": progress,
        "completed": len(progress) == len(ProcessOrchestrator().processors)
    }

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    """主页"""
    return templates.TemplateResponse(
        "index.html", {
            "request": request,
            "time": datetime.now(shanghai_tz).strftime("%Y%m%d%H%M%S")
        }
    )

# -----------------------------------------------------------------------
# 5. 本地启动命令
# -----------------------------------------------------------------------
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)