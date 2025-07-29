import asyncio
import json
import httpx
import re
import os
from datetime import datetime
from typing import AsyncGenerator, List, Optional

import pytz
from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI, OpenAIError
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google import genai

# 导入认证相关模块
from models import UserManager, UserCreate, UserLogin, UserResponse, user_manager, verify_token

# -----------------------------------------------------------------------
# 0. 配置
# -----------------------------------------------------------------------
shanghai_tz = pytz.timezone("Asia/Shanghai")

credentials = json.load(open("credentials.json"))
API_KEY = credentials["API_KEY"]
BASE_URL = credentials.get("BASE_URL", "")

# 配置Qwen模型客户端
QWEN_BASE_URL = "https://api-inference.modelscope.cn/v1/"
QWEN_API_KEY = "ms-076e7668-1000-4ce8-be4e-f475ddfeead7"  # ModelScope Token
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
    基于书名生成一个简单的封面样式
    """
    # 根据书名长度和内容选择不同的默认样式
    title_length = len(book_title)
    
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
        
        # 搜索书籍封面
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
            
            # 搜索封面
            cover_url = await search_book_cover(book_title, author)
            book_data['cover_url'] = cover_url
            
        except Exception as cover_error:
            print(f"搜索封面失败: {cover_error}")
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

async def step2_create_ppt_slides(book_data: dict) -> list:
    """
    第2步：创建PPT画面结构（苹果发布会风格）
    """
    system_prompt = f"""基于以下书籍数据，设计苹果发布会风格的PPT画面结构：

{json.dumps(book_data, ensure_ascii=False, indent=2)}

请为这本书设计6-10页苹果风格PPT的画面结构，每页包含：

## 苹果发布会PPT页面类型：
1. **开场页** - 书名大标题，简洁背景
2. **作者介绍页** - 作者信息，优雅布局
3. **核心观点页** - 单一重点，大字体展示
4. **数据展示页** - 关键数字，视觉化呈现
5. **引用页** - 书中金句，艺术化排版
6. **总结页** - 核心价值，call-to-action

每页PPT请包含以下结构：
- slide_number: 页面编号
- slide_type: 页面类型 (opening/author/concept/data/quote/summary)
- title: 主标题（3-8个字）
- subtitle: 副标题（可选）
- main_content: 核心内容
- visual_elements: 视觉元素配置
- animation_entrance: 入场动画类型
- key_message: 核心信息

设计原则：
- 每页只传达一个核心概念
- 使用大量留白
- 字体层级清晰
- 颜色搭配和谐
- 符合苹果美学

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

async def step3_create_narration(slides: list, book_data: dict) -> list:
    """
    第3步：为每页PPT创建解说词（苹果发布会风格）
    """
    system_prompt = f"""基于以下PPT画面结构和书籍数据，为每页PPT创建苹果发布会风格的解说词：

书籍数据：
{json.dumps(book_data, ensure_ascii=False, indent=2)}

PPT画面结构：
{json.dumps(slides, ensure_ascii=False, indent=2)}

请为每页PPT创建苹果发布会风格的解说词：

## 苹果发布会解说风格特点：
1. **开场方式**：
   - 简洁有力的开场
   - 直接切入主题
   - 制造期待感

2. **表达方式**：
   - 简洁明了，避免冗长
   - 使用数据和事实说话
   - 情感化的语言
   - 适当的停顿和强调

3. **结构模式**：
   - 问题设定 → 解决方案 → 价值体现
   - 现状描述 → 改进展示 → 结果呈现

每页解说词包含：
- slide_number: 页面编号
- opening: 开场白（1-2句话，吸引注意）
- main_narration: 主要解说内容（2-3分钟，深入浅出）
- key_emphasis: 重点强调的内容（金句或核心观点）
- transition: 过渡语（连接下一页）
- timing: 时间控制信息
- tone: 语调风格

解说词要求：
- 模仿苹果发布会的表达风格
- 语言简洁有力，富有感染力
- 结合书籍内容，但保持通俗易懂
- 适合现场演讲的节奏
- 包含适当的情感渲染

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

async def step4_generate_html(slides: list, narrations: list, book_data: dict) -> str:
    """
    第4步：将画面和解说词转换为HTML格式（苹果发布会风格）
    """
    system_prompt = f"""基于以下数据，生成一个完整的HTML格式PPT，采用苹果发布会的设计风格：

书籍数据：
{json.dumps(book_data, ensure_ascii=False, indent=2)}

PPT画面：
{json.dumps(slides, ensure_ascii=False, indent=2)}

解说词：
{json.dumps(narrations, ensure_ascii=False, indent=2)}

**重要要求：必须实现真正的分页PPT效果，每次只显示一页内容，而不是把所有页面都显示在一个页面上！**

## 正确的HTML结构示例：
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>书籍介绍PPT</title>
    <style>
        body {{ margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }}
        .presentation-container {{ position: relative; width: 100vw; height: 100vh; overflow: hidden; }}
        .slide {{ 
            position: absolute; 
            width: 100%; 
            height: 100%; 
            display: flex; 
            flex-direction: column; 
            justify-content: center; 
            align-items: center;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.5s ease;
        }}
        .slide.active {{ opacity: 1; transform: translateX(0); }}
        .slide.prev {{ transform: translateX(-100%); }}
    </style>
</head>
<body>
    <div class="presentation-container">
        <!-- 每个slide都是独立的，通过JavaScript控制显示 -->
        <div class="slide active" data-slide="0">第1页内容</div>
        <div class="slide" data-slide="1">第2页内容</div>
        <div class="slide" data-slide="2">第3页内容</div>
        <!-- 更多页面... -->
    </div>
    <div class="navigation">
        <button onclick="prevSlide()">←</button>
        <div class="dots"></div>
        <button onclick="nextSlide()">→</button>
    </div>
    <div class="narration-panel">解说词区域</div>
    <script>
        let currentSlide = 0;
        const slides = document.querySelectorAll('.slide');
        const totalSlides = slides.length;
        
        function showSlide(n) {{
            slides.forEach(slide => slide.classList.remove('active', 'prev'));
            if (n >= 0 && n < totalSlides) {{
                slides[n].classList.add('active');
                currentSlide = n;
                updateNarration(n);
                updateDots(n);
            }}
        }}
        
        function nextSlide() {{ showSlide(currentSlide + 1); }}
        function prevSlide() {{ showSlide(currentSlide - 1); }}
        
        // 键盘导航
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'ArrowRight') nextSlide();
            if (e.key === 'ArrowLeft') prevSlide();
        }});
    </script>
</body>
</html>
```

## 关键实现要点：

1. **分页显示逻辑**：
   - 使用 `position: absolute` 让所有slide重叠
   - 通过 `opacity` 和 `transform` 控制显示/隐藏
   - 只有当前页面 `opacity: 1`，其他页面 `opacity: 0`

2. **页面切换动画**：
   - 使用 CSS `transition` 实现平滑切换
   - 当前页面：`transform: translateX(0)`
   - 下一页：`transform: translateX(100%)`  
   - 上一页：`transform: translateX(-100%)`

3. **JavaScript控制**：
   - `currentSlide` 变量跟踪当前页面
   - `showSlide(n)` 函数切换到指定页面
   - 键盘事件监听（左右箭头键）
   - 导航点击事件

4. **苹果风格设计**：
   - 纯白背景 (#FFFFFF)
   - 苹果蓝强调色 (#007AFF)
   - SF Pro 字体系列
   - 圆角和阴影效果
   - 毛玻璃效果

5. **解说词同步**：
   - 每次切换页面时更新解说词内容
   - 解说词面板固定位置显示

**请严格按照这个结构生成HTML，确保实现真正的分页效果，而不是滚动浏览所有内容！**

**重要：必须生成完整的HTML文件，包含完整的JavaScript代码，确保文件以</html>结尾！**

## 完整的工作示例模板：

请基于以下完整的工作模板生成HTML，确保所有功能都能正常工作，并且HTML文件必须完整：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>书籍PPT</title>
    <style>
        body {{ margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #FFFFFF; color: #1D1D1F; overflow: hidden; }}
        .presentation-container {{ position: relative; width: 100vw; height: 100vh; overflow: hidden; }}
        .slide {{ position: absolute; width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; opacity: 0; transform: translateX(100%); transition: all 0.5s ease; padding: 40px; box-sizing: border-box; text-align: center; }}
        .slide.active {{ opacity: 1; transform: translateX(0); }}
        .slide h1 {{ font-size: 4rem; font-weight: 300; margin-bottom: 20px; }}
        .slide h2 {{ font-size: 2rem; font-weight: 400; color: #86868B; margin-bottom: 30px; }}
        .slide p {{ font-size: 1.5rem; line-height: 1.6; max-width: 800px; }}
        .navigation {{ position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%); display: flex; align-items: center; z-index: 1000; }}
        .navigation button {{ background: #007AFF; color: white; border: none; padding: 12px 24px; margin: 0 15px; border-radius: 25px; cursor: pointer; font-size: 1.2rem; }}
        .navigation button:disabled {{ background: #86868B; cursor: not-allowed; }}
        .dot {{ width: 12px; height: 12px; border-radius: 50%; background: rgba(255,255,255,0.5); margin: 0 6px; cursor: pointer; }}
        .dot.active {{ background: #007AFF; }}
        .narration-panel {{ position: fixed; top: 30px; right: 30px; width: 350px; background: rgba(255,255,255,0.9); backdrop-filter: blur(20px); border-radius: 16px; padding: 20px; z-index: 1000; }}
    </style>
</head>
<body>
    <div class="presentation-container">
        <!-- 根据slides数据生成每一页 -->
    </div>
    <div class="navigation">
        <button id="prevButton" onclick="prevSlide()">← 上一页</button>
        <div class="dots" id="dotsContainer"></div>
        <button id="nextButton" onclick="nextSlide()">下一页 →</button>
    </div>
    <div class="narration-panel" id="narrationPanel">解说词区域</div>
    <script>
        let currentSlide = 0;
        const slides = document.querySelectorAll('.slide');
        const totalSlides = slides.length;
        
        // 生成导航点
        const dotsContainer = document.getElementById('dotsContainer');
        for (let i = 0; i < totalSlides; i++) {{
            const dot = document.createElement('div');
            dot.classList.add('dot');
            if (i === 0) dot.classList.add('active');
            dot.addEventListener('click', () => showSlide(i));
            dotsContainer.appendChild(dot);
        }}
        
        function showSlide(n) {{
            if (n < 0 || n >= totalSlides) return;
            slides.forEach(slide => slide.classList.remove('active'));
            slides[n].classList.add('active');
            currentSlide = n;
            updateUI(n);
        }}
        
        function nextSlide() {{ if (currentSlide < totalSlides - 1) showSlide(currentSlide + 1); }}
        function prevSlide() {{ if (currentSlide > 0) showSlide(currentSlide - 1); }}
        
        function updateUI(n) {{
            document.getElementById('prevButton').disabled = n === 0;
            document.getElementById('nextButton').disabled = n === totalSlides - 1;
            document.querySelectorAll('.dot').forEach((dot, i) => dot.classList.toggle('active', i === n));
            // 更新解说词
        }}
        
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'ArrowRight') nextSlide();
            if (e.key === 'ArrowLeft') prevSlide();
        }});
        
        updateUI(0);
    </script>
</body>
</html>
```

**关键要求：**
1. 必须生成完整的HTML文件，从<!DOCTYPE html>到</html>
2. 必须使用 `position: absolute` 让所有slide重叠
3. 只有当前slide有 `active` 类，其他都是 `opacity: 0`
4. 导航按钮必须能正常工作
5. 键盘导航必须响应
6. 解说词必须同步更新
7. 每页内容根据提供的数据动态生成
8. JavaScript代码必须完整，包含所有必要的函数
9. 确保HTML结构完整，没有未闭合的标签
"""

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

    # 不再使用AI生成，直接使用可靠的模板
    return generate_reliable_ppt_html_internal(slides, narrations, book_data)

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
            title = topic
            author = "未知作者"
            
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

def generate_reliable_ppt_html_internal(slides, narrations, book_data):
    """生成可靠的PPT HTML（内置函数，确保完整性）"""
    
    # 解析book_data
    parsed_book_data = parse_ai_response(book_data)
    book_title = extract_book_title(parsed_book_data)
    
    # 获取书籍封面
    cover_url = ""
    # 首先从原始book_data中获取cover_url
    if isinstance(book_data, dict):
        cover_url = book_data.get('cover_url', '')
    # 如果原始数据中没有，再从解析后的数据中获取
    if not cover_url and isinstance(parsed_book_data, dict):
        cover_url = parsed_book_data.get('cover_url', '')
    
    # 解析slides数据
    parsed_slides = parse_ai_response(slides)
    processed_slides = process_slides_data(parsed_slides, book_title)
    
    # 解析narrations数据
    parsed_narrations = parse_ai_response(narrations)
    processed_narrations = process_narrations_data(parsed_narrations, book_title)
    
    # 确保slides和narrations数量匹配
    while len(processed_narrations) < len(processed_slides):
        processed_narrations.append(f'这是第{len(processed_narrations)+1}页的解说内容')
    
    # 生成幻灯片HTML
    slides_html = ""
    for i, slide in enumerate(processed_slides):
        active_class = "active" if i == 0 else ""
        
        # 如果是封面页，显示封面
        if i == 0:
            if cover_url and (cover_url.startswith('http') or cover_url.startswith('covers/')):
                # 有真实封面图片（URL或本地文件）
                if cover_url.startswith('covers/'):
                    # 本地文件，需要转换为静态文件URL
                    static_url = f"/covers/{cover_url.replace('covers/', '')}"
                else:
                    # 远程URL
                    static_url = cover_url
                
                slides_html += f'''
        <div class="slide {active_class}" data-slide="{i}">
            <div class="cover-container">
                <div class="book-cover">
                    <img src="{static_url}" alt="{book_title}" class="cover-image">
                </div>
                <div class="cover-text">
                    <h1>{slide.get('title', book_title)}</h1>
                    <h2>{slide.get('subtitle', '')}</h2>
                </div>
            </div>
        </div>'''
            else:
                # 没有真实封面，显示默认封面
                slides_html += f'''
        <div class="slide {active_class}" data-slide="{i}">
            <div class="cover-container">
                <div class="book-cover">
                    <div class="default-cover">
                        <div class="default-cover-title">{book_title}</div>
                    </div>
                </div>
                <div class="cover-text">
                    <h1>{slide.get('title', book_title)}</h1>
                    <h2>{slide.get('subtitle', '')}</h2>
                </div>
            </div>
        </div>'''
        else:
            slides_html += f'''
        <div class="slide {active_class}" data-slide="{i}">
            <h1>{slide.get('title', f'第{i+1}页')}</h1>
            <h2>{slide.get('subtitle', '')}</h2>
            <p>{slide.get('content', '')}</p>
        </div>'''
    
    # 生成解说词JavaScript数组
    narrations_js = "[\n"
    for narration in processed_narrations:
        # 转义引号和换行符
        escaped_narration = str(narration).replace('"', '\\"').replace('\n', '\\n')
        narrations_js += f'        "{escaped_narration}",\n'
    narrations_js += "    ]"
    
    html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{book_title} - PPT演示</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #1D1D1F;
            overflow: hidden;
        }}
        
        .presentation-container {{
            position: relative;
            width: 100vw;
            height: 100vh;
            overflow: hidden;
        }}
        
        .slide {{
            position: absolute;
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            padding: 40px;
            box-sizing: border-box;
            text-align: center;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            margin: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }}
        
        .slide.active {{
            opacity: 1;
            transform: translateX(0);
        }}
        
        /* 开场页特殊样式 */
        .slide[data-slide="0"] {{
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.9) 100%);
        }}
        
        .slide[data-slide="0"] h1 {{
            font-size: 5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        /* 封面页样式 */
        .cover-container {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 60px;
            width: 100%;
            height: 100%;
        }}
        
        .book-cover {{
            flex-shrink: 0;
            width: 300px;
            height: 400px;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            transform: perspective(1000px) rotateY(-15deg);
            transition: transform 0.3s ease;
        }}
        
        .book-cover:hover {{
            transform: perspective(1000px) rotateY(-5deg) scale(1.05);
        }}
        
        .cover-image {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        .cover-text {{
            flex: 1;
            max-width: 500px;
            text-align: left;
        }}
        
        .cover-text h1 {{
            font-size: 4rem;
            font-weight: 700;
            margin-bottom: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .cover-text h2 {{
            font-size: 1.5rem;
            font-weight: 400;
            color: #86868B;
            margin-bottom: 30px;
        }}
        
        /* 默认封面样式（当没有真实封面时） */
        .default-cover {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            text-align: center;
            padding: 40px;
            box-sizing: border-box;
        }}
        
        .default-cover::before {{
            content: "📚";
            font-size: 4rem;
            margin-bottom: 20px;
        }}
        
        .default-cover-title {{
            font-size: 1.5rem;
            line-height: 1.3;
            word-break: break-word;
        }}
        
        /* 引用页特殊样式 */
        .slide[data-slide="3"] p {{
            font-size: 2rem;
            font-style: italic;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            border-left: 4px solid #667eea;
        }}
        
        /* 总结页特殊样式 */
        .slide[data-slide="6"] {{
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        }}
        
        .slide h1 {{
            font-size: 4rem;
            font-weight: 700;
            margin-bottom: 20px;
            color: #1D1D1F;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .slide h2 {{
            font-size: 2rem;
            font-weight: 500;
            color: #86868B;
            margin-bottom: 30px;
            opacity: 0.8;
        }}
        
        .slide p {{
            font-size: 1.5rem;
            line-height: 1.6;
            max-width: 800px;
            color: #1D1D1F;
            background: rgba(255, 255, 255, 0.8);
            padding: 20px 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        }}
        
        .navigation {{
            position: fixed;
            bottom: 100px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            align-items: center;
            z-index: 1000;
        }}
        
        .navigation button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #FFFFFF;
            border: none;
            padding: 12px 24px;
            margin: 0 15px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1.2rem;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }}
        
        .navigation button:hover {{
            background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }}
        
        .navigation button:disabled {{
            background-color: #86868B;
            cursor: not-allowed;
            transform: none;
        }}
        
        .dots {{
            display: flex;
            margin: 0 20px;
        }}
        
        .dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: rgba(255, 255, 255, 0.5);
            margin: 0 6px;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .dot.active {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            transform: scale(1.2);
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        }}
        
        .narration-panel {{
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            width: 80%;
            max-width: 800px;
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.9) 100%);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 12px 40px rgba(102, 126, 234, 0.15);
            font-size: 1rem;
            line-height: 1.6;
            color: #1D1D1F;
            z-index: 1000;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .slide-counter {{
            position: fixed;
            top: 30px;
            left: 30px;
            background-color: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 10px 15px;
            border-radius: 20px;
            font-size: 1rem;
            z-index: 1000;
        }}
        
        .back-home-button {{
            position: fixed;
            top: 30px;
            right: 30px;
            background-color: rgba(0, 0, 0, 0.7);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 20px;
            font-size: 1rem;
            cursor: pointer;
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
        }}
        
        .back-home-button:hover {{
            background-color: rgba(0, 0, 0, 0.8);
            transform: translateY(-2px);
        }}
        
        .back-home-button svg {{
            width: 16px;
            height: 16px;
        }}
    </style>
</head>
<body>
    <div class="presentation-container">{slides_html}
    </div>
    
    <div class="slide-counter">
        <span id="currentSlideNum">1</span> / <span id="totalSlideNum">{len(processed_slides)}</span>
    </div>
    
    <button class="back-home-button" onclick="goBackHome()">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M19 12H5"/>
            <path d="M12 19l-7-7 7-7"/>
        </svg>
        返回首页
    </button>
    
    <div class="navigation">
        <button id="prevButton" onclick="prevSlide()">← 上一页</button>
        <div class="dots" id="dotsContainer"></div>
        <button id="nextButton" onclick="nextSlide()">下一页 →</button>
    </div>
    
    <div class="narration-panel" id="narrationPanel">
        <strong>解说词：</strong><br>
        {processed_narrations[0] if processed_narrations else '欢迎观看PPT演示'}
    </div>
    
    <script>
        // 解说词数据
        const narrations = {narrations_js};
        
        let currentSlide = 0;
        const slides = document.querySelectorAll('.slide');
        const totalSlides = slides.length;
        const dotsContainer = document.getElementById('dotsContainer');
        const prevButton = document.getElementById('prevButton');
        const nextButton = document.getElementById('nextButton');
        const narrationPanel = document.getElementById('narrationPanel');
        const currentSlideNum = document.getElementById('currentSlideNum');
        const totalSlideNum = document.getElementById('totalSlideNum');
        
        // 初始化
        totalSlideNum.textContent = totalSlides;
        
        // 生成导航点
        for (let i = 0; i < totalSlides; i++) {{
            const dot = document.createElement('div');
            dot.classList.add('dot');
            if (i === 0) dot.classList.add('active');
            dot.addEventListener('click', () => showSlide(i));
            dotsContainer.appendChild(dot);
        }}
        
        function showSlide(n) {{
            // 边界检查
            if (n < 0 || n >= totalSlides) return;
            
            // 移除所有活动状态
            slides.forEach(slide => slide.classList.remove('active'));
            
            // 设置当前页面
            slides[n].classList.add('active');
            currentSlide = n;
            
            // 更新UI
            updateNarration(n);
            updateDots(n);
            updateNavigationButtons();
            updateSlideCounter(n);
        }}
        
        function nextSlide() {{
            if (currentSlide < totalSlides - 1) {{
                showSlide(currentSlide + 1);
            }}
        }}
        
        function prevSlide() {{
            if (currentSlide > 0) {{
                showSlide(currentSlide - 1);
            }}
        }}
        
        function updateNavigationButtons() {{
            prevButton.disabled = currentSlide === 0;
            nextButton.disabled = currentSlide === totalSlides - 1;
        }}
        
        function updateDots(n) {{
            const dots = document.querySelectorAll('.dot');
            dots.forEach((dot, index) => {{
                dot.classList.toggle('active', index === n);
            }});
        }}
        
        function updateNarration(slideIndex) {{
            if (narrations[slideIndex]) {{
                narrationPanel.innerHTML = `<strong>解说词：</strong><br>${{narrations[slideIndex]}}`;
            }}
        }}
        
        function updateSlideCounter(n) {{
            currentSlideNum.textContent = n + 1;
        }}
        
        // 键盘导航
        document.addEventListener('keydown', (e) => {{
            switch(e.key) {{
                case 'ArrowRight':
                case ' ':
                    e.preventDefault();
                    nextSlide();
                    break;
                case 'ArrowLeft':
                    e.preventDefault();
                    prevSlide();
                    break;
                case 'Home':
                    e.preventDefault();
                    showSlide(0);
                    break;
                case 'End':
                    e.preventDefault();
                    showSlide(totalSlides - 1);
                    break;
            }}
        }});
        
        // 返回首页函数
        function goBackHome() {{
            // 返回到主应用页面
            window.location.href = '/';
        }}
        
        // 初始化显示
        updateNavigationButtons();
        console.log('PPT初始化完成，共', totalSlides, '页');
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
                            "title": data.get("topic", "未知主题"),
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
# 4. 本地启动命令
# -----------------------------------------------------------------------
# uvicorn appbook:app --reload --host 0.0.0.0 --port 8000


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
