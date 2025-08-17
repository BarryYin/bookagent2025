import asyncio
import json
import httpx
import re
import os
import sys
import subprocess
from datetime import datetime
from typing import AsyncGenerator, List, Optional
from pathlib import Path

import pytz
from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.responses import StreamingResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI, OpenAIError
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from google import genai

# 导入认证相关模块
from models import UserManager, UserCreate, UserLogin, UserResponse, user_manager, verify_token

# 导入方法论配置
sys.path.append(str(Path(__file__).parent / "create"))
try:
    from methodology_config import MethodologyConfig, VoiceConfig, VideoConfig
except ImportError:
    print("Warning: 方法论配置模块导入失败，将使用默认配置")

# -----------------------------------------------------------------------
# 0. 配置
# -----------------------------------------------------------------------
shanghai_tz = pytz.timezone("Asia/Shanghai")

credentials = json.load(open("credentials.json"))
API_KEY = credentials["API_KEY"]
BASE_URL = credentials.get("BASE_URL", "")

# 配置Qwen模型客户端
QWEN_BASE_URL = "https://api-inference.modelscope.cn/v1/"
QWEN_API_KEY = "ms-9ff035d4-50cb-4adf-afe0-89788293e19e"  # ModelScope Token
QWEN_MODEL = "Qwen/Qwen3-Coder-480B-A35B-Instruct"

if API_KEY.startswith("sk-"):
    client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)
    USE_GEMINI = False
    USE_QWEN = False
else:
    # 使用Qwen模型
    client = AsyncOpenAI(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL)
    USE_GEMINI = False
    USE_QWEN = True

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
app.mount("/podcast_audio", StaticFiles(directory="podcast_audio"), name="podcast_audio")
app.mount("/covers", StaticFiles(directory="covers"), name="covers")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

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

class EnhancedGenerateRequest(BaseModel):
    """增强版生成请求模型"""
    title: str
    author: Optional[str] = None
    category: Optional[str] = None
    language: Optional[str] = "中文"
    description: Optional[str] = None
    user_intent: Optional[str] = None
    methodology: str = "dongyu_literature"
    voice_style: Optional[str] = "professional_style"
    video_style: Optional[str] = "classic_ppt"
    agent_type: str = "exploration"

class InterviewRequest(BaseModel):
    """读后感访谈请求模型"""
    message: str
    book_title: str
    book_author: Optional[str] = None
    history: Optional[List[dict]] = None

class VideoExportRequest(BaseModel):
    """视频导出请求模型"""
    session_id: str
    html_file: str
    audio_prefix: str

# -----------------------------------------------------------------------
# 1.5. 书籍封面搜索功能 - 导入test_cover.py的函数
# -----------------------------------------------------------------------

# 导入test_cover.py中的封面搜索函数
try:
    from test_cover import search_book_cover as test_cover_search_book_cover
    from test_cover import search_douban_books, search_google_books, get_search_variations
    from test_cover import normalize_text, calculate_similarity, is_better_match
    from test_cover import download_image
    print("✅ 成功导入test_cover.py中的封面搜索和下载函数")
except ImportError as e:
    print(f"⚠️ 导入test_cover.py失败: {e}")
    # 如果导入失败，使用简化的备用函数
    async def test_cover_search_book_cover(book_title: str, author: str = None) -> str:
        """备用封面搜索函数"""
        return get_default_book_cover(book_title)
    
    async def download_image(url: str, save_path: str) -> bool:
        """备用下载函数"""
        return False

# 导入分类管理器
try:
    from book_category_manager import add_book_to_category, get_all_books_with_categories, get_books_by_category_id, get_categories_summary
    print("✅ 成功导入分类管理器")
except ImportError as e:
    print(f"⚠️ 导入分类管理器失败: {e}")
    # 备用函数
    def add_book_to_category(title: str, author: str, category_info: dict, ppt_path: str):
        pass
    
    def get_all_books_with_categories():
        return []
    
    def get_books_by_category_id(category_id: str):
        return []
    
    def get_categories_summary():
        return {}

    def search_books_by_keyword(keyword: str):
        """搜索书籍的兼容性函数"""
        try:
            # 如果导入了真正的函数，使用它
            from book_category_manager import search_books_by_keyword as real_search
            return real_search(keyword)
        except ImportError:
            # 否则返回所有书籍并过滤
            all_books = get_all_books_with_categories()
            if not keyword:
                return all_books
            
            keyword_lower = keyword.lower()
            filtered_books = []
            for book in all_books:
                # 搜索标题、作者或描述
                if (keyword_lower in book.get('title', '').lower() or 
                    keyword_lower in book.get('author', '').lower() or 
                    keyword_lower in book.get('description', '').lower()):
                    filtered_books.append(book)
            return filtered_books

async def search_book_cover(book_title: str, author: str = None, download: bool = True) -> str:
    """
    搜索书籍封面图片
    使用test_cover.py中的函数，优先使用豆瓣图书API，然后使用Google Books API作为备选
    如果download=True，会下载图片到本地covers目录
    """
    try:
        # 使用test_cover.py中的函数
        cover_url = await test_cover_search_book_cover(book_title, author)
        
        # 如果返回的是本地文件路径，直接返回
        if cover_url.startswith("covers/"):
            return cover_url
        
        # 如果找到了真实URL且需要下载
        if download and cover_url.startswith("http"):
            # 创建covers目录
            import os
            os.makedirs("covers", exist_ok=True)
            
            # 生成文件名
            safe_title = "".join(c for c in book_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_author = "".join(c for c in (author or "") if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_title}_{safe_author}.jpg" if safe_author else f"{safe_title}.jpg"
            filename = filename.replace(" ", "_")
            
            save_path = os.path.join("covers", filename)
            
            # 下载图片
            print(f"📥 正在下载封面: {filename}")
            success = await download_image(cover_url, save_path)
            
            if success:
                print(f"✅ 封面下载成功: {save_path}")
                return save_path
            else:
                print(f"❌ 封面下载失败，使用原始URL")
                return cover_url
        
        return cover_url
        
    except Exception as e:
        print(f"搜索书籍封面失败: {e}")
        return get_default_book_cover(book_title)

def get_default_book_cover(book_title: str) -> str:
    """
    生成默认书籍封面
    基于书名生成一个美观的默认封面样式
    """
    # 预定义的渐变色方案
    gradients = [
        "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
        "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
        "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
        "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)",
        "linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)",
        "linear-gradient(135deg, #ff8a80 0%, #ea4c89 100%)",
        "linear-gradient(135deg, #8fd3f4 0%, #84fab0 100%)"
    ]
    
    # 根据书名哈希选择渐变
    gradient_index = hash(book_title) % len(gradients)
    gradient = gradients[gradient_index]
    
    # 返回CSS渐变字符串，前端可以直接使用
    return f"gradient:{gradient}"

# -----------------------------------------------------------------------
# 2. 核心处理函数：分为4个步骤
# -----------------------------------------------------------------------

async def step1_extract_book_data(topic: str, methodology: str = "dongyu_literature") -> dict:
    """
    第1步：提取书本基本数据（支持方法论）
    """
    
    # 根据方法论调整分析角度
    methodology_context = ""
    if "dongyu" in methodology:
        if "literature" in methodology:
            methodology_context = """
特别关注：
- 作品的情感深度和人性内涵
- 可以引发个人经历共鸣的要素
- 古今中外的对比和引用素材
- 哲学思辨和精神价值
- 适合情感表达的细节和场景
"""
        elif "autobiography" in methodology:
            methodology_context = """
特别关注：
- 人物的关键人生选择和转折点
- 成功与失败的对比反差
- 成长过程中的智慧和教训
- 可学习的人生态度和品格
- 励志价值和激励意义
"""
        elif "fiction" in methodology:
            methodology_context = """
特别关注：
- 想象世界的构建和规则
- 现实与虚构的对比关系
- 思维边界的拓展价值
- 引发思考的哲学问题
- 创意和想象力的体现
"""
    elif "luozhenyu" in methodology:
        methodology_context = """
特别关注：
- 认知升级的具体方法论
- 时代变化和竞争压力
- 实用的效率提升技巧
- 底层逻辑和系统思维
- 可执行的行动指南
"""
    
    system_prompt = f"""你是一位专业的图书分析师。请对《{topic}》这本书进行基本数据提取和分析。

{methodology_context}

请提取以下信息：
1. 书名和作者
2. 主要内容概述（3-5句话）
3. 核心观点或理论（3-5个要点）
4. 目标读者群体
5. 书籍的价值和意义
6. 适合制作PPT的关键章节或主题（5-8个）

请以JSON格式返回结果，确保分析角度符合上述方法论要求。
"""

    try:
        if USE_QWEN:
            response = await client.chat.completions.create(
                model=QWEN_MODEL,
                messages=[{"role": "user", "content": system_prompt}],
                temperature=0.7
            )
            result = response.choices[0].message.content
        else:
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": system_prompt}],
                temperature=0.7
            )
            result = response.choices[0].message.content

        try:
            book_data = json.loads(result)
        except:
            book_data = {"raw_content": result}
        
        # 简单的LLM分类
        try:
            category_prompt = f"""请将《{topic}》这本书分类到以下5个分类之一，只输出分类名称：

文学类、效率提升类、虚构类、自传类、教材类

只输出分类名称，不要其他内容。"""
            
            if USE_QWEN:
                category_response = await client.chat.completions.create(
                    model=QWEN_MODEL,
                    messages=[{"role": "user", "content": category_prompt}],
                    temperature=0.3
                )
                category = category_response.choices[0].message.content.strip()
            else:
                category_response = await client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": category_prompt}],
                    temperature=0.3
                )
                category = category_response.choices[0].message.content.strip()
            
            # 分类映射
            category_mapping = {
                '文学类': {'id': 'literature', 'name': '文学类', 'color': '#E74C3C', 'icon': '📖'},
                '效率提升类': {'id': 'efficiency', 'name': '效率提升类', 'color': '#27AE60', 'icon': '⚡'},
                '虚构类': {'id': 'fiction', 'name': '虚构类', 'color': '#9B59B6', 'icon': '🔮'},
                '自传类': {'id': 'biography', 'name': '自传类', 'color': '#F39C12', 'icon': '👤'},
                '教材类': {'id': 'textbook', 'name': '教材类', 'color': '#34495E', 'icon': '📚'}
            }
            
            category_info = category_mapping.get(category, category_mapping['文学类'])
            book_data['category_id'] = category_info['id']
            book_data['category_name'] = category_info['name']
            book_data['category_color'] = category_info['color']
            book_data['category_icon'] = category_info['icon']
            book_data['category_confidence'] = 1.0
            
            print(f"📚 书籍《{topic}》分类为: {category_info['name']}")
            
        except Exception as e:
            print(f"分类失败: {e}")
            # 默认分类
            book_data['category_id'] = 'literature'
            book_data['category_name'] = '文学类'
            book_data['category_color'] = '#E74C3C'
            book_data['category_icon'] = '📖'
            book_data['category_confidence'] = 0.0
        
        # 搜索书籍封面（暂时简化，避免阻塞）
        try:
            # 从解析的数据中提取书名和作者
            if isinstance(book_data, dict) and 'raw_content' not in book_data:
                book_title = book_data.get('book_title', topic)
                author = book_data.get('author', '')
            else:
                # 从raw_content中提取信息
                book_title = topic
                author = ''
                if 'raw_content' in book_data:
                    content = str(book_data['raw_content'])
                    # 尝试从内容中提取作者信息
                    author_match = re.search(r'"author":\s*"([^"]+)"', content)
                    if author_match:
                        author = author_match.group(1)
            
            # 暂时使用默认封面（避免网络调用阻塞）
            print(f"📸 暂时使用默认封面: {book_title}")
            book_data['cover_url'] = get_default_book_cover(book_title)
            
        except Exception as cover_error:
            print(f"封面处理失败: {cover_error}")
            book_data['cover_url'] = get_default_book_cover(topic)
        
        return book_data
            
    except Exception as e:
        # 详细记录错误信息
        error_str = str(e)
        print(f"Step1 API调用出错，错误类型: {type(e).__name__}")
        print(f"错误详情: {error_str}")
        
        # 根据错误类型提供不同的处理
        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
            print("检测到API配额限制，使用备用数据")
        elif "ConnectError" in error_str or "SSL" in error_str or "EOF" in error_str:
            print("检测到网络连接问题，使用备用数据")
        elif "timeout" in error_str.lower():
            print("检测到请求超时，使用备用数据")
        else:
            print(f"未知错误类型，使用备用数据: {error_str}")
        
        fallback_data = get_fallback_book_data(topic)
        fallback_data['cover_url'] = get_default_book_cover(topic)
        return fallback_data

async def step2_create_ppt_slides(book_data: dict, methodology: str = "dongyu_literature", video_style: str = "classic_ppt") -> list:
    """
    第2步：创建PPT画面结构（支持方法论和视频风格）
    """
    
    # 根据方法论调整PPT结构
    methodology_structure = ""
    if "dongyu_literature" in methodology:
        methodology_structure = """
## 董宇辉式文学作品PPT结构：
1. **情感开场页** - 情感提问 + 金句引入
2. **个人经历页** - 自身故事分享，建立连接
3. **故事重构页** - 英雄之旅 + 时代背景
4. **细节放大页** - 经典场景 + 象征意义
5. **古今对比页** - 古典名句 + 现代思考
6. **作者深挖页** - 创作动机 + 人生体验
7. **现实关照页** - 当下对比 + 价值引导
8. **收获升华页** - 精神财富 + 人生指导

设计特点：
- 温暖的色调，营造情感氛围
- 大量引用和对比
- 注重情感共鸣
- 故事化表达"""
    elif "dongyu_autobiography" in methodology:
        methodology_structure = """
## 董宇辉式自传体PPT结构：
1. **反差开场页** - 成就 vs 出身的对比
2. **人生轨迹页** - 关键转折点时间轴
3. **选择分析页** - 重大决定的背景和代价
4. **困难克服页** - 挫折中的坚持和成长
5. **智慧提炼页** - 人生经验的深度思考
6. **价值传递页** - 对读者的启发意义

设计特点：
- 对比强烈的视觉元素
- 时间轴式布局
- 励志感的色彩搭配"""
    elif "luozhenyu_efficiency" in methodology:
        methodology_structure = """
## 罗振宇式效率提升PPT结构：
1. **焦虑制造页** - 差距对比 + 时代紧迫感
2. **认知升级页** - 底层逻辑揭示
3. **方法拆解页** - 系统化的解决方案
4. **数据支撑页** - 权威背书 + 效果证明
5. **行动指南页** - 具体可执行的步骤
6. **认知变现页** - 学以致用的价值体现

设计特点：
- 强对比色彩（橙色、黑色）
- 数据可视化
- 逻辑清晰的布局
- 紧迫感的视觉表达"""
    else:
        methodology_structure = """
## 通用PPT结构：
1. **开场页** - 书名大标题，简洁背景
2. **作者介绍页** - 作者信息，优雅布局
3. **核心观点页** - 单一重点，大字体展示
4. **数据展示页** - 关键数字，视觉化呈现
5. **引用页** - 书中金句，艺术化排版
6. **总结页** - 核心价值，call-to-action"""
    
    # 根据视频风格调整视觉元素
    style_config = ""
    if video_style == "storytelling":
        style_config = """
视觉风格配置：
- 温暖的色调（暖橙、米白、深棕）
- 手绘风格的插图元素
- 圆润的边角设计
- 温馨的字体选择
- 渐变背景
"""
    elif video_style == "modern_presentation":
        style_config = """
视觉风格配置：
- 现代感强的配色（深蓝、亮橙、纯白）
- 几何图形装饰
- 无衬线字体
- 动感的布局
- 渐变和阴影效果
"""
    else:  # classic_ppt
        style_config = """
视觉风格配置：
- 商务感配色（深蓝、灰白、金色）
- 简洁的线条设计
- 经典的字体搭配
- 对称的布局
- 专业的表格和图表
"""

    system_prompt = f"""基于以下书籍数据，设计符合指定方法论的PPT画面结构：

{json.dumps(book_data, ensure_ascii=False, indent=2)}

{methodology_structure}

{style_config}

每页PPT请包含以下结构：
- slide_number: 页面编号
- slide_type: 页面类型
- title: 主标题
- subtitle: 副标题（可选）
- main_content: 核心内容
- visual_elements: 视觉元素配置
- animation_entrance: 入场动画类型
- key_message: 核心信息

重要要求：
1. 必须严格按照指定方法论的结构来组织内容
2. 内容表达方式要体现方法论特色
3. 视觉风格要符合配置要求
4. 确保每页内容有深度和感染力

请以JSON数组格式返回。
"""

    try:
        if USE_QWEN:
            response = await client.chat.completions.create(
                model=QWEN_MODEL,
                messages=[{"role": "user", "content": system_prompt}],
                temperature=0.8
            )
            result = response.choices[0].message.content
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
            
    except Exception as e:
        # API配额用完或其他错误时，返回默认数据
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "ConnectError" in str(e) or "SSL" in str(e) or "EOF" in str(e):
            book_title = extract_book_title(book_data) if book_data else "未知书籍"
            print(f"Step2 API调用失败，使用备用数据: {e}")
            return get_fallback_slides_data(book_title)
        else:
            book_title = extract_book_title(book_data) if book_data else "未知书籍"
            print(f"Step2 未知错误，使用备用数据: {e}")
            return get_fallback_slides_data(book_title)

async def step3_create_narration(slides: list, book_data: dict, methodology: str = "dongyu_literature") -> list:
    """
    第3步：为每页PPT创建解说词（支持方法论风格）
    """
    
    # 根据方法论调整解说风格
    narration_style = ""
    if "dongyu_literature" in methodology:
        narration_style = """
## 董宇辉式文学作品解说风格：
1. **情感共鸣式开场**：
   - "你有没有过这样的经历..."
   - "当我第一次读到这段文字的时候..."
   - "在那个特殊的时刻..."

2. **表达方式**：
   - 温暖亲切的语调
   - 结合自身经历和感受
   - 大量的比喻和类比
   - 古典文学的引用和对比
   - 哲思与生活的结合

3. **结构模式**：
   - 个人体验 → 文学升华 → 人生感悟
   - 古今对比 → 深度思考 → 价值启发

4. **语言特色**：
   - "我想起了..."、"就像..."、"正如...所说"
   - 充满诗意的表达
   - 温暖的人文关怀
   - 深度的文化内涵"""
    elif "dongyu_autobiography" in methodology:
        narration_style = """
## 董宇辉式自传体解说风格：
1. **反差对比式开场**：
   - "谁能想到..."
   - "在成功的背后..."
   - "从...到...的转变"

2. **表达方式**：
   - 真诚坦率的分享
   - 成长经历的深度挖掘
   - 选择背后的思考过程
   - 失败与成功的对比

3. **结构模式**：
   - 现状展示 → 回溯经历 → 启发思考
   - 困难描述 → 克服过程 → 价值传递"""
    elif "luozhenyu_efficiency" in methodology:
        narration_style = """
## 罗振宇式效率提升解说风格：
1. **焦虑制造式开场**：
   - "你知道吗，现在的时代..."
   - "有一个残酷的事实..."
   - "我们面临着前所未有的挑战..."

2. **表达方式**：
   - 紧迫感的营造
   - 数据和案例的堆叠
   - 逻辑清晰的论证
   - 权威专家的背书
   - 立竿见影的解决方案

3. **结构模式**：
   - 问题暴露 → 原因分析 → 方法提供
   - 差距对比 → 认知升级 → 行动指南

4. **语言特色**：
   - "关键是..."、"核心在于..."、"本质上..."
   - 强烈的时间紧迫感
   - 明确的行动指导
   - 可量化的成果预期"""
    else:
        narration_style = """
## 通用解说风格：
1. **开场方式**：
   - 简洁有力的开场
   - 直接切入主题
   - 制造期待感

2. **表达方式**：
   - 简洁明了，避免冗长
   - 使用数据和事实说话
   - 情感化的语言
   - 适当的停顿和强调"""

    system_prompt = f"""基于以下PPT画面结构和书籍数据，为每页PPT创建指定方法论风格的解说词：

书籍数据：
{json.dumps(book_data, ensure_ascii=False, indent=2)}

PPT画面结构：
{json.dumps(slides, ensure_ascii=False, indent=2)}

{narration_style}

每页解说词包含：
- slide_number: 页面编号
- opening: 开场白（1-2句话，吸引注意）
- main_narration: 主要解说内容（2-3分钟，深入浅出）
- key_emphasis: 重点强调的内容（金句或核心观点）
- transition: 过渡语（连接下一页）
- timing: 时间控制信息
- tone: 语调风格
- voice_emotion: 语音情感标记（用于语音合成）

解说词要求：
- 严格按照指定方法论的表达风格
- 语言要体现方法论的独特特色
- 结合书籍内容，保持风格一致性
- 适合现场演讲的节奏
- 包含适当的情感渲染和语音提示

请以JSON数组格式返回。
"""

    try:
        if USE_QWEN:
            response = await client.chat.completions.create(
                model=QWEN_MODEL,
                messages=[{"role": "user", "content": system_prompt}],
                temperature=0.8
            )
            result = response.choices[0].message.content
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
            
    except Exception as e:
        # API配额用完或其他错误时，返回默认数据
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "ConnectError" in str(e) or "SSL" in str(e) or "EOF" in str(e):
            book_title = extract_book_title(book_data) if book_data else "未知书籍"
            print(f"Step3 API调用失败，使用备用数据: {e}")
            return get_fallback_narrations_data(book_title)
        else:
            book_title = extract_book_title(book_data) if book_data else "未知书籍"
            print(f"Step3 未知错误，使用备用数据: {e}")
            return get_fallback_narrations_data(book_title)

async def step4_generate_html(slides: list, narrations: list, book_data: dict, methodology: str = "dongyu_literature", enable_voice: bool = False, book_title: str = None) -> str:
    """
    第4步：将画面和解说词转换为HTML格式（支持语音和方法论风格）
    """
    
    # 直接使用可靠的内置模板，不再调用AI
    print(f"DEBUG: step4_generate_html直接调用generate_reliable_ppt_html_internal")
    print(f"DEBUG: slides类型: {type(slides)}, 长度: {len(slides) if isinstance(slides, list) else 'N/A'}")
    print(f"DEBUG: narrations类型: {type(narrations)}, 长度: {len(narrations) if isinstance(narrations, list) else 'N/A'}")
    print(f"DEBUG: 传递的book_title: {book_title}")
    result = generate_reliable_ppt_html_internal(slides, narrations, book_data, book_title)
    print(f"DEBUG: 生成的HTML长度: {len(result)}, 包含data-speech: {'data-speech' in result}")
    return result

async def llm_event_stream(
    topic: str,
    history: Optional[List[dict]] = None,
    model: str = QWEN_MODEL,
    user_id: Optional[int] = None,
) -> AsyncGenerator[str, None]:
    """
    主流式生成器：依次执行4个步骤，显示详细的处理日志
    """
    history = history or []
    
    # 生成唯一的会话ID用于保存文件
    import uuid
    session_id = str(uuid.uuid4())
    
    try:
        # 开始思考与规划阶段
        yield f"data: {json.dumps({'log': '🤔 Kiro Agent 开始思考与规划...'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.5)
        
        yield f"data: {json.dumps({'log': f'📚 分析主题: {topic}'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.3)
        
        yield f"data: {json.dumps({'log': '🎯 制定生成策略: 4步骤流程'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.3)
        
        yield f"data: {json.dumps({'log': '  ├─ 步骤1: 提取书籍基本数据'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': '  ├─ 步骤2: 设计PPT画面结构'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': '  ├─ 步骤3: 创建解说词内容'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': '  └─ 步骤4: 生成完整HTML'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.5)
        
        # 步骤1：提取书本数据
        yield f"data: {json.dumps({'log': '🔍 [步骤1/4] 正在分析书籍数据...'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': '  ├─ 调用AI模型分析书籍信息'}, ensure_ascii=False)}\n\n"
        
        try:
            book_data = await step1_extract_book_data(topic)
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "ConnectError" in str(e) or "SSL" in str(e) or "EOF" in str(e):
                yield f"data: {json.dumps({'log': '  ├─ ⚠️  API连接问题，使用备用数据'}, ensure_ascii=False)}\n\n"
                book_data = get_fallback_book_data(topic)
            else:
                yield f"data: {json.dumps({'log': f'  ├─ ⚠️  未知错误，使用备用数据: {str(e)}'}, ensure_ascii=False)}\n\n"
                book_data = get_fallback_book_data(topic)
        
        # 提取书名用于日志显示
        book_title = topic
        if isinstance(book_data, dict) and 'raw_content' in book_data:
            try:
                import re
                title_match = re.search(r'"(?:book_title|title)":\s*"([^"]+)"', str(book_data['raw_content']))
                if title_match:
                    book_title = title_match.group(1)
            except:
                pass
        
        yield f"data: {json.dumps({'log': f'  ├─ 识别书籍: 《{book_title}》'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': '  └─ ✅ 书籍数据分析完成'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.3)
        
        # 步骤2：创建PPT画面
        yield f"data: {json.dumps({'log': '🎨 [步骤2/4] 正在设计PPT画面结构...'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': '  ├─ 基于苹果发布会风格设计'}, ensure_ascii=False)}\n\n"
        
        try:
            slides = await step2_create_ppt_slides(book_data)
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "ConnectError" in str(e) or "SSL" in str(e) or "EOF" in str(e):
                yield f"data: {json.dumps({'log': '  ├─ ⚠️  API连接问题，使用备用数据'}, ensure_ascii=False)}\n\n"
                slides = get_fallback_slides_data(book_title)
            else:
                yield f"data: {json.dumps({'log': f'  ├─ ⚠️  未知错误，使用备用数据: {str(e)}'}, ensure_ascii=False)}\n\n"
                slides = get_fallback_slides_data(book_title)
        
        slide_count = len(slides) if isinstance(slides, list) else 3
        yield f"data: {json.dumps({'log': f'  ├─ 设计了 {slide_count} 页PPT画面'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': '  └─ ✅ PPT画面设计完成'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.3)
        
        # 步骤3：创建解说词
        yield f"data: {json.dumps({'log': '🎤 [步骤3/4] 正在创建解说词内容...'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': '  ├─ 为每页PPT匹配解说词'}, ensure_ascii=False)}\n\n"
        
        try:
            narrations = await step3_create_narration(slides, book_data)
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "ConnectError" in str(e) or "SSL" in str(e) or "EOF" in str(e):
                yield f"data: {json.dumps({'log': '  ├─ ⚠️  API连接问题，使用备用数据'}, ensure_ascii=False)}\n\n"
                narrations = get_fallback_narrations_data(book_title)
            else:
                yield f"data: {json.dumps({'log': f'  ├─ ⚠️  未知错误，使用备用数据: {str(e)}'}, ensure_ascii=False)}\n\n"
                narrations = get_fallback_narrations_data(book_title)
        
        narration_count = len(narrations) if isinstance(narrations, list) else slide_count
        yield f"data: {json.dumps({'log': f'  ├─ 生成了 {narration_count} 段解说词'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': '  └─ ✅ 解说词创建完成'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.3)
        
        # 步骤4：生成HTML
        yield f"data: {json.dumps({'log': '🔧 [步骤4/4] 正在生成完整HTML...'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': '  ├─ 使用可靠的内置模板'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': '  ├─ 集成交互功能和导航'}, ensure_ascii=False)}\n\n"
        
        html_content = await step4_generate_html(slides, narrations, book_data)
        
        # 清理HTML内容
        html_content = clean_html_content(html_content)
        
        # 验证HTML内容完整性
        if not html_content.strip().endswith('</html>'):
            raise ValueError("生成的HTML内容不完整")
        
        yield f"data: {json.dumps({'log': f'  ├─ HTML长度: {len(html_content)} 字符'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': '  └─ ✅ HTML生成完成'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.3)
        
        # 保存文件
        yield f"data: {json.dumps({'log': '💾 正在保存生成的文件...'}, ensure_ascii=False)}\n\n"
        
        await save_generated_content(session_id, {
            'topic': topic,
            'book_data': book_data,
            'slides': slides,
            'narrations': narrations,
            'html_content': html_content
        })
        
        yield f"data: {json.dumps({'log': f'  └─ ✅ 文件已保存到: outputs/{session_id}/'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.3)
        
        # 开始输出结果
        yield f"data: {json.dumps({'log': '🎉 生成完成！开始输出结果...'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.5)
        
        # 检查HTML内容
        yield f"data: {json.dumps({'log': f'🔍 检查HTML内容: 长度={len(html_content)}, 类型={type(html_content)}'}, ensure_ascii=False)}\n\n"
        
        if not html_content:
            yield f"data: {json.dumps({'log': '❌ HTML内容为空！'}, ensure_ascii=False)}\n\n"
            return
        
        # 按照前端期望的格式输出HTML内容
        yield f"data: {json.dumps({'log': '📤 开始输出HTML内容...'}, ensure_ascii=False)}\n\n"
        
        start_token = '```html\n'
        yield f"data: {json.dumps({'token': start_token}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': f'  ├─ 已发送开始标记: {repr(start_token)}'}, ensure_ascii=False)}\n\n"
        
        # 分块输出HTML内容，使用较大的块大小确保完整性
        chunk_size = 500
        chunk_count = 0
        for i in range(0, len(html_content), chunk_size):
            chunk = html_content[i:i+chunk_size]
            chunk_count += 1
            # 确保JSON字符串正确转义
            payload = json.dumps({"token": chunk}, ensure_ascii=False)
            yield f"data: {payload}\n\n"
            await asyncio.sleep(0.01)
        
        yield f"data: {json.dumps({'log': f'  ├─ 已发送 {chunk_count} 个HTML块'}, ensure_ascii=False)}\n\n"
        
        # 输出结束标记
        end_token = '\n```'
        yield f"data: {json.dumps({'token': end_token}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': f'  └─ 已发送结束标记: {repr(end_token)}'}, ensure_ascii=False)}\n\n"
        
        # 最终完成信息
        yield f"data: {json.dumps({'log': '🎊 PPT生成完成！您可以在浏览器中查看效果'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': '✅ 准备发送DONE信号'}, ensure_ascii=False)}\n\n"
        
        # 如果有用户ID，保存PPT信息到数据库
        if user_id:
            try:
                await save_ppt_to_database(session_id, user_id, topic)
                yield f"data: {json.dumps({'log': '💾 PPT信息已保存到个人书架'}, ensure_ascii=False)}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'log': f'⚠️ 保存到书架失败: {str(e)}'}, ensure_ascii=False)}\n\n"
            
    except Exception as e:
        error_msg = f"❌ 生成过程中发生错误: {str(e)}"
        yield f"data: {json.dumps({'error': error_msg}, ensure_ascii=False)}\n\n"
        return

    yield f"data: {json.dumps({'log': '📡 发送DONE信号'}, ensure_ascii=False)}\n\n"
    yield f'data: {json.dumps({"event":"[DONE]", "session_id": session_id, "output_path": f"outputs/{session_id}/"}, ensure_ascii=False)}\n\n'

# -----------------------------------------------------------------------
# 5. 文件保存功能
# -----------------------------------------------------------------------
async def save_ppt_to_database(session_id: str, user_id: int, topic: str):
    """保存PPT信息到数据库"""
    try:
        # 读取data.json文件获取详细信息
        data_file = f"outputs/{session_id}/data.json"
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            book_data = data.get('book_data', {})
            title = topic  # 默认使用topic
            author = "未知作者"
            
            # 首先尝试从book_data中提取书名
            if isinstance(book_data, dict):
                if 'title' in book_data:
                    title = book_data['title']
                elif 'book_title' in book_data:
                    title = book_data['book_title']
                elif 'raw_content' in book_data:
                    content_str = str(book_data['raw_content'])
                    # 尝试从内容中提取书名
                    title_match = re.search(r'"title":\s*"([^"]+)"', content_str)
                    if title_match:
                        title = title_match.group(1)
                    else:
                        # 如果没有找到结构化的书名，尝试从topic中提取
                        if '《' in topic and '》' in topic:
                            title_match = re.search(r'《([^》]+)》', topic)
                            if title_match:
                                title = title_match.group(1)
            
            # 提取作者信息
            if isinstance(book_data, dict):
                if 'author' in book_data:
                    author = book_data['author']
                elif 'raw_content' in book_data:
                    content_str = str(book_data['raw_content'])
                    author_match = re.search(r'"author":\s*"([^"]+)"', content_str)
                    if author_match:
                        author = author_match.group(1)
            
            # 提取分类信息
            category_id = book_data.get('category_id', 'literature')
            category_name = book_data.get('category_name', '文学类')
            category_color = book_data.get('category_color', '#E74C3C')
            category_icon = book_data.get('category_icon', '📖')
            
            # 获取封面URL
            cover_url = None
            if 'cover_url' in book_data:
                cover_url = book_data['cover_url']
                
            # 如果封面URL是default_cover，生成默认封面
            if cover_url == "default_cover":
                cover_url = get_default_book_cover(title)
            
            # 保存到数据库
            from models import user_manager
            success = user_manager.add_ppt(
                session_id=session_id,
                user_id=user_id,
                title=title,
                author=author,
                cover_url=cover_url,
                category_id=category_id,
                category_name=category_name,
                category_color=category_color,
                category_icon=category_icon
            )
            
            if success:
                print(f"✅ PPT已保存到用户数据库: {title}")
            else:
                print(f"❌ 保存PPT到数据库失败: {title}")
                
    except Exception as e:
        print(f"保存PPT到数据库时出错: {e}")

async def save_generated_content(session_id: str, content: dict):
    """
    保存生成的内容到文件系统
    """
    import os
    
    # 创建输出目录
    output_dir = f"outputs/{session_id}"
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存HTML文件
    html_file = os.path.join(output_dir, "presentation.html")
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content['html_content'])
    
    # 保存JSON数据文件
    data_file = os.path.join(output_dir, "data.json")
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump({
            'topic': content['topic'],
            'book_data': content['book_data'],
            'slides': content['slides'],
            'narrations': content['narrations']
        }, f, ensure_ascii=False, indent=2)
    
    # 保存README文件
    readme_file = os.path.join(output_dir, "README.md")
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(f"""# 书籍介绍PPT - {content['topic']}

## 文件说明
- `presentation.html` - 完整的PPT演示文件（可直接在浏览器中打开）
- `data.json` - 生成过程中的所有数据
- `README.md` - 本说明文件

## 使用方法
1. 直接双击 `presentation.html` 在浏览器中打开
2. 使用左右箭头键或点击导航点切换页面
3. 查看底部解说词面板了解详细内容

## 生成时间
{datetime.now(shanghai_tz).strftime("%Y-%m-%d %H:%M:%S")}

## 会话ID
{session_id}
""")
    
    # 添加到分类数据库
    try:
        book_data = content.get('book_data', {})
        topic = content.get('topic', '')
        
        # 提取作者信息
        author = "未知作者"
        if isinstance(book_data, dict):
            # 尝试从不同字段提取作者
            if 'author' in book_data:
                author = book_data['author']
            elif 'raw_content' in book_data:
                content_str = str(book_data['raw_content'])
                author_match = re.search(r'"author":\s*"([^"]+)"', content_str)
                if author_match:
                    author = author_match.group(1)
        
        # 提取分类信息
        category_info = {
            'category_id': book_data.get('category_id', 'literature'),
            'category_name': book_data.get('category_name', '文学类'),
            'category_color': book_data.get('category_color', '#E74C3C'),
            'category_icon': book_data.get('category_icon', '📖')
        }
        
        # 添加到分类数据库
        add_book_to_category(topic, author, category_info, session_id)
        print(f"✅ 已添加到分类数据库: 《{topic}》- {category_info['category_name']}")
        
    except Exception as e:
        print(f"⚠️ 添加到分类数据库失败: {e}")
    
    print(f"内容已保存到: {output_dir}/")
    return output_dir

def clean_html_content(html_content: str) -> str:
    """
    清理HTML内容，移除代码块标记和多余内容
    """
    import re
    
    # 移除开头的 ```html 标记
    html_content = re.sub(r'^```html\s*\n?', '', html_content, flags=re.MULTILINE)
    
    # 移除结尾的 ``` 标记和后续的所有内容
    html_content = re.sub(r'\n?```[\s\S]*$', '', html_content)
    
    # 确保文件以 </html> 结尾
    if not html_content.strip().endswith('</html>'):
        # 找到最后一个 </html> 标签的位置
        last_html_match = None
        for match in re.finditer(r'</html>', html_content):
            last_html_match = match
        
        if last_html_match:
            # 截取到最后一个 </html> 标签
            html_content = html_content[:last_html_match.end()]
    
    # 移除多余的空行
    html_content = re.sub(r'\n\s*\n\s*\n', '\n\n', html_content)
    
    # 确保文件以换行符结尾
    if not html_content.endswith('\n'):
        html_content += '\n'
    
    return html_content

def generate_reliable_ppt_html_internal(slides, narrations, book_data, book_title=None):
    """生成优化的毛玻璃风格PPT HTML"""
    
    print(f"DEBUG: generate_reliable_ppt_html_internal 开始执行")
    print(f"DEBUG: slides: {type(slides)}, narrations: {type(narrations)}")
    print(f"DEBUG: 传入的book_title参数: {book_title}")
    
    # 解析book_data
    parsed_book_data = parse_ai_response(book_data)
    
    # 优先使用传入的book_title参数，否则尝试从book_data中提取
    if book_title:
        final_book_title = book_title
        print(f"DEBUG: 使用传入的book_title: {final_book_title}")
    else:
        final_book_title = extract_book_title(parsed_book_data)
        print(f"DEBUG: 从book_data提取的book_title: {final_book_title}")
    
    # 如果还是"未知书籍"，尝试从book_data的其他字段获取
    if final_book_title == "未知书籍" and isinstance(book_data, dict):
        if 'title' in book_data:
            final_book_title = book_data['title']
        elif 'book_title' in book_data:
            final_book_title = book_data['book_title']
    
    print(f"DEBUG: 最终使用的book_title: {final_book_title}")
    
    # 获取书籍封面
    cover_url = ""
    if isinstance(book_data, dict):
        cover_url = book_data.get('cover_url', '')
    if not cover_url and isinstance(parsed_book_data, dict):
        cover_url = parsed_book_data.get('cover_url', '')
    
    # 解析slides数据
    parsed_slides = parse_ai_response(slides)
    processed_slides = process_slides_data(parsed_slides, final_book_title)
    print(f"DEBUG: processed_slides 长度: {len(processed_slides)}")
    
    # 解析narrations数据
    parsed_narrations = parse_ai_response(narrations)
    processed_narrations = process_narrations_data(parsed_narrations, final_book_title)
    print(f"DEBUG: processed_narrations 长度: {len(processed_narrations)}")
    
    # 确保slides和narrations数量匹配
    while len(processed_narrations) < len(processed_slides):
        processed_narrations.append(f'这是第{len(processed_narrations)+1}页的解说内容')
    
    # 生成解说词数据（每页按句子分割）
    narration_data = []
    for i, narration in enumerate(processed_narrations):
        sentences = []
        timings = []
        
        # 按标点符号分割句子
        text = str(narration).strip()
        sentence_list = []
        for sent in text.split('。'):
            sent = sent.strip()
            if sent:
                sentence_list.append(sent + '。')
        
        # 如果没有按句号分割成功，尝试其他标点
        if len(sentence_list) <= 1:
            for sent in text.split('！'):
                sent = sent.strip()
                if sent:
                    sentence_list.append(sent + '！')
        
        if len(sentence_list) <= 1:
            for sent in text.split('？'):
                sent = sent.strip()
                if sent:
                    sentence_list.append(sent + '？')
        
        # 如果还是分割不了，就用整段文字
        if len(sentence_list) <= 1:
            sentence_list = [text]
        
        # 生成时间点（每句话间隔6秒）
        for j, sentence in enumerate(sentence_list):
            sentences.append(sentence)
            timings.append(j * 6)
        
        narration_data.append({
            "sentences": sentences,
            "timings": timings
        })
    
    # 生成幻灯片HTML
    slides_html = ""
    for i, slide in enumerate(processed_slides):
        active_class = "active" if i == 0 else ""
        # 获取对应的解说词，并进行HTML转义
        narration_text = processed_narrations[i] if i < len(processed_narrations) else ""
        # HTML转义处理引号和特殊字符
        narration_text = str(narration_text).replace('"', '&quot;').replace('\n', ' ').replace('\r', '')
        
        if i == 0:
            # 书籍标题页 - 专门展示书名
            slides_html += f'''
                <div class="slide {active_class}" data-speech="{narration_text}">
                    <div style="text-align: center; padding: 2rem;">
                        <h1 style="font-size: 3rem; font-weight: bold; margin-bottom: 1rem; color: #1D1D1F;">{final_book_title}</h1>
                        <div style="width: 80px; height: 3px; background: linear-gradient(to right, #667eea, #764ba2); margin: 2rem auto; border-radius: 2px;"></div>
                        <p style="font-size: 1.2rem; color: #666; font-style: italic;">欢迎来到本书的精彩解读</p>
                    </div>
                </div>'''
        else:
            # 内容页
            content = slide.get('content', '').replace('\n', '<br>')
            slides_html += f'''
                <div class="slide {active_class}" data-speech="{narration_text}">
                    <h2>{slide.get('title', f'第{i+1}页')}</h2>
                    <p>{content}</p>
                </div>'''
    
    
    # 生成解说词JavaScript数据
    narration_data_js = "["
    for i, data in enumerate(narration_data):
        if i > 0:
            narration_data_js += ","
        narration_data_js += "\n        {\n"
        narration_data_js += f'            "sentences": {json.dumps(data["sentences"], ensure_ascii=False)},\n'
        narration_data_js += f'            "timings": {data["timings"]}\n'
        narration_data_js += "        }"
    narration_data_js += "\n    ]"
    
    html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{final_book_title} - Bookagent 智能演示</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-font-smoothing: antialiased;
        }}

        body {{
            font-family: "Helvetica Neue", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            background: linear-gradient(135deg, 
                #667eea 0%, 
                #764ba2 25%, 
                #f093fb 50%, 
                #f5576c 75%, 
                #4facfe 100%);
            background-size: 400% 400%;
            animation: gradientShift 10s ease infinite;
            min-height: 100vh;
            overflow: hidden;
            color: #333;
        }}

        @keyframes gradientShift {{
            0%, 100% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
        }}

        .presentation-container {{
            display: flex;
            height: 100vh;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
        }}

        /* 左侧导航 */
        .nav-sidebar {{
            width: 250px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(30px);
            -webkit-backdrop-filter: blur(30px);
            border-right: 1px solid rgba(255, 255, 255, 0.2);
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}

        .logo-section {{
            text-align: center;
            padding: 20px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            margin-bottom: 20px;
        }}

        .logo-title {{
            font-size: 24px;
            font-weight: bold;
            color: white;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
            background: linear-gradient(45deg, #fff, #f0f0f0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .nav-button {{
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 15px 20px;
            color: white;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            text-align: center;
            font-size: 16px;
            font-weight: 500;
            text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
            position: relative;
            overflow: hidden;
        }}

        .nav-button:hover {{
            background: rgba(255, 255, 255, 0.25);
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        }}

        .nav-button.playing {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}

        .slide-counter {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 12px;
            text-align: center;
            color: white;
            font-size: 14px;
            margin-top: auto;
        }}

        /* 主内容区域 */
        .main-content {{
            flex: 1;
            display: flex;
            flex-direction: column;
            position: relative;
        }}

        .slide-container {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px;
            position: relative;
        }}

        .slide {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 60px;
            max-width: 900px;
            width: 100%;
            min-height: 600px;
            display: none;
            flex-direction: column;
            justify-content: center;
            position: relative;
            animation: slideIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        .slide.active {{
            display: flex;
        }}

        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateY(30px) scale(0.95);
            }}
            to {{
                opacity: 1;
                transform: translateY(0) scale(1);
            }}
        }}

        .slide h1 {{
            font-size: 2.5em;
            margin-bottom: 30px;
            color: #2c3e50;
            text-align: center;
            line-height: 1.3;
            font-weight: 600;
        }}

        .slide h2 {{
            font-size: 2em;
            margin-bottom: 25px;
            color: #34495e;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}

        .slide p {{
            font-size: 1.2em;
            line-height: 1.8;
            margin-bottom: 20px;
            color: #555;
            text-align: justify;
        }}

        .slide ul {{
            margin: 20px 0;
            padding-left: 30px;
        }}

        .slide li {{
            font-size: 1.1em;
            line-height: 1.7;
            margin-bottom: 12px;
            color: #666;
        }}

        /* 右侧导航 */
        .nav-right {{
            width: 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 20px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(30px);
            -webkit-backdrop-filter: blur(30px);
            border-left: 1px solid rgba(255, 255, 255, 0.2);
        }}

        .nav-arrow {{
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            color: white;
            font-size: 20px;
            margin: 0 auto;
        }}

        .nav-arrow:hover {{
            background: rgba(255, 255, 255, 0.25);
            transform: scale(1.1);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
        }}

        .nav-arrow:disabled {{
            opacity: 0.3;
            cursor: not-allowed;
            transform: none;
        }}

        /* 字幕区域 */
        .narration-display {{
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            color: #FFD700;
            padding: 25px 40px;
            text-align: center;
            font-size: 18px;
            line-height: 1.6;
            min-height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
        }}

        .sentence {{
            opacity: 0;
            transition: opacity 0.8s ease-in-out;
            font-weight: 500;
        }}

        .sentence.active {{
            opacity: 1;
        }}

        /* 响应式设计 */
        @media (max-width: 1024px) {{
            .nav-sidebar {{
                width: 200px;
            }}
            
            .slide {{
                padding: 40px;
                max-width: 700px;
            }}
        }}

        @media (max-width: 768px) {{
            .presentation-container {{
                flex-direction: column;
            }}
            
            .nav-sidebar {{
                width: 100%;
                height: auto;
                flex-direction: row;
                justify-content: space-around;
                padding: 15px;
            }}
            
            .nav-right {{
                width: 100%;
                flex-direction: row;
                justify-content: center;
                height: auto;
                padding: 15px;
            }}
            
            .slide {{
                padding: 30px;
                margin: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="presentation-container">
        <!-- 左侧导航栏 -->
        <div class="nav-sidebar">
            <div class="logo-section">
                <div class="logo-title">Bookagent</div>
            </div>
            
            <button id="playPauseButton" class="nav-button" onclick="toggleAudio()">
                🔊 播放解说
            </button>
            
            <button id="backButton" class="nav-button" onclick="goBack()" style="background: rgba(255, 255, 255, 0.2);">
                ← 返回主页
            </button>
            
            <div class="slide-counter">
                <div id="slideCounter">第 1 页 / {len(processed_slides)} 页</div>
            </div>
        </div>

        <!-- 主内容区域 -->
        <div class="main-content">
            <div class="slide-container">
                {slides_html}
            </div>

            <!-- 字幕显示区域 -->
            <div class="narration-display">
                <div id="currentNarration">点击"播放解说"开始自动播放演示</div>
            </div>
        </div>

        <!-- 右侧导航 -->
        <div class="nav-right">
            <button class="nav-arrow" id="prevBtn" onclick="prevSlide()">❮</button>
            <button class="nav-arrow" id="nextBtn" onclick="nextSlide()">❯</button>
        </div>
    </div>

    <!-- 音频播放器 -->
    <audio id="audioPlayer" preload="auto"></audio>

    <script>
        // 全局变量
        let currentSlide = 0;
        let totalSlides = {len(processed_slides)};
        let isAutoPlaying = false;
        let isPlaying = false;
        let sentenceTimers = [];

        // 解说词数据
        const narrationData = {narration_data_js};

        // 初始化
        document.addEventListener('DOMContentLoaded', function() {{
            updateSlideCounter();
            updateNavigationButtons();
        }});

        // 音频播放功能
        function toggleAudio() {{
            const playPauseButton = document.getElementById('playPauseButton');
            
            if (isAutoPlaying) {{
                // 停止自动播放
                stopAutoPlay();
                playPauseButton.textContent = '🔊 播放解说';
                playPauseButton.classList.remove('playing');
            }} else {{
                // 开始自动播放整个PPT
                startAutoPlay();
                playPauseButton.textContent = '⏸️ 停止播放';
                playPauseButton.classList.add('playing');
            }}
        }}
        
        function startAutoPlay() {{
            isAutoPlaying = true;
            // 从当前页开始播放，而不是重置到第一页
            // currentSlide 保持当前值
            showSlide(currentSlide);
            playCurrentSlide();
        }}
        
        function stopAutoPlay() {{
            isAutoPlaying = false;
            isPlaying = false;
            const audioPlayer = document.getElementById('audioPlayer');
            if (audioPlayer) {{
                audioPlayer.pause();
                audioPlayer.currentTime = 0;
            }}
            clearSentenceTimers();
            resetNarrationDisplay();
        }}
        
        function playCurrentSlide() {{
            if (!isAutoPlaying) return;
            
            const audioPlayer = document.getElementById('audioPlayer');
            const sessionId = window.location.pathname.split('/')[2]; // 从URL中提取session_id
            const slideNumber = (currentSlide + 1).toString().padStart(2, '0');
            const audioPath = `/ppt_audio/${{sessionId}}_slide_${{slideNumber}}.mp3`;
            
            audioPlayer.src = audioPath;
            audioPlayer.play().then(() => {{
                isPlaying = true;
                startSentenceDisplay();
            }}).catch((error) => {{
                console.error('音频播放失败:', error);
                // 如果音频播放失败，仍然显示字幕并在5秒后切换到下一页
                startSentenceDisplay();
                setTimeout(() => {{
                    if (isAutoPlaying) {{
                        goToNextSlide();
                    }}
                }}, 5000);
            }});
        }}

        // 导航功能
        function nextSlide() {{
            if (isAutoPlaying) {{
                stopAutoPlay();
                const playPauseButton = document.getElementById('playPauseButton');
                playPauseButton.textContent = '🔊 播放解说';
                playPauseButton.classList.remove('playing');
            }}
            goToNextSlide();
        }}
        
        function prevSlide() {{
            if (isAutoPlaying) {{
                stopAutoPlay();
                const playPauseButton = document.getElementById('playPauseButton');
                playPauseButton.textContent = '🔊 播放解说';
                playPauseButton.classList.remove('playing');
            }}
            goToPrevSlide();
        }}
        
        function goToNextSlide() {{
            if (currentSlide < totalSlides - 1) {{
                currentSlide++;
                showSlide(currentSlide);
                if (isAutoPlaying) {{
                    setTimeout(() => playCurrentSlide(), 500);
                }}
            }} else if (isAutoPlaying) {{
                // 到达最后一页，停止自动播放
                stopAutoPlay();
                const playPauseButton = document.getElementById('playPauseButton');
                playPauseButton.textContent = '🔊 播放解说';
                playPauseButton.classList.remove('playing');
            }}
        }}
        
        function goToPrevSlide() {{
            if (currentSlide > 0) {{
                currentSlide--;
                showSlide(currentSlide);
                if (isAutoPlaying) {{
                    setTimeout(() => playCurrentSlide(), 500);
                }}
            }}
        }}

        function showSlide(slideIndex) {{
            const slides = document.querySelectorAll('.slide');
            
            // 隐藏所有幻灯片
            slides.forEach(slide => slide.classList.remove('active'));
            
            // 显示目标幻灯片
            if (slides[slideIndex]) {{
                slides[slideIndex].classList.add('active');
                currentSlide = slideIndex;
            }}
            
            updateSlideCounter();
            updateNavigationButtons();
            if (!isAutoPlaying) {{
                resetNarrationDisplay();
            }}
        }}

        function updateSlideCounter() {{
            const counter = document.getElementById('slideCounter');
            if (counter) {{
                counter.textContent = `第 ${{currentSlide + 1}} 页 / ${{totalSlides}} 页`;
            }}
        }}

        function updateNavigationButtons() {{
            const prevBtn = document.getElementById('prevBtn');
            const nextBtn = document.getElementById('nextBtn');
            
            if (prevBtn) {{
                prevBtn.disabled = currentSlide === 0;
            }}
            if (nextBtn) {{
                nextBtn.disabled = currentSlide === totalSlides - 1;
            }}
        }}

        // 字幕显示功能
        function startSentenceDisplay() {{
            const slideData = narrationData[currentSlide];
            if (!slideData) return;
            
            clearSentenceTimers();
            
            slideData.sentences.forEach((sentence, index) => {{
                const delay = slideData.timings[index] * 1000;
                const timer = setTimeout(() => {{
                    if (isAutoPlaying || isPlaying) {{
                        displaySentence(sentence);
                    }}
                }}, delay);
                sentenceTimers.push(timer);
            }});

            // 音频结束后自动切换到下一页
            const audioPlayer = document.getElementById('audioPlayer');
            audioPlayer.onended = () => {{
                if (isAutoPlaying) {{
                    setTimeout(() => goToNextSlide(), 1000);
                }}
            }};
        }}

        function displaySentence(sentence) {{
            const narrationDiv = document.getElementById('currentNarration');
            if (narrationDiv) {{
                narrationDiv.innerHTML = `<span class="sentence active">${{sentence}}</span>`;
            }}
        }}

        function clearSentenceTimers() {{
            sentenceTimers.forEach(timer => clearTimeout(timer));
            sentenceTimers = [];
        }}

        function resetNarrationDisplay() {{
            const narrationDiv = document.getElementById('currentNarration');
            if (narrationDiv) {{
                narrationDiv.innerHTML = '点击"播放解说"开始自动播放演示';
            }}
        }}

        // 键盘导航
        document.addEventListener('keydown', function(event) {{
            if (event.key === 'ArrowLeft') {{
                prevSlide();
            }} else if (event.key === 'ArrowRight') {{
                nextSlide();
            }} else if (event.key === ' ') {{
                event.preventDefault();
                toggleAudio();
            }}
        }});

        // 返回主页功能
        function goBack() {{
            // 返回到主应用页面
            window.location.href = '/';
        }}
    </script>
</body>
</html>'''
    
    return html_template

def parse_ai_response(data):
    """解析AI返回的数据，处理raw_content格式"""
    if isinstance(data, dict) and 'raw_content' in data:
        raw_content = data['raw_content']
        if isinstance(raw_content, str):
            # 尝试从JSON代码块中提取数据
            import re
            json_match = re.search(r'```json\s*\n(.*?)\n```', raw_content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except:
                    pass
            # 尝试直接解析JSON
            try:
                return json.loads(raw_content)
            except:
                pass
        return raw_content
    elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict) and 'raw_content' in data[0]:
        # 处理列表格式的数据
        return parse_ai_response(data[0])
    return data

def extract_book_title(book_data):
    """从书籍数据中提取标题"""
    if isinstance(book_data, dict):
        # 直接查找title字段
        if 'book_title' in book_data:
            return book_data['book_title']
        elif 'title' in book_data:
            return book_data['title']
        # 检查raw_content字段
        elif 'raw_content' in book_data:
            raw_content = book_data['raw_content']
            if isinstance(raw_content, str):
                import re
                # 尝试多种模式匹配
                patterns = [
                    r'"book_title":\s*"([^"]+)"',
                    r'"title":\s*"([^"]+)"',
                    r'《([^》]+)》',  # 匹配书名号
                    r'"([^"]*)"'  # 最后尝试匹配任何引号内容
                ]
                for pattern in patterns:
                    match = re.search(pattern, raw_content)
                    if match:
                        title = match.group(1).strip()
                        if title and title != "未知书籍":
                            return title
    
    # 从字符串中提取
    if isinstance(book_data, str):
        import re
        patterns = [
            r'"(?:book_title|title)":\s*"([^"]+)"',
            r'《([^》]+)》',
            r'"([^"]*)"'
        ]
        for pattern in patterns:
            match = re.search(pattern, book_data)
            if match:
                title = match.group(1).strip()
                if title and title != "未知书籍":
                    return title
    
    return "未知书籍"

def process_slides_data(slides_data, book_title):
    """处理幻灯片数据"""
    processed_slides = []
    
    if isinstance(slides_data, list) and len(slides_data) > 0:
        for i, slide in enumerate(slides_data):
            if isinstance(slide, dict):
                processed_slides.append({
                    'title': slide.get('title', f'第{i+1}页'),
                    'subtitle': slide.get('subtitle', ''),
                    'content': slide.get('main_content', slide.get('content', ''))
                })
            else:
                processed_slides.append({
                    'title': f'第{i+1}页',
                    'subtitle': '',
                    'content': str(slide)
                })
    
    # 如果没有有效数据，使用默认幻灯片
    if not processed_slides:
        processed_slides = [
            {'title': book_title, 'subtitle': '开场介绍', 'content': f'欢迎来到《{book_title}》的分享'},
            {'title': '作者介绍', 'subtitle': '了解作者', 'content': f'让我们了解《{book_title}》的作者'},
            {'title': '核心内容', 'subtitle': '主要观点', 'content': f'《{book_title}》的核心内容和主要观点'},
            {'title': '深度解读', 'subtitle': '精彩片段', 'content': f'《{book_title}》中的精彩片段和深度思考'},
            {'title': '现实意义', 'subtitle': '当代价值', 'content': f'《{book_title}》对当代读者的意义和价值'},
            {'title': '总结', 'subtitle': '结束语', 'content': f'感谢您观看《{book_title}》的介绍，希望这本书能给您带来启发'}
        ]
    
    return processed_slides

def process_narrations_data(narrations_data, book_title):
    """处理解说词数据"""
    processed_narrations = []
    
    if isinstance(narrations_data, list) and len(narrations_data) > 0:
        for narration in narrations_data:
            if isinstance(narration, dict):
                # 提取主要解说内容
                content = (narration.get('main_narration', '') or 
                          narration.get('opening', '') or 
                          narration.get('content', '') or
                          str(narration))
                processed_narrations.append(content)
            else:
                processed_narrations.append(str(narration))
    
    # 如果没有有效数据，使用默认解说词
    if not processed_narrations:
        processed_narrations = [
            f'欢迎来到《{book_title}》的介绍，让我们一起探索这本书的精彩内容',
            f'让我们了解《{book_title}》的作者，以及创作这本书的背景和动机',
            f'《{book_title}》包含了丰富的内容和深刻的思考，值得我们仔细品味',
            f'通过深度解读，我们可以更好地理解《{book_title}》想要传达的信息',
            f'《{book_title}》不仅是一本书，更是对现实生活的深刻反思',
            f'感谢您观看《{book_title}》的介绍，希望这本书能给您带来收获和启发'
        ]
    
    return processed_narrations

def get_fallback_book_data(topic: str) -> dict:
    """当API配额用完时，返回默认的书籍数据"""
    return {
        "raw_content": f'''```json
{{
  "book_title": "{topic}",
  "author": "知名作者",
  "summary": [
    "《{topic}》是一部深受读者喜爱的经典作品。",
    "这本书通过生动的故事情节，展现了深刻的人生哲理。",
    "作品具有很强的现实意义和教育价值。"
  ],
  "core_ideas": [
    "探讨人生的意义和价值",
    "展现人性的复杂与美好",
    "传达积极向上的人生态度",
    "反思社会现象和人际关系"
  ],
  "target_audience": [
    "文学爱好者",
    "青年读者",
    "教育工作者",
    "对人生哲理感兴趣的读者"
  ],
  "value_and_significance": [
    "具有重要的文学价值和社会意义",
    "能够启发读者思考人生",
    "对当代文学发展有重要影响"
  ],
  "ppt_key_chapters_themes": [
    "作品背景与创作动机",
    "主要人物形象分析",
    "核心主题思想",
    "艺术特色与表现手法",
    "现实意义与启示",
    "读后感悟与思考"
  ]
}}
```'''
    }

def get_fallback_slides_data(book_title: str) -> list:
    """当API配额用完时，返回默认的幻灯片数据"""
    return [{
        "raw_content": f'''```json
[
  {{
    "slide_number": 1,
    "slide_type": "opening",
    "title": "{book_title}",
    "subtitle": "经典作品分享",
    "main_content": "一部值得深入阅读的优秀作品",
    "key_message": "开启文学之旅"
  }},
  {{
    "slide_number": 2,
    "slide_type": "author",
    "title": "作者介绍",
    "subtitle": "了解创作背景",
    "main_content": "深入了解作者的创作历程和文学成就",
    "key_message": "作者的文学世界"
  }},
  {{
    "slide_number": 3,
    "slide_type": "concept",
    "title": "核心主题",
    "subtitle": "思想内涵",
    "main_content": "探讨作品中蕴含的深刻思想和人生哲理",
    "key_message": "思想的力量"
  }},
  {{
    "slide_number": 4,
    "slide_type": "quote",
    "title": "经典语句",
    "subtitle": "文学之美",
    "main_content": "品味作品中的经典语句和优美表达",
    "key_message": "语言的魅力"
  }},
  {{
    "slide_number": 5,
    "slide_type": "summary",
    "title": "现实意义",
    "subtitle": "当代价值",
    "main_content": "《{book_title}》对当代读者的启发和意义",
    "key_message": "文学的永恒价值"
  }}
]
```'''
    }]

def get_fallback_narrations_data(book_title: str) -> list:
    """当API配额用完时，返回默认的解说词数据"""
    return [{
        "raw_content": f'''```json
[
  {{
    "slide_number": 1,
    "opening": "欢迎大家，今天我们来分享一部优秀的文学作品。",
    "main_narration": "《{book_title}》是一部深受读者喜爱的经典作品，它以独特的视角和深刻的思考，为我们展现了丰富的人生画卷。这部作品不仅具有很高的文学价值，更能给我们带来深刻的人生启示。",
    "key_emphasis": "一部值得反复阅读的经典之作",
    "transition": "让我们先来了解一下这部作品的作者。"
  }},
  {{
    "slide_number": 2,
    "opening": "了解作者，有助于我们更好地理解作品。",
    "main_narration": "作者以其深厚的文学功底和独特的创作风格，创作了这部令人印象深刻的作品。通过了解作者的创作背景和人生经历，我们能够更深入地理解作品所要表达的思想内涵。",
    "key_emphasis": "作者的人生阅历丰富了作品的内涵",
    "transition": "接下来，让我们探讨作品的核心主题。"
  }},
  {{
    "slide_number": 3,
    "opening": "每部优秀的作品都有其独特的思想内涵。",
    "main_narration": "《{book_title}》通过生动的故事情节和深刻的人物刻画，探讨了人生的意义、人性的复杂以及社会现象等重要主题。这些主题不仅具有普遍性，更能引发我们对现实生活的深入思考。",
    "key_emphasis": "思想的深度决定了作品的价值",
    "transition": "让我们来欣赏一些作品中的经典语句。"
  }},
  {{
    "slide_number": 4,
    "opening": "优美的语言是文学作品的重要特色。",
    "main_narration": "《{book_title}》在语言表达上具有独特的魅力，作者运用精练而富有诗意的语言，创造出许多令人难忘的经典语句。这些语句不仅展现了作者的文学功底，更能触动读者的心灵。",
    "key_emphasis": "语言的美感提升了阅读体验",
    "transition": "最后，让我们思考这部作品的现实意义。"
  }},
  {{
    "slide_number": 5,
    "opening": "优秀的文学作品总是具有跨越时代的价值。",
    "main_narration": "《{book_title}》虽然创作于特定的历史时期，但其所探讨的主题和思想在今天仍然具有重要的现实意义。它能够启发我们思考人生，指导我们的生活，这正是经典文学作品的永恒价值所在。",
    "key_emphasis": "经典作品的价值在于其永恒的启发意义",
    "transition": "感谢大家的聆听，希望这次分享能够激发大家对阅读的兴趣。"
  }}
]
```'''
    }]

# -----------------------------------------------------------------------
# 增强的流式生成器
# -----------------------------------------------------------------------

async def enhanced_llm_event_stream(
    topic: str,
    history: Optional[List[dict]] = None,
    model: str = QWEN_MODEL,
    user_id: Optional[int] = None,
    methodology: str = "dongyu_literature",
    voice_style: str = "professional_style",
    video_style: str = "classic_ppt",
    book_info: dict = None,
) -> AsyncGenerator[str, None]:
    """
    增强的流式生成器：支持方法论定制和语音生成
    """
    import asyncio  # 在函数开头导入，确保整个函数都能使用
    
    history = history or []
    book_info = book_info or {}
    
    # 生成唯一的会话ID用于保存文件
    import uuid
    session_id = str(uuid.uuid4())
    
    try:
        # 开始思考与规划阶段
        yield f"data: {json.dumps({'log': '🎭 增强生成模式启动...'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.5)
        
        book_title = book_info.get("title", "未知")
        yield f"data: {json.dumps({'log': f'📚 书籍：《{book_title}》'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': f'🎭 方法论：{methodology}'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': f'🎙️ 语音风格：{voice_style}'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': f'🎬 视频风格：{video_style}'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.5)
        
        yield f"data: {json.dumps({'log': '🎯 制定个性化生成策略...'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.3)
        
        yield f"data: {json.dumps({'log': '  ├─ 步骤1: 基于方法论分析书籍'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': '  ├─ 步骤2: 按风格设计PPT结构'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': '  ├─ 步骤3: 生成个性化解说词'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': '  ├─ 步骤4: 生成HTML和语音'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': '  └─ 步骤5: 后处理优化'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.5)
        
        # 步骤1：基于方法论提取书本数据 
        yield f"data: {json.dumps({'log': '🔍 [步骤1/5] 基于方法论分析书籍数据...'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': f'  ├─ 使用 {methodology} 方法论分析'}, ensure_ascii=False)}\n\n"
        
        # 构建方法论特定的提示词
        methodology_context = f"""
你正在使用 {methodology} 方法论来分析书籍《{book_info.get('title', '未知')}》。

请特别注意：
- 如果是董宇辉式方法论：注重情感共鸣、个人经历植入、古今中外引用
- 如果是罗振宇式方法论：强调认知升级、时代焦虑、方法论拆解
- 确保分析结果体现所选方法论的特色和风格
        """
        
        enhanced_topic = f"{topic}\n\n【方法论上下文】\n{methodology_context}"
        
        try:
            book_data = await step1_extract_book_data(enhanced_topic, methodology=methodology)
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "ConnectError" in str(e) or "SSL" in str(e) or "EOF" in str(e):
                yield f"data: {json.dumps({'log': '  ├─ ⚠️  API连接问题，使用备用数据'}, ensure_ascii=False)}\n\n"
                book_data = get_fallback_book_data(book_info.get('title', topic))
            else:
                yield f"data: {json.dumps({'log': f'  ├─ ⚠️  未知错误，使用备用数据: {str(e)}'}, ensure_ascii=False)}\n\n"
                book_data = get_fallback_book_data(book_info.get('title', topic))
        
        # 添加方法论信息到书籍数据
        if isinstance(book_data, dict):
            book_data['methodology'] = methodology
            book_data['voice_style'] = voice_style
            book_data['video_style'] = video_style
        
        book_title = book_info.get('title', topic)
        yield f"data: {json.dumps({'log': f'  ├─ 书籍分析完成: 《{book_title}》'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': '  └─ ✅ 方法论特色已融入分析'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.3)
        
        # 步骤2：基于风格创建PPT画面
        yield f"data: {json.dumps({'log': '🎨 [步骤2/5] 基于风格设计PPT结构...'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': f'  ├─ 应用 {video_style} 视频风格'}, ensure_ascii=False)}\n\n"
        
        try:
            slides_data = await step2_create_ppt_slides(book_data, methodology=methodology, video_style=video_style)
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "ConnectError" in str(e) or "SSL" in str(e) or "EOF" in str(e):
                yield f"data: {json.dumps({'log': '  ├─ ⚠️  API连接问题，使用备用幻灯片'}, ensure_ascii=False)}\n\n"
                slides_data = get_fallback_slides_data(book_title)
            else:
                yield f"data: {json.dumps({'log': f'  ├─ ⚠️  未知错误，使用备用幻灯片: {str(e)}'}, ensure_ascii=False)}\n\n"
                slides_data = get_fallback_slides_data(book_title)
        
        yield f"data: {json.dumps({'log': '  ├─ PPT结构设计完成'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': '  └─ ✅ 风格特色已体现'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.3)
        
        # 步骤3：生成个性化解说词
        yield f"data: {json.dumps({'log': '🎙️ [步骤3/5] 生成个性化解说词...'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': f'  ├─ 采用 {voice_style} 语音风格'}, ensure_ascii=False)}\n\n"
        
        try:
            narrations_data = await step3_create_narration(slides_data, book_data, methodology=methodology)
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "ConnectError" in str(e) or "SSL" in str(e) or "EOF" in str(e):
                yield f"data: {json.dumps({'log': '  ├─ ⚠️  API连接问题，使用备用解说词'}, ensure_ascii=False)}\n\n"
                narrations_data = get_fallback_narrations_data(book_title)
            else:
                yield f"data: {json.dumps({'log': f'  ├─ ⚠️  未知错误，使用备用解说词: {str(e)}'}, ensure_ascii=False)}\n\n"
                narrations_data = get_fallback_narrations_data(book_title)
        
        yield f"data: {json.dumps({'log': '  ├─ 个性化解说词生成完成'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': '  └─ ✅ 方法论风格已融入'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.3)
        
        # 步骤4：生成HTML和语音
        yield f"data: {json.dumps({'log': '🌐 [步骤4/5] 生成HTML演示文件...'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': '  ├─ 整合所有组件'}, ensure_ascii=False)}\n\n"
        
        # 组合所有数据
        combined_data = {
            "topic": topic,
            "book_data": book_data,
            "slides": slides_data,
            "narrations": narrations_data,
            "methodology": methodology,
            "voice_style": voice_style,
            "video_style": video_style
        }
        
        try:
            html_content = await step4_generate_html(slides_data, narrations_data, book_data, methodology=methodology, enable_voice=True, book_title=book_title)
        except Exception as e:
            yield f"data: {json.dumps({'log': f'  ├─ HTML生成遇到问题: {str(e)}'}, ensure_ascii=False)}\n\n"
            # 使用简化的HTML生成
            html_content = f"<html><body><h1>《{book_title}》</h1><p>演示文件生成中遇到问题，请稍后重试。</p></body></html>"
        
        yield f"data: {json.dumps({'log': '  ├─ HTML文件生成完成'}, ensure_ascii=False)}\n\n"
        
        # 步骤5：后处理优化（语音生成等）
        yield f"data: {json.dumps({'log': '🎵 [步骤5/5] 后处理优化...'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': '  ├─ 添加语音支持'}, ensure_ascii=False)}\n\n"
        
        # 保存文件
        output_dir = Path(f"outputs/{session_id}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存HTML文件
        html_file = output_dir / "presentation.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 语音生成集成（优化后重新启用）
        voice_generated = False
        
        try:
            if voice_style and voice_style != "no_voice":
                yield f"data: {json.dumps({'log': '  ├─ 正在生成语音文件...'}, ensure_ascii=False)}\n\n"
                
                # 导入语音生成器
                sys.path.append(str(Path(__file__).parent / "create"))
                from ppt_voice_generator import PPTVoiceGenerator
                
                # 初始化语音生成器
                voice_generator = PPTVoiceGenerator(
                    html_file=str(html_file),
                    audio_prefix=f"{session_id}_slide"
                )
                
                # 生成语音文件 - 设置超时保护
                try:
                    # 使用 asyncio.wait_for 设置超时
                    voice_results = await asyncio.wait_for(
                        asyncio.to_thread(voice_generator.generate_all_audio),
                        timeout=60.0  # 60秒超时
                    )
                    
                    if voice_results:
                        yield f"data: {json.dumps({'log': f'  ├─ ✅ 语音文件生成完成 ({len(voice_results)}个音频)'}, ensure_ascii=False)}\n\n"
                        # 创建播放列表
                        voice_generator.create_playlist(voice_results)
                        yield f"data: {json.dumps({'log': '  ├─ ✅ 播放列表创建完成'}, ensure_ascii=False)}\n\n"
                        voice_generated = True
                    else:
                        yield f"data: {json.dumps({'log': '  ├─ ⚠️ 语音生成完成但结果为空'}, ensure_ascii=False)}\n\n"
                
                except asyncio.TimeoutError:
                    yield f"data: {json.dumps({'log': '  ├─ ⚠️ 语音生成超时，跳过语音功能'}, ensure_ascii=False)}\n\n"
                
            else:
                yield f"data: {json.dumps({'log': '  ├─ ℹ️ 跳过语音生成（用户选择）'}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'log': f'  ├─ ⚠️ 语音生成失败: {str(e)}'}, ensure_ascii=False)}\n\n"
        
        yield f"data: {json.dumps({'log': '  ├─ 优化播放体验'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'log': '  └─ ✅ 后处理完成'}, ensure_ascii=False)}\n\n"
        
        # 保存数据文件
        data_file = output_dir / "data.json"
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, ensure_ascii=False, indent=2)
        
        # 返回成功结果
        yield f"data: {json.dumps({'log': '🎉 增强生成完成！', 'session_id': session_id}, ensure_ascii=False)}\n\n"
        
        result = {
            "status": "complete",
            "session_id": session_id,
            "html_url": f"/outputs/{session_id}/presentation.html",
            "methodology": methodology,
            "voice_style": voice_style,
            "video_style": video_style
        }
        
        yield f"data: {json.dumps(result, ensure_ascii=False)}\n\n"
        
    except Exception as e:
        print(f"Enhanced generation error: {e}")
        error_result = {
            "status": "error",
            "message": f"增强生成失败: {str(e)}"
        }
        yield f"data: {json.dumps(error_result, ensure_ascii=False)}\n\n"

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
    # 获取当前用户
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    
    accumulated_response = ""
    session_id = None

    async def event_generator():
        nonlocal accumulated_response, session_id
        try:
            async for chunk in llm_event_stream(chat_request.topic, chat_request.history, user_id=user.id):
                accumulated_response += chunk
                
                # 检查是否包含session_id
                if '"session_id"' in chunk:
                    try:
                        data = json.loads(chunk.replace('data: ', ''))
                        if 'session_id' in data:
                            session_id = data['session_id']
                    except:
                        pass
                
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

@app.post("/api/enhanced-generate")
async def enhanced_generate(
    request_data: EnhancedGenerateRequest,
    request: Request,
):
    """
    增强版生成端点：使用指定的方法论和风格配置
    """
    # 获取当前用户
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    
    try:
        # 初始化方法论配置
        try:
            config = MethodologyConfig()
        except:
            config = None
        
        # 构建书籍信息
        book_info = {
            "title": request_data.title,
            "author": request_data.author or "未知作者",
            "category": request_data.category or "文学类",
            "description": request_data.description or "",
            "user_intent": request_data.user_intent or ""
        }
        
        # 生成方法论特定的提示词
        if config:
            methodology_prompt = config.generate_methodology_prompt(
                request_data.methodology, 
                book_info
            )
        else:
            methodology_prompt = f"""
请使用 {request_data.methodology} 方法论来介绍书籍《{request_data.title}》。

**书籍信息：**
- 书名：{request_data.title}
- 作者：{request_data.author or '未知作者'}
- 分类：{request_data.category or '文学类'}

请根据所选方法论的特点来组织内容结构和表达方式。
            """
        
        # 创建增强的聊天请求 - 这里是关键，我们需要明确指示AI使用方法论
        enhanced_topic = f"""
请为书籍《{request_data.title}》生成一个专业的介绍演示。

**书籍基本信息：**
- 书名：{request_data.title}
- 作者：{request_data.author or '未知作者'}
- 分类：{request_data.category or '文学类'}
- 语言：{request_data.language}
{f"- 简介：{request_data.description}" if request_data.description else ""}
{f"- 特别要求：{request_data.user_intent}" if request_data.user_intent else ""}

**指定方法论：**
{methodology_prompt}

**风格配置：**
- 语音风格：{request_data.voice_style}
- 视频风格：{request_data.video_style}

请严格按照选定的方法论来组织内容结构和表达方式，确保生成的介绍具有该方法论的特色和风格。

**重要要求：**
1. 在生成slides内容时，必须体现所选方法论的核心特点
2. 在生成narrations时，必须采用对应的表达风格和语调
3. 确保生成的HTML包含data-speech属性以支持语音生成
4. 整体内容应该具有明显的方法论特色，而不是通用的介绍方式
        """
        
        # 使用增强的流式生成器
        async def enhanced_event_generator():
            session_id = None
            try:
                async for chunk in enhanced_llm_event_stream(
                    enhanced_topic, 
                    None,  # history
                    user_id=user.id,
                    methodology=request_data.methodology,
                    voice_style=request_data.voice_style,
                    video_style=request_data.video_style,
                    book_info=book_info
                ):
                    # 检查是否包含session_id
                    if '"session_id"' in chunk:
                        try:
                            import json
                            lines = chunk.strip().split('\n')
                            for line in lines:
                                if line.startswith('data: ') and '"session_id"' in line:
                                    data = json.loads(line[6:])
                                    if 'session_id' in data:
                                        session_id = data['session_id']
                                        # 保存增强配置到session
                                        await save_enhanced_config(session_id, request_data)
                                        break
                        except Exception as e:
                            print(f"解析session_id失败: {e}")
                    
                    yield chunk
                    await asyncio.sleep(0)  # 让出控制权

            except Exception as e:
                print(f"Enhanced generation error: {e}")
                error_data = {
                    "status": "error",
                    "message": f"生成过程中出现错误: {str(e)}"
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

        return StreamingResponse(
            enhanced_event_generator(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"增强生成失败: {str(e)}")

async def save_enhanced_config(session_id: str, config: EnhancedGenerateRequest):
    """保存增强配置到session目录"""
    try:
        session_dir = Path(f"outputs/{session_id}")
        if session_dir.exists():
            config_path = session_dir / "enhanced_config.json"
            config_data = {
                "methodology": config.methodology,
                "voice_style": config.voice_style,
                "video_style": config.video_style,
                "book_info": {
                    "title": config.title,
                    "author": config.author,
                    "category": config.category,
                    "language": config.language,
                    "description": config.description,
                    "user_intent": config.user_intent
                },
                "timestamp": datetime.now().isoformat()
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
                
    except Exception as e:
        print(f"保存增强配置失败: {e}")

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

@app.get("/outputs/{session_id}")
async def get_generated_content(session_id: str):
    """
    获取已生成的内容信息
    """
    import os
    output_dir = f"outputs/{session_id}"
    
    if not os.path.exists(output_dir):
        raise HTTPException(status_code=404, detail="会话不存在或内容未找到")
    
    files = []
    for filename in os.listdir(output_dir):
        file_path = os.path.join(output_dir, filename)
        if os.path.isfile(file_path):
            files.append({
                "name": filename,
                "size": os.path.getsize(file_path),
                "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
            })
    
    return {
        "session_id": session_id,
        "output_path": output_dir,
        "files": files,
        "html_url": f"/outputs/{session_id}/presentation.html"
    }

@app.get("/outputs/{session_id}/{filename}")
async def serve_generated_file(session_id: str, filename: str):
    """
    提供生成的文件访问，HTML文件在浏览器中打开，其他文件下载
    """
    import os
    from fastapi.responses import FileResponse
    
    file_path = os.path.join("outputs", session_id, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 根据文件类型设置不同的媒体类型
    if filename.endswith('.html'):
        # HTML文件在浏览器中打开（不设置filename参数避免下载）
        return FileResponse(
            path=file_path,
            media_type='text/html; charset=utf-8',
            headers={
                "Cache-Control": "no-cache",
                "Content-Disposition": "inline"  # 强制在浏览器中显示
            }
        )
    elif filename.endswith('.json'):
        # JSON文件在浏览器中显示
        return FileResponse(
            path=file_path,
            media_type='application/json; charset=utf-8',
            headers={"Content-Disposition": "inline"}
        )
    else:
        # 其他文件作为下载
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )

@app.post("/regenerate/{session_id}")
async def regenerate_ppt(session_id: str):
    """
    重新生成指定会话的PPT（使用新的模板）
    """
    import os
    
    # 检查会话是否存在
    data_file = os.path.join("outputs", session_id, "data.json")
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="会话数据不存在")
    
    # 读取原始数据
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 重新生成HTML
    html_content = await step4_generate_html(
        data['slides'], 
        data['narrations'], 
        data['book_data']
    )
    
    # 保存新的HTML文件
    html_file = os.path.join("outputs", session_id, "presentation.html")
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return {
        "message": "PPT重新生成完成",
        "session_id": session_id,
        "html_url": f"/outputs/{session_id}/presentation.html",
        "regenerated_at": datetime.now(shanghai_tz).isoformat()
    }



@app.get("/api/ppt-preview/{session_id}")
async def get_ppt_preview(session_id: str):
    """
    获取PPT预览信息
    """
    import os
    
    data_file = f"outputs/{session_id}/data.json"
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="PPT不存在")
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 解析数据
        book_data = data.get('book_data', {})
        slides_data = data.get('slides', [])
        
        parsed_book_data = parse_ai_response(book_data)
        parsed_slides = parse_ai_response(slides_data)
        
        book_title = extract_book_title(parsed_book_data)
        
        # 获取前3页幻灯片作为预览
        preview_slides = []
        if isinstance(parsed_slides, list):
            for i, slide in enumerate(parsed_slides[:3]):
                if isinstance(slide, dict):
                    preview_slides.append({
                        'title': slide.get('title', f'第{i+1}页'),
                        'subtitle': slide.get('subtitle', ''),
                        'content': slide.get('main_content', slide.get('content', ''))[:100] + '...'
                    })
        
        return {
            'session_id': session_id,
            'title': book_title,
            'topic': data.get('topic', ''),
            'preview_slides': preview_slides,
            'total_slides': len(parsed_slides) if isinstance(parsed_slides, list) else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取预览失败: {str(e)}")

@app.get("/api/generated-ppts")
async def get_generated_ppts(
    limit: int = 10, 
    page: int = 1, 
    category_id: str = None,
    search: str = None
):
    """获取已生成的PPT列表"""
    import os
    import json
    from pathlib import Path
    
    try:
        outputs_dir = Path("outputs")
        if not outputs_dir.exists():
            return {"ppts": []}
        
        ppt_list = []
        
        # 遍历outputs目录下的所有子目录
        for session_dir in outputs_dir.iterdir():
            if session_dir.is_dir():
                data_file = session_dir / "data.json"
                html_file = session_dir / "presentation.html"
                
                if data_file.exists() and html_file.exists():
                    try:
                        # 读取数据文件获取PPT信息
                        with open(data_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # 获取文件创建时间
                        created_time = datetime.fromtimestamp(
                            data_file.stat().st_ctime, 
                            tz=shanghai_tz
                        ).strftime("%Y-%m-%d %H:%M")
                        
                        # 获取封面信息
                        book_data = data.get("book_data", {})
                        cover_url = book_data.get("cover_url", get_default_book_cover(data.get("topic", "未知主题")))
                        
                        # 获取书名 - 优先从book_data中提取
                        title = data.get("topic", "未知主题")  # 默认值
                        if book_data:
                            # 尝试从book_data中提取书名
                            if 'title' in book_data:
                                title = book_data['title']
                            elif 'raw_content' in book_data:
                                # 尝试从raw_content中解析JSON获取书名
                                try:
                                    raw_content = book_data['raw_content']
                                    if 'title' in raw_content:
                                        import json as json_parser
                                        # 尝试解析JSON
                                        if raw_content.strip().startswith('```json'):
                                            json_start = raw_content.find('{')
                                            json_end = raw_content.rfind('}') + 1
                                            if json_start != -1 and json_end > json_start:
                                                parsed_data = json_parser.loads(raw_content[json_start:json_end])
                                                if 'book_info' in parsed_data and 'title' in parsed_data['book_info']:
                                                    title = parsed_data['book_info']['title']
                                except:
                                    pass
                            
                            # 如果还是原始的长文本，尝试从topic中提取书名
                            if len(title) > 100:
                                import re
                                # 尝试匹配《书名》格式
                                title_match = re.search(r'《([^》]+)》', title)
                                if title_match:
                                    title = title_match.group(1)
                                else:
                                    # 尝试匹配"书名："格式
                                    title_match = re.search(r'书名[：:]\s*([^\n\-]+)', title)
                                    if title_match:
                                        title = title_match.group(1).strip()
                                        title = re.sub(r'\s*-\s*作者.*$', '', title)
                                        title = re.sub(r'\s*-\s*分类.*$', '', title)
                                        title = title.strip()
                        
                        # 转换本地封面路径为URL
                        if cover_url.startswith('covers/'):
                            cover_url = f"/covers/{cover_url.replace('covers/', '')}"
                        
                        # 获取分类信息
                        ppt_category_id = book_data.get("category_id", "literature")
                        category_name = book_data.get("category_name", "文学类")
                        category_color = book_data.get("category_color", "#E74C3C")
                        category_icon = book_data.get("category_icon", "📖")
                        
                        ppt_info = {
                            "session_id": session_dir.name,
                            "title": title,
                            "created_time": created_time,
                            "html_url": f"/outputs/{session_dir.name}/presentation.html",
                            "preview_url": f"/ppt-preview/{session_dir.name}",
                            "cover_url": cover_url,
                            "category_id": ppt_category_id,
                            "category_name": category_name,
                            "category_color": category_color,
                            "category_icon": category_icon
                        }
                        
                        ppt_list.append(ppt_info)
                        
                    except (json.JSONDecodeError, KeyError) as e:
                        print(f"读取PPT数据失败: {session_dir.name}, 错误: {e}")
                        continue
        
        # 筛选功能
        if category_id:
            ppt_list = [ppt for ppt in ppt_list if ppt.get("category_id") == category_id]
        
        if search:
            search_lower = search.lower()
            ppt_list = [ppt for ppt in ppt_list if 
                       search_lower in ppt.get("title", "").lower() or 
                       search_lower in ppt.get("topic", "").lower()]
        
        # 按创建时间排序，最新的在前
        ppt_list.sort(key=lambda x: x["created_time"], reverse=True)
        
        # 分页功能
        total_count = len(ppt_list)
        total_pages = (total_count + limit - 1) // limit
        start_index = (page - 1) * limit
        end_index = start_index + limit
        paged_ppt_list = ppt_list[start_index:end_index]
        
        return {
            "ppts": paged_ppt_list,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_count": total_count,
                "per_page": limit
            }
        }
        
    except Exception as e:
        print(f"获取PPT列表失败: {e}")
        return {"error": str(e), "ppts": []}

@app.get("/ppt-preview/{session_id}", response_class=HTMLResponse)
async def get_ppt_preview(session_id: str):
    """获取PPT预览页面"""
    import os
    from pathlib import Path
    
    try:
        html_file = Path(f"outputs/{session_id}/presentation.html")
        if html_file.exists():
            with open(html_file, 'r', encoding='utf-8') as f:
                return HTMLResponse(content=f.read())
        else:
            raise HTTPException(status_code=404, detail="PPT文件不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取PPT文件失败: {str(e)}")

@app.get("/test_stream.html", response_class=HTMLResponse)
async def test_stream():
    """测试流数据的页面"""
    with open("test_stream.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/library", response_class=HTMLResponse)
async def library_page(request: Request):
    """图书馆页面"""
    return templates.TemplateResponse(
        "library.html", {
            "request": request,
            "time": datetime.now(shanghai_tz).strftime("%Y%m%d%H%M%S")
        }
    )

@app.get("/enhanced-generator", response_class=HTMLResponse)
async def enhanced_generator_page(request: Request):
    """增强版生成器页面"""
    return templates.TemplateResponse(
        "enhanced_generator.html", {
            "request": request,
            "time": datetime.now(shanghai_tz).strftime("%Y%m%d%H%M%S")
        }
    )

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse(
        "index.html", {
            "request": request,
            "time": datetime.now(shanghai_tz).strftime("%Y%m%d%H%M%S")})

@app.get("/debug", response_class=HTMLResponse)
async def debug_page():
    with open("test_frontend_debug.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/simple_switch_test.html", response_class=HTMLResponse)
async def simple_switch_test(request: Request):
    return templates.TemplateResponse(
        "simple_switch_test.html", {
            "request": request,
            "time": datetime.now(shanghai_tz).strftime("%Y%m%d%H%M%S")})

@app.get("/test-static-cover", response_class=HTMLResponse)
async def test_static_cover():
    """测试静态封面图片的页面"""
    with open("test_static_cover.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/test-cover/{filename}")
async def test_cover_direct(filename: str):
    """直接测试封面文件访问"""
    import os
    import urllib.parse
    from fastapi.responses import FileResponse
    
    # URL解码文件名
    decoded_filename = urllib.parse.unquote(filename)
    cover_path = os.path.join("covers", decoded_filename)
    
    print(f"测试路由 - 请求的文件: {filename}")
    print(f"测试路由 - 解码后的文件名: {decoded_filename}")
    print(f"测试路由 - 完整路径: {cover_path}")
    print(f"测试路由 - 文件是否存在: {os.path.exists(cover_path)}")
    
    if os.path.exists(cover_path):
        return FileResponse(cover_path, media_type="image/jpeg")
    else:
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=404, content={"error": f"Cover image not found: {decoded_filename}"})

@app.get("/covers/{filename}")
async def serve_cover_image(filename: str):
    """服务covers目录中的图片文件"""
    import os
    import urllib.parse
    from fastapi.responses import FileResponse
    
    # URL解码文件名
    decoded_filename = urllib.parse.unquote(filename)
    cover_path = os.path.join("covers", decoded_filename)
    
    print(f"请求的文件: {filename}")
    print(f"解码后的文件名: {decoded_filename}")
    print(f"完整路径: {cover_path}")
    print(f"文件是否存在: {os.path.exists(cover_path)}")
    
    if os.path.exists(cover_path):
        return FileResponse(cover_path, media_type="image/jpeg")
    else:
        # 如果文件不存在，返回404
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=404, content={"error": f"Cover image not found: {decoded_filename}"})

@app.get("/ppt_audio/{filename}")
async def serve_audio_file(filename: str):
    """提供音频文件服务"""
    try:
        from fastapi.responses import FileResponse
        import os
        
        audio_file_path = os.path.join("ppt_audio", filename)
        
        # 检查文件是否存在
        if not os.path.exists(audio_file_path):
            raise HTTPException(status_code=404, detail=f"音频文件未找到: {filename}")
        
        return FileResponse(
            path=audio_file_path,
            media_type="audio/mpeg",
            headers={"Cache-Control": "public, max-age=3600"}
        )
    except Exception as e:
        print(f"提供音频文件失败: {e}")
        raise HTTPException(status_code=500, detail="音频文件服务错误")

# -----------------------------------------------------------------------
# 分类管理API端点
# -----------------------------------------------------------------------

@app.get("/api/categories")
async def get_categories():
    """
    获取所有分类统计信息
    """
    try:
        categories = get_categories_summary()
        return {
            "success": True,
            "categories": categories
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# 方法论配置API端点
# -----------------------------------------------------------------------

@app.get("/api/methodologies")
async def get_methodologies():
    """获取所有可用的介绍方法论"""
    try:
        config = MethodologyConfig()
        methodologies = config.get_all_methodologies()
        return {
            "success": True,
            "methodologies": methodologies
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "methodologies": []
        }

@app.get("/api/methodologies/suitable")
async def get_suitable_methodologies(category: str):
    """根据书籍分类获取合适的方法论"""
    try:
        config = MethodologyConfig()
        suitable = config.get_suitable_methodologies(category)
        return {
            "success": True,
            "methodologies": suitable
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "methodologies": []
        }

@app.get("/api/voice-styles")
async def get_voice_styles():
    """获取可用的语音风格"""
    try:
        styles = VoiceConfig.get_voice_styles()
        return {
            "success": True,
            "styles": styles
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "styles": {}
        }

@app.get("/api/video-styles")
async def get_video_styles():
    """获取可用的视频风格"""
    try:
        styles = VideoConfig.get_video_styles()
        return {
            "success": True,
            "styles": styles
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "styles": {}
        }

@app.get("/api/books")
async def get_books(category_id: str = None, search: str = None):
    """
    获取书籍列表，支持按分类筛选和搜索
    """
    try:
        if category_id:
            books = get_books_by_category_id(category_id)
        elif search:
            books = search_books_by_keyword(search)
        else:
            books = get_all_books_with_categories()
        
        return {
            "success": True,
            "books": books,
            "total": len(books)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/categories/{category_id}/books")
async def get_books_by_category(category_id: str):
    """
    获取指定分类的书籍
    """
    try:
        books = get_books_by_category_id(category_id)
        return {
            "success": True,
            "category_id": category_id,
            "books": books,
            "total": len(books)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/export-video")
async def export_video(request: VideoExportRequest):
    """导出PPT演示视频"""
    try:
        # 验证session_id和相关文件是否存在
        html_file_path = Path(f"outputs/{request.session_id}/{request.html_file}")
        if not html_file_path.exists():
            raise HTTPException(status_code=404, detail="演示文件不存在")
        
        # 检查音频文件是否存在
        audio_dir = Path("ppt_audio")
        if not audio_dir.exists():
            raise HTTPException(status_code=404, detail="音频文件目录不存在")
        
        # 动态导入视频生成器
        sys.path.append(str(Path("create").absolute()))
        from universal_ppt_video_generator import UniversalPPTVideoGenerator
        
        # 在项目根目录运行，传入完整的HTML文件路径
        full_html_path = str(html_file_path.absolute())
        
        # 创建视频生成器实例
        generator = UniversalPPTVideoGenerator(
            html_file=full_html_path,
            audio_prefix=request.audio_prefix
        )
        
        # 修改生成器的音频目录和输出目录
        generator.audio_dir = Path("ppt_audio")
        generator.output_dir = Path(f"outputs/{request.session_id}")
        
        # 检查依赖
        if not generator.check_dependencies():
            raise HTTPException(status_code=500, detail="系统依赖不满足，请检查FFmpeg和Chrome是否安装")
        
        # 生成视频
        result = generator.generate_video()
        
        if result and result.exists():
            # 获取视频信息
            file_size = result.stat().st_size / (1024 * 1024)  # MB
            
            # 获取视频时长
            duration = 0
            try:
                duration_result = subprocess.run([
                    "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                    "-of", "csv=p=0", str(result)
                ], capture_output=True, text=True)
                if duration_result.returncode == 0:
                    duration = float(duration_result.stdout.strip())
            except:
                pass
            
            # 返回成功响应
            return {
                "success": True,
                "video_url": f"/outputs/{request.session_id}/{result.name}",
                "filename": result.name,
                "file_size": f"{file_size:.1f} MB",
                "duration": f"{duration:.1f}",
                "message": "视频生成成功"
            }
        else:
            return {
                "success": False,
                "error": "视频生成失败，请检查音频文件是否存在"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"视频生成错误：{str(e)}"
        }

# -----------------------------------------------------------------------
# 认证相关依赖和中间件
# -----------------------------------------------------------------------

security = HTTPBearer()

async def get_current_user(request: Request):
    """获取当前用户"""
    # 首先尝试从cookie获取session token
    session_token = request.cookies.get("session_token")
    if session_token:
        user = user_manager.get_user_by_session(session_token)
        if user:
            return user
    
    # 如果没有session，尝试从Authorization header获取JWT token
    try:
        credentials: HTTPAuthorizationCredentials = Depends(security)
        token = credentials.credentials
        username = verify_token(token)
        if username:
            user = user_manager.get_user_by_username(username)
            if user:
                return user
    except:
        pass
    
    return None

async def require_auth(request: Request):
    """要求认证的依赖"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# -----------------------------------------------------------------------
# 认证相关路由
# -----------------------------------------------------------------------

@app.post("/api/register")
async def register(user_data: UserCreate):
    """用户注册"""
    # 验证输入
    if len(user_data.username) < 3:
        raise HTTPException(status_code=400, detail="用户名至少需要3个字符")
    
    if len(user_data.password) < 6:
        raise HTTPException(status_code=400, detail="密码至少需要6个字符")
    
    # 创建用户
    user = user_manager.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password
    )
    
    if not user:
        raise HTTPException(status_code=400, detail="用户名或邮箱已存在")
    
    # 创建session
    session_token = user_manager.create_session(user.id)
    
    response = {
        "success": True,
        "message": "注册成功",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at,
            "last_login": user.last_login
        }
    }
    
    # 设置cookie
    from fastapi.responses import JSONResponse
    json_response = JSONResponse(content=response)
    json_response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=86400,  # 24小时
        samesite="lax"
    )
    
    return json_response

@app.post("/api/login")
async def login(user_data: UserLogin):
    """用户登录"""
    user = user_manager.authenticate_user(user_data.username, user_data.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 创建session
    session_token = user_manager.create_session(user.id)
    
    response = {
        "success": True,
        "message": "登录成功",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at,
            "last_login": user.last_login
        }
    }
    
    # 设置cookie
    from fastapi.responses import JSONResponse
    json_response = JSONResponse(content=response)
    json_response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=86400,  # 24小时
        samesite="lax"
    )
    
    return json_response

@app.post("/api/logout")
async def logout(request: Request):
    """用户登出"""
    session_token = request.cookies.get("session_token")
    if session_token:
        user_manager.delete_session(session_token)
    
    response = {"success": True, "message": "登出成功"}
    
    # 清除cookie
    from fastapi.responses import JSONResponse
    json_response = JSONResponse(content=response)
    json_response.delete_cookie(key="session_token")
    
    return json_response

@app.get("/api/user")
async def get_current_user_info(request: Request):
    """获取当前用户信息"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    
    return {
        "success": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at,
            "last_login": user.last_login
        }
    }

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """登录页面"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """注册页面"""
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/bookshelf", response_class=HTMLResponse)
async def bookshelf_page(request: Request):
    """个人书架页面"""
    return templates.TemplateResponse(
        "bookshelf.html", {
            "request": request,
            "time": datetime.now(shanghai_tz).strftime("%Y%m%d%H%M%S")
        }
    )

@app.get("/recommendations", response_class=HTMLResponse)
async def recommendations_page(request: Request):
    """推荐页面"""
    return templates.TemplateResponse(
        "recommendations.html", {
            "request": request,
            "time": datetime.now(shanghai_tz).strftime("%Y%m%d%H%M%S")
        }
    )

@app.get("/recommendation-agent", response_class=HTMLResponse)
async def recommendation_agent_page(request: Request):
    """引导推荐代理页面"""
    return templates.TemplateResponse(
        "recommendation_agent.html", {
            "request": request,
            "time": datetime.now(shanghai_tz).strftime("%Y%m%d%H%M%S")
        }
    )

@app.get("/api/user-ppts")
async def get_user_ppts(
    request: Request,
    limit: int = 20, 
    page: int = 1, 
    category_id: str = None,
    search: str = None
):
    """获取当前用户的PPT列表"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    
    try:
        from models import user_manager
        result = user_manager.get_user_ppts(
            user_id=user.id,
            limit=limit,
            page=page,
            category_id=category_id,
            search=search
        )
        return result
    except Exception as e:
        print(f"获取用户PPT列表失败: {e}")
        return {"error": str(e), "ppts": []}

@app.delete("/api/user-ppts/{session_id}")
async def delete_user_ppt(session_id: str, request: Request):
    """删除用户的PPT"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    
    try:
        from models import user_manager
        success = user_manager.delete_user_ppt(session_id, user.id)
        if success:
            return {"message": "PPT删除成功"}
        else:
            raise HTTPException(status_code=404, detail="PPT不存在或无权限删除")
    except Exception as e:
        print(f"删除PPT失败: {e}")
        raise HTTPException(status_code=500, detail="删除失败")

@app.get("/api/recommendations")
async def get_recommendations(request: Request, limit: int = 10):
    """获取用户推荐书籍"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    
    try:
        from models import user_manager
        recommendations = user_manager.get_recommendations_for_user(user.id, limit)
        return {"recommendations": recommendations}
    except Exception as e:
        print(f"获取推荐失败: {e}")
        return {"recommendations": []}

@app.get("/api/books/search")
async def search_books_api(title: str = None, author: str = None, search: str = None):
    """书籍搜索API"""
    try:
        # 构建搜索关键词
        search_term = search or ""
        if title:
            search_term += f" {title}"
        if author:
            search_term += f" {author}"
        
        search_term = search_term.strip()
        
        if search_term:
            books = search_books_by_keyword(search_term)
        else:
            books = get_all_books_with_categories()
        
        return {
            "success": True,
            "books": books,
            "total": len(books)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "books": []
        }

@app.post("/api/recommendation/start")
async def start_recommendation_session(request: Request):
    """开始引导推荐会话"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    
    try:
        # 这里可以集成 guided_recommendation_agent.py 的功能
        # 目前返回基本响应
        return {
            "success": True,
            "message": "你好！我是你的私人阅读顾问。让我先了解一下你的阅读情况...",
            "user_profile": {
                "reading_frequency": "未知",
                "preferred_categories": [],
                "current_life_stage": "分析中"
            },
            "user_info": {
                "username": user.username,
                "id": user.id
            }
        }
    except Exception as e:
        print(f"启动推荐会话失败: {e}")
        raise HTTPException(status_code=500, detail="启动推荐会话失败")

@app.get("/api/user")
async def get_current_user_info(request: Request):
    """获取当前用户信息"""
    try:
        user = await get_current_user(request)
        if user:
            return {
                "success": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": getattr(user, 'email', '')
                }
            }
        else:
            return {"success": False, "user": None}
    except Exception as e:
        print(f"获取用户信息失败: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/user-preferences")
async def get_user_preferences(request: Request):
    """获取用户偏好"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    
    try:
        from models import user_manager
        preferences = user_manager.get_user_preferences(user.id)
        return {"preferences": preferences}
    except Exception as e:
        print(f"获取用户偏好失败: {e}")
        return {"preferences": {}}

@app.get("/api/popular-books/{category_name}")
async def get_popular_books_by_category(
    category_name: str, 
    request: Request, 
    limit: int = 10
):
    """获取指定分类的热门书籍"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    
    try:
        from models import user_manager
        books = user_manager.get_popular_books_by_category(
            category_name, 
            exclude_user_id=user.id, 
            limit=limit
        )
        return {"books": books}
    except Exception as e:
        print(f"获取热门书籍失败: {e}")
        return {"books": []}

@app.post("/api/add-book-to-bookshelf")
async def add_book_to_bookshelf(request: Request):
    """添加书籍到用户书架"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    
    try:
        data = await request.json()
        title = data.get("title")
        author = data.get("author")
        cover_url = data.get("cover_url")
        category_id = data.get("category_id")
        category_name = data.get("category_name")
        category_color = data.get("category_color")
        category_icon = data.get("category_icon")
        source_type = data.get("source_type", "library")
        source_id = data.get("source_id")
        
        if not title:
            raise HTTPException(status_code=400, detail="书籍标题不能为空")
        
        from models import user_manager
        
        # 检查书籍是否已在书架中
        if user_manager.check_book_in_bookshelf(user.id, title, author):
            return {"success": False, "message": "该书籍已在您的书架中"}
        
        # 添加书籍到书架
        session_id = user_manager.add_book_to_bookshelf(
            user_id=user.id,
            title=title,
            author=author,
            cover_url=cover_url,
            category_id=category_id,
            category_name=category_name,
            category_color=category_color,
            category_icon=category_icon,
            source_type=source_type,
            source_id=source_id
        )
        
        if session_id:
            return {"success": True, "message": "书籍已添加到书架", "session_id": session_id}
        else:
            raise HTTPException(status_code=500, detail="添加书籍失败")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"添加书籍到书架失败: {e}")
        raise HTTPException(status_code=500, detail="添加书籍失败")

@app.get("/api/check-book-in-bookshelf")
async def check_book_in_bookshelf(
    request: Request,
    title: str,
    author: str = None
):
    """检查书籍是否已在用户书架中"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    
    try:
        from models import user_manager
        is_in_bookshelf = user_manager.check_book_in_bookshelf(user.id, title, author)
        return {"in_bookshelf": is_in_bookshelf}
    except Exception as e:
        print(f"检查书籍是否在书架中失败: {e}")
        return {"in_bookshelf": False}

# -----------------------------------------------------------------------
# 访谈功能API路由
# -----------------------------------------------------------------------
from interview_dialogue import get_dialogue_engine
from interview_content_processor import get_podcast_generator

class InterviewStartRequest(BaseModel):
    """访谈开始请求"""
    book_title: str
    book_author: str
    user_intro: str

class InterviewMessageRequest(BaseModel):
    """访谈消息请求"""
    session_id: str
    message: str

class InterviewGenerateRequest(BaseModel):
    """访谈生成请求"""
    session_id: str

@app.post("/api/interview/start")
async def start_interview(request: InterviewStartRequest):
    """开始访谈"""
    try:
        engine = get_dialogue_engine()
        result = engine.start_interview(
            request.book_title,
            request.book_author,
            request.user_intro
        )
        return result
    except Exception as e:
        print(f"开始访谈失败: {e}")
        raise HTTPException(status_code=500, detail="开始访谈失败")

@app.post("/api/interview/message")
async def send_interview_message(request: InterviewMessageRequest):
    """发送访谈消息"""
    try:
        engine = get_dialogue_engine()
        result = await engine.process_user_message(
            request.session_id,
            request.message
        )
        return result
    except Exception as e:
        print(f"处理访谈消息失败: {e}")
        raise HTTPException(status_code=500, detail="处理消息失败")

@app.post("/api/interview/generate-podcast")
async def generate_interview_podcast(request: InterviewGenerateRequest):
    """生成访谈播客"""
    try:
        generator = get_podcast_generator()
        result = await generator.generate_podcast_content(request.session_id)
        return result
    except Exception as e:
        print(f"生成播客失败: {e}")
        raise HTTPException(status_code=500, detail="生成播客失败")

@app.get("/api/interview/session/{session_id}")
async def get_interview_session(session_id: str):
    """获取访谈会话信息"""
    try:
        from interview_user_model import get_session
        session = get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        engine = get_dialogue_engine()
        summary = engine.get_session_summary(session_id)
        return summary
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取会话信息失败: {e}")
        raise HTTPException(status_code=500, detail="获取会话信息失败")

@app.get("/api/book-info")
async def get_book_info(title: str, author: str = None):
    """获取书籍扩展信息"""
    try:
        import sqlite3
        import os
        import json
        
        # 查询数据库中的PPT信息 (注意表名是ppts，不是presentations)
        query = """
        SELECT 
            session_id, title, author, category_name, cover_url, created_at
        FROM ppts 
        WHERE title LIKE ? 
        """
        params = [f"%{title}%"]
        
        if author:
            query += " AND author LIKE ?"
            params.append(f"%{author}%")
            
        query += " ORDER BY created_at DESC LIMIT 1"
        
        conn = sqlite3.connect("users.db")
        try:
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            
            if row:
                session_id = row[0]
                ppt_title = row[1]
                ppt_author = row[2]
                category_name = row[3]
                cover_url = row[4]
                created_at = row[5]
                
                # 检查对应的PPT文件是否存在
                ppt_path = f"outputs/{session_id}/presentation.html"
                data_path = f"outputs/{session_id}/data.json"
                
                ppt_exists = os.path.exists(ppt_path)
                description = f"关于《{ppt_title}》的深度解读"
                
                # 如果data.json存在，尝试读取更详细的信息
                if os.path.exists(data_path):
                    try:
                        with open(data_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            book_data = data.get('book_data', {})
                            raw_content = book_data.get('raw_content', '')
                            if 'content_summary' in raw_content:
                                # 提取简介信息
                                import re
                                summary_match = re.search(r'"content_summary":\s*\[(.*?)\]', raw_content, re.DOTALL)
                                if summary_match:
                                    description = "这是一部经典文学作品..."
                    except:
                        pass
                
                return {
                    "id": session_id,
                    "title": ppt_title,
                    "author": ppt_author or "未知作者",
                    "category": category_name or "未分类",
                    "description": description,
                    "created_at": created_at,
                    "cover_url": cover_url,
                    "ppt_exists": ppt_exists,
                    "ppt_url": f"/outputs/{session_id}/presentation.html" if ppt_exists else None,
                    "interview_count": 1,  # 至少有一次访问记录
                    "podcast_count": 0,
                    "source": "library"
                }
            else:
                # 如果数据库中没有，返回默认信息
                return {
                    "title": title,
                    "author": author or "未知作者",
                    "category": "文学作品",
                    "description": f"关于《{title}》的深度访谈",
                    "created_at": datetime.now(shanghai_tz).isoformat(),
                    "ppt_exists": False,
                    "ppt_url": None,
                    "interview_count": 0,
                    "podcast_count": 0,
                    "source": "new"
                }
        finally:
            conn.close()
                
    except Exception as e:
        print(f"获取书籍信息失败: {e}")
        # 返回默认信息而不是抛出错误
        return {
            "title": title,
            "author": author or "未知作者",
            "category": "未分类",
            "description": f"关于《{title}》的深度访谈",
            "created_at": datetime.now(shanghai_tz).isoformat(),
            "ppt_exists": False,
            "ppt_url": None,
            "interview_count": 0,
            "podcast_count": 0,
            "source": "error"
        }

@app.get("/interview", response_class=HTMLResponse)
async def interview_page(request: Request, book_title: str = None, book_author: str = None):
    """读后感访谈页面"""
    # 尝试从数据库中查找对应的书籍信息
    book_info = None
    if book_title:
        try:
            import sqlite3
            conn = sqlite3.connect('fogsight.db')
            cursor = conn.cursor()
            
            # 查找书籍信息
            cursor.execute("""
                SELECT session_id, title, author, cover_url, category_name, created_at 
                FROM presentations 
                WHERE title LIKE ? OR (author LIKE ? AND title LIKE ?)
                ORDER BY created_at DESC 
                LIMIT 1
            """, (f'%{book_title}%', f'%{book_author}%' if book_author else '%', f'%{book_title}%'))
            
            result = cursor.fetchone()
            if result:
                session_id, title, author, cover_url, category_name, created_at = result
                book_info = {
                    'session_id': session_id,
                    'title': title,
                    'author': author,
                    'cover_url': cover_url,
                    'category': category_name,
                    'created_at': created_at,
                    'found_in_library': True
                }
            conn.close()
        except Exception as e:
            print(f"查询书籍信息失败: {e}")
    
    return templates.TemplateResponse(
        "interview.html", {
            "request": request,
            "time": datetime.now(shanghai_tz).strftime("%Y%m%d%H%M%S"),
            "book_title": book_title,
            "book_author": book_author,
            "book_info": book_info,
            "book_cover": book_info['cover_url'] if book_info else None,
            "book_description": f"关于《{book_title}》的深度访谈" if book_title else "开始你的读后感访谈"
        }
    )

# -----------------------------------------------------------------------
# 4. 本地启动命令
# -----------------------------------------------------------------------
# uvicorn appbook:app --reload --host 0.0.0.0 --port 8000


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
