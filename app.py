"""
书籍介绍系统 - 主应用
"""
import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

import pytz
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from models import BookInfo, BookIntroductionRequest, GenerationProgress, ProcessContext
from processors import ProcessOrchestrator

# -----------------------------------------------------------------------
# 0. 配置
# -----------------------------------------------------------------------
shanghai_tz = pytz.timezone("Asia/Shanghai")

# 加载凭证
try:
    credentials = json.load(open("credentials.json"))
    API_KEY = credentials["API_KEY"]
    BASE_URL = credentials.get("BASE_URL", "")
except (FileNotFoundError, json.JSONDecodeError, KeyError):
    print("警告: credentials.json 文件不存在或格式错误，将使用模拟数据")
    API_KEY = "mock_api_key"
    BASE_URL = ""

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