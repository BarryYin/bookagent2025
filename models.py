"""
书籍介绍系统 - 数据模型
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid
import sqlite3
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, EmailStr
import jwt

# 基础数据模型
@dataclass
class BookInfo:
    """书籍基本信息"""
    title: str
    author: str
    isbn: Optional[str] = None
    genre: Optional[str] = None
    publication_year: Optional[int] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None

@dataclass
class Review:
    """书籍评价"""
    source: str
    rating: float
    content: str
    date: Optional[datetime] = None
    reviewer: str = "匿名"

@dataclass
class StructuredInfo:
    """结构化的书籍信息"""
    book_details: BookInfo
    reviews_summary: str
    key_themes: List[str]
    target_audience: str
    strengths: List[str]
    criticisms: List[str]

# PPT相关数据模型
@dataclass
class VisualElement:
    """PPT中的视觉元素"""
    type: str  # 'image', 'chart', 'quote', etc.
    content: str
    style: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Slide:
    """PPT幻灯片"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    content: str = ""
    visual_elements: List[VisualElement] = field(default_factory=list)
    layout_type: str = "standard"
    notes: str = ""

@dataclass
class SlidesStructure:
    """PPT整体结构"""
    title_slide: Slide
    content_slides: List[Slide]
    summary_slide: Slide
    total_slides: int = 0

    def __post_init__(self):
        self.total_slides = len(self.content_slides) + 2  # 标题页 + 内容页 + 总结页

@dataclass
class SlidesContent:
    """完整的PPT内容"""
    structure: SlidesStructure
    slides: List[Slide]
    theme: str
    duration_estimate: int  # 预计演示时长(秒)

# 演讲稿相关数据模型
@dataclass
class SpeechScript:
    """幻灯片演讲稿"""
    slide_id: str
    text: str
    duration_estimate: float  # 预计时长(秒)
    emphasis_points: List[str] = field(default_factory=list)

# 样式相关数据模型
@dataclass
class ColorScheme:
    """配色方案"""
    primary: str
    secondary: str
    accent: str
    background: str
    text: str

@dataclass
class FontConfig:
    """字体配置"""
    heading_font: str
    body_font: str
    heading_size: str
    body_size: str

@dataclass
class StyleConfig:
    """样式配置"""
    theme_name: str
    color_scheme: ColorScheme
    font_config: FontConfig
    animation_level: str = "moderate"  # 'none', 'subtle', 'moderate', 'dynamic'
    layout_density: str = "balanced"   # 'compact', 'balanced', 'spacious'

# 音频相关数据模型
@dataclass
class AudioData:
    """音频数据"""
    slide_id: str
    content: bytes
    format: str
    duration: float
    start_time: float = 0.0

# 处理上下文
@dataclass
class ProcessContext:
    """处理上下文，在各阶段之间传递数据"""
    book_info: BookInfo
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    structured_info: Optional[StructuredInfo] = None
    guidewords: Optional[str] = None
    ppt_content: Optional[SlidesContent] = None
    speech_scripts: Optional[List[SpeechScript]] = None
    style_config: Optional[StyleConfig] = None
    html_content: Optional[str] = None
    audio_files: Optional[List[AudioData]] = None
    current_output: Any = None
    final_result: Optional[Dict[str, Any]] = None

# API请求/响应模型
@dataclass
class BookIntroductionRequest:
    """书籍介绍生成请求"""
    book_title: str
    author: str
    isbn: Optional[str] = None
    additional_info: Optional[str] = None
    style_preference: str = "professional"
    language: str = "zh"
    agent_type: str = "exploration"  # 新增：智能体类型 (recommendation, exploration, interview)

@dataclass
class GenerationProgress:
    """生成进度信息"""
    session_id: str
    current_stage: str
    progress_percentage: float
    stage_output: Optional[str] = None
    estimated_remaining_time: Optional[int] = None

@dataclass
class BookIntroductionResult:
    """书籍介绍生成结果"""
    session_id: str
    html_content: str
    audio_files: List[str]
    metadata: Dict[str, Any]
    download_url: str

# 数据库配置
DATABASE_PATH = "fogsight.db"

class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    password_hash: str
    created_at: Optional[str] = None
    last_login: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: str
    last_login: Optional[str] = None

class TokenData(BaseModel):
    username: Optional[str] = None

# JWT配置
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def init_database():
    """初始化数据库"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # 创建sessions表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # 创建PPT表，关联用户
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ppts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            author TEXT,
            cover_url TEXT,
            category_id TEXT,
            category_name TEXT,
            category_color TEXT,
            category_icon TEXT,
            book_type TEXT DEFAULT 'generated',  -- 'generated' 或 'added'
            source_type TEXT DEFAULT 'self',      -- 'self', 'library', 'recommendation'
            source_id TEXT,                       -- 来源ID（如果是从图书馆或推荐添加的）
            view_count INTEGER DEFAULT 0,         -- 访问次数
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # 为现有的ppts表添加view_count字段（如果不存在）
    try:
        cursor.execute('ALTER TABLE ppts ADD COLUMN view_count INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        # 字段已存在，忽略错误
        pass
    
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    """密码加密"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """验证密码"""
    return hash_password(password) == hashed

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """验证JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except jwt.PyJWTError:
        return None

@dataclass
class BookViewRecord:
    """书籍浏览记录"""
    title: str
    author: Optional[str]
    first_viewed_at: datetime

class UserManager:
    def __init__(self):
        init_database()
    
    def get_user_view_history(self, user_id: int, limit: int = 10) -> List[BookViewRecord]:
        """获取用户的书籍浏览历史（基于PPT的浏览记录）"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            # 让返回结果可以通过列名访问
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 使用 updated_at 作为最近浏览时间的代理
            cursor.execute('''
                SELECT title, author, updated_at
                FROM ppts
                WHERE user_id = ? AND view_count > 0
                ORDER BY updated_at DESC
                LIMIT ?
            ''', (user_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            history = []
            for row in rows:
                history.append(BookViewRecord(
                    title=row['title'],
                    author=row['author'],
                    first_viewed_at=datetime.fromisoformat(row['updated_at'])
                ))
            
            return history
        except Exception as e:
            print(f"获取用户浏览历史错误: {e}")
            return []
    
    def create_user(self, username: str, email: str, password: str) -> Optional[User]:
        """创建新用户"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            password_hash = hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            ''', (username, email, password_hash))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return User(
                id=user_id,
                username=username,
                email=email,
                password_hash=password_hash,
                created_at=datetime.now().isoformat()
            )
        except sqlite3.IntegrityError:
            return None  # 用户名或邮箱已存在
        except Exception as e:
            print(f"创建用户错误: {e}")
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """验证用户"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, email, password_hash, created_at, last_login
                FROM users WHERE username = ?
            ''', (username,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row and verify_password(password, row[3]):
                # 更新最后登录时间
                self.update_last_login(row[0])
                
                return User(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    password_hash=row[3],
                    created_at=row[4],
                    last_login=row[5]
                )
            return None
        except Exception as e:
            print(f"验证用户错误: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, email, password_hash, created_at, last_login
                FROM users WHERE username = ?
            ''', (username,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return User(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    password_hash=row[3],
                    created_at=row[4],
                    last_login=row[5]
                )
            return None
        except Exception as e:
            print(f"获取用户错误: {e}")
            return None
    
    def update_last_login(self, user_id: int):
        """更新用户最后登录时间"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (user_id,))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"更新登录时间错误: {e}")
    
    def create_session(self, user_id: int) -> str:
        """创建用户session"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=24)
            
            cursor.execute('''
                INSERT INTO sessions (user_id, session_token, expires_at)
                VALUES (?, ?, ?)
            ''', (user_id, session_token, expires_at))
            
            conn.commit()
            conn.close()
            
            return session_token
        except Exception as e:
            print(f"创建session错误: {e}")
            return None
    
    def get_user_by_session(self, session_token: str) -> Optional[User]:
        """根据session token获取用户"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT u.id, u.username, u.email, u.password_hash, u.created_at, u.last_login
                FROM users u
                JOIN sessions s ON u.id = s.user_id
                WHERE s.session_token = ? AND s.expires_at > CURRENT_TIMESTAMP
            ''', (session_token,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return User(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    password_hash=row[3],
                    created_at=row[4],
                    last_login=row[5]
                )
            return None
        except Exception as e:
            print(f"获取session用户错误: {e}")
            return None
    
    def delete_session(self, session_token: str):
        """删除session"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM sessions WHERE session_token = ?', (session_token,))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"删除session错误: {e}")
    
    def cleanup_expired_sessions(self):
        """清理过期的sessions"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM sessions WHERE expires_at < CURRENT_TIMESTAMP')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"清理过期sessions错误: {e}")
    
    def add_ppt(self, session_id: str, user_id: int, title: str, author: str = None, 
                cover_url: str = None, category_id: str = None, category_name: str = None,
                category_color: str = None, category_icon: str = None, book_type: str = 'generated',
                source_type: str = 'self', source_id: str = None):
        """添加PPT到数据库"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO ppts 
                (session_id, user_id, title, author, cover_url, category_id, category_name, category_color, category_icon, book_type, source_type, source_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session_id, user_id, title, author, cover_url, category_id, category_name, category_color, category_icon, book_type, source_type, source_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"添加PPT错误: {e}")
            return False
    
    def get_user_ppts(self, user_id: int, limit: int = 20, page: int = 1, 
                      category_id: str = None, search: str = None):
        """获取用户的PPT列表"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            # 构建查询条件
            where_conditions = ["user_id = ?"]
            params = [user_id]
            
            if category_id:
                where_conditions.append("category_id = ?")
                params.append(category_id)
            
            if search:
                where_conditions.append("(title LIKE ? OR author LIKE ?)")
                search_param = f"%{search}%"
                params.extend([search_param, search_param])
            
            where_clause = " AND ".join(where_conditions)
            
            # 获取总数
            cursor.execute(f'''
                SELECT COUNT(*) FROM ppts WHERE {where_clause}
            ''', params)
            total_count = cursor.fetchone()[0]
            
            # 获取分页数据
            offset = (page - 1) * limit
            cursor.execute(f'''
                SELECT session_id, title, author, cover_url, category_id, category_name, 
                       category_color, category_icon, book_type, source_type, source_id, created_at, view_count
                FROM ppts 
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', params + [limit, offset])
            
            rows = cursor.fetchall()
            conn.close()
            
            ppts = []
            for row in rows:
                ppts.append({
                    "session_id": row[0],
                    "title": row[1],
                    "author": row[2],
                    "cover_url": row[3],
                    "category_id": row[4],
                    "category_name": row[5],
                    "category_color": row[6],
                    "category_icon": row[7],
                    "book_type": row[8],
                    "source_type": row[9],
                    "source_id": row[10],
                    "created_at": row[11],
                    "view_count": row[12] or 0,
                    "html_url": f"/outputs/{row[0]}/presentation.html",
                    "preview_url": f"/ppt-preview/{row[0]}"
                })
            
            total_pages = (total_count + limit - 1) // limit
            
            return {
                "ppts": ppts,
                "pagination": {
                    "current_page": page,
                    "total_pages": total_pages,
                    "total_count": total_count,
                    "per_page": limit
                }
            }
        except Exception as e:
            print(f"获取用户PPT列表错误: {e}")
            return {"ppts": [], "pagination": {"current_page": 1, "total_pages": 0, "total_count": 0, "per_page": limit}}
    
    def delete_user_ppt(self, session_id: str, user_id: int):
        """删除用户的PPT"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM ppts WHERE session_id = ? AND user_id = ?
            ''', (session_id, user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"删除PPT错误: {e}")
            return False

    def get_user_preferences(self, user_id: int) -> dict:
        """获取用户偏好（基于个人书架中书籍的浏览次数加权统计）"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 使用 SUM(view_count + 1) 作为加权统计，浏览次数越多的书，权重越高
            cursor.execute("""
                SELECT category_name, SUM(view_count + 1) as weight
                FROM ppts 
                WHERE user_id = ? AND category_name IS NOT NULL
                GROUP BY category_name 
                ORDER BY weight DESC
            """, (user_id,))
            
            preferences = {}
            for row in cursor.fetchall():
                preferences[row['category_name']] = row['weight']
            
            conn.close()
            return preferences
        except Exception as e:
            print(f"获取用户偏好时出错: {e}")
            return {}

    def get_popular_books_by_category(self, category_name: str, limit: int = 10) -> list:
        """获取指定分类的热门书籍（按浏览次数排序）"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = f"""
                SELECT session_id, title, author, cover_url, category_name, 
                       category_color, category_icon, created_at, view_count
                FROM ppts 
                WHERE category_name = ?
                ORDER BY view_count DESC, created_at DESC
                LIMIT ?
            """
            
            cursor.execute(query, (category_name, limit))
            
            books = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return books
        except Exception as e:
            print(f"获取热门书籍时出错: {e}")
            return []

    def get_recommendations_for_user(self, user_id: int, limit: int = 10) -> list:
        """为用户生成推荐书籍, 包含多层备用逻辑确保永不为空."""
        try:
            # 1. 获取用户书架上所有书籍的ID，用于后续过滤
            user_books_on_shelf = self.get_user_ppts(user_id, limit=1000) # 获取用户所有书
            shelf_session_ids = {book['session_id'] for book in user_books_on_shelf.get('ppts', [])}

            # 2. 获取用户偏好
            preferences = self.get_user_preferences(user_id)
            
            final_recommendations = []

            # 3. 主要逻辑：基于偏好推荐
            if preferences:
                potential_recommendations = []
                total_weight = sum(preferences.values())
                for category, weight in preferences.items():
                    category_limit = max(3, int((weight / total_weight) * limit * 1.5))
                    books = self.get_popular_books_by_category(category, category_limit)
                    potential_recommendations.extend(books)
                
                # 过滤掉用户已有的书籍
                for book in potential_recommendations:
                    if len(final_recommendations) >= limit: break
                    if book['session_id'] not in shelf_session_ids:
                        final_recommendations.append(book)

            # 4. 备用逻辑1：如果个性化推荐结果为空（比如偏好分类下没有新书），启动“探索”模式
            if not final_recommendations:
                print(f"Personalized recommendations failed for user {user_id}. Triggering Fallback 1: Exploration.")
                conn = sqlite3.connect(DATABASE_PATH)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT session_id, title, author, cover_url, category_name, view_count, created_at
                    FROM ppts
                    WHERE category_name NOT IN (SELECT DISTINCT category_name FROM ppts WHERE user_id = ?)
                    ORDER BY view_count DESC, created_at DESC
                    LIMIT ?
                """, (user_id, limit * 2))
                
                fallback_books = [dict(row) for row in cursor.fetchall()]
                conn.close()
                
                for book in fallback_books:
                    if len(final_recommendations) >= limit: break
                    if book['session_id'] not in shelf_session_ids:
                        final_recommendations.append(book)

            # 5. 备用逻辑2：如果“探索”模式也失败（比如用户已涉足所有分类），启动“全站热门”模式
            if not final_recommendations:
                print(f"Fallback 1 failed for user {user_id}. Triggering Fallback 2: Global Hot.")
                conn = sqlite3.connect(DATABASE_PATH)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT session_id, title, author, cover_url, category_name, view_count, created_at
                    FROM ppts
                    ORDER BY view_count DESC, created_at DESC
                    LIMIT ?
                """, (limit * 5,)) # 拉取足够多的数据以供过滤
                
                global_hot_books = [dict(row) for row in cursor.fetchall()]
                conn.close()

                for book in global_hot_books:
                    if len(final_recommendations) >= limit: break
                    if book['session_id'] not in shelf_session_ids:
                        final_recommendations.append(book)

            # 6. 去重并返回
            seen_ids = set()
            unique_recommendations = []
            for book in final_recommendations:
                if book['session_id'] not in seen_ids:
                    unique_recommendations.append(book)
                    seen_ids.add(book['session_id'])

            return unique_recommendations[:limit]
            
        except Exception as e:
            print(f"生成推荐时出错: {e}")
            return []

    def record_book_view(self, session_id: str):
        """记录书籍浏览次数"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE ppts SET view_count = view_count + 1 
                WHERE session_id = ?
            ''', (session_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"记录浏览次数错误: {e}")
            return False
    
    def get_ppt_view_count(self, session_id: str) -> int:
        """获取PPT的访问次数"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT view_count FROM ppts WHERE session_id = ?
            ''', (session_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0] or 0
            else:
                return 0
        except Exception as e:
            print(f"获取访问次数错误: {e}")
            return 0
    
    def add_book_to_bookshelf(self, user_id: int, title: str, author: str = None, 
                             cover_url: str = None, category_id: str = None, 
                             category_name: str = None, category_color: str = None, 
                             category_icon: str = None, source_type: str = 'library', 
                             source_id: str = None):
        """添加书籍到用户书架"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            # 生成唯一的session_id
            session_id = str(uuid.uuid4())
            
            cursor.execute('''
                INSERT INTO ppts 
                (session_id, user_id, title, author, cover_url, category_id, category_name, 
                 category_color, category_icon, book_type, source_type, source_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'added', ?, ?)
            ''', (session_id, user_id, title, author, cover_url, category_id, category_name, 
                  category_color, category_icon, source_type, source_id))
            
            conn.commit()
            conn.close()
            return session_id
        except Exception as e:
            print(f"添加书籍到书架错误: {e}")
            return None
    
    def check_book_in_bookshelf(self, user_id: int, title: str, author: str = None) -> bool:
        """检查书籍是否已在用户书架中"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            if author:
                cursor.execute('''
                    SELECT COUNT(*) FROM ppts 
                    WHERE user_id = ? AND title = ? AND author = ?
                ''', (user_id, title, author))
            else:
                cursor.execute('''
                    SELECT COUNT(*) FROM ppts 
                    WHERE user_id = ? AND title = ?
                ''', (user_id, title))
            
            count = cursor.fetchone()[0]
            conn.close()
            return count > 0
        except Exception as e:
            print(f"检查书籍是否在书架中错误: {e}")
            return False

# 全局用户管理器实例
user_manager = UserManager()