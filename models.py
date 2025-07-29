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
DATABASE_PATH = "users.db"

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

class UserManager:
    def __init__(self):
        init_database()
    
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

# 全局用户管理器实例
user_manager = UserManager()