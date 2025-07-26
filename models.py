"""
书籍介绍系统 - 数据模型
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid

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