"""
用户阅读状态识别与建模模块
"""
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel
import re

class UserReadingProfile(BaseModel):
    """用户阅读画像"""
    user_id: str
    age_group: str  # 年龄段：teenager, young_adult, adult, middle_aged, senior
    profession: str  # 职业：student, teacher, engineer, manager, etc.
    reading_experience: str  # 阅读经验：beginner, intermediate, advanced
    expression_style: str  # 表达风格：analytical, emotional, creative, practical
    cognitive_pattern: str  # 认知模式：logical, intuitive, balanced
    emotional_tendency: str  # 情感倾向：rational, sensitive, passionate
    interest_areas: List[str]  # 兴趣领域
    reading_goals: List[str]  # 阅读目标

class BookReadingState(BaseModel):
    """书籍阅读状态"""
    book_title: str
    book_author: str
    reading_progress: float  # 阅读进度 0-1
    current_chapter: Optional[str]
    key_impressions: List[str]  # 关键印象
    emotional_response: str  # 情感反应
    confusion_points: List[str]  # 困惑点
    favorite_passages: List[str]  # 喜欢的段落
    personal_connections: List[str]  # 个人联系

class InterviewSession(BaseModel):
    """访谈会话"""
    session_id: str
    user_profile: UserReadingProfile
    book_state: BookReadingState
    conversation_history: List[Dict[str, Any]]
    current_stage: str  # 当前阶段：ice_break, deep_dive, perspective_clash, creative_inspiration
    extracted_insights: List[str]  # 提取的洞察
    creation_materials: List[str]  # 创作素材
    start_time: datetime
    last_interaction: datetime

class UserStateAnalyzer:
    """用户状态分析器"""
    
    def __init__(self):
        self.age_keywords = {
            "teenager": ["高中生", "中学生", "teenager", "学生", "17岁", "18岁", "19岁"],
            "young_adult": ["大学生", "研究生", "20岁", "21岁", "22岁", "23岁", "24岁", "25岁"],
            "adult": ["职场", "工作", "26岁", "27岁", "28岁", "29岁", "30岁"],
            "middle_aged": ["35岁", "40岁", "45岁", "中年", "妈妈", "爸爸"],
            "senior": ["退休", "50岁", "55岁", "60岁", "老", "老年"]
        }
        
        self.profession_keywords = {
            "student": ["学生", "大学生", "高中生", "研究生", "备考"],
            "teacher": ["老师", "教师", "教授", "教育"],
            "engineer": ["工程师", "技术", "程序员", "开发"],
            "manager": ["管理", "经理", "主管", "总监"],
            "parent": ["妈妈", "爸爸", "家长", "孩子"]
        }
        
        self.emotion_keywords = {
            "rational": ["理性", "分析", "逻辑", "客观", "科学"],
            "sensitive": ["感动", "触动", "难过", "痛苦", "温柔"],
            "passionate": ["愤怒", "激动", "热情", "强烈", "激烈"]
        }
    
    def analyze_user_profile(self, user_input: str, session_id: str) -> UserReadingProfile:
        """分析用户画像"""
        # 提取年龄信息
        age_group = self._extract_age_group(user_input)
        
        # 提取职业信息
        profession = self._extract_profession(user_input)
        
        # 分析表达风格
        expression_style = self._analyze_expression_style(user_input)
        
        # 分析认知模式
        cognitive_pattern = self._analyze_cognitive_pattern(user_input)
        
        # 分析情感倾向
        emotional_tendency = self._analyze_emotional_tendency(user_input)
        
        return UserReadingProfile(
            user_id=session_id,
            age_group=age_group,
            profession=profession,
            reading_experience="intermediate",  # 默认值
            expression_style=expression_style,
            cognitive_pattern=cognitive_pattern,
            emotional_tendency=emotional_tendency,
            interest_areas=[],  # 需要通过对话积累
            reading_goals=[]   # 需要通过对话积累
        )
    
    def _extract_age_group(self, text: str) -> str:
        """提取年龄段"""
        for age_group, keywords in self.age_keywords.items():
            if any(keyword in text for keyword in keywords):
                return age_group
        return "adult"  # 默认值
    
    def _extract_profession(self, text: str) -> str:
        """提取职业"""
        for profession, keywords in self.profession_keywords.items():
            if any(keyword in text for keyword in keywords):
                return profession
        return "general"  # 默认值
    
    def _analyze_expression_style(self, text: str) -> str:
        """分析表达风格"""
        # 分析文本特征
        question_count = text.count("?")
        exclamation_count = text.count("!")
        logical_words = ["因为", "所以", "但是", "然而", "虽然", "尽管"]
        emotional_words = ["感动", "难过", "痛苦", "快乐", "喜欢", "讨厌"]
        
        logical_score = sum(1 for word in logical_words if word in text)
        emotional_score = sum(1 for word in emotional_words if word in text)
        
        if logical_score > emotional_score:
            return "analytical"
        elif emotional_score > logical_score:
            return "emotional"
        else:
            return "balanced"
    
    def _analyze_cognitive_pattern(self, text: str) -> str:
        """分析认知模式"""
        analytical_words = ["分析", "逻辑", "原因", "结果", "证明"]
        intuitive_words = ["感觉", "直觉", "相信", "觉得", "可能"]
        
        analytical_score = sum(1 for word in analytical_words if word in text)
        intuitive_score = sum(1 for word in intuitive_words if word in text)
        
        if analytical_score > intuitive_score:
            return "logical"
        elif intuitive_score > analytical_score:
            return "intuitive"
        else:
            return "balanced"
    
    def _analyze_emotional_tendency(self, text: str) -> str:
        """分析情感倾向"""
        for tendency, keywords in self.emotion_keywords.items():
            if any(keyword in text for keyword in keywords):
                return tendency
        return "balanced"
    
    def create_session(self, user_input: str, book_title: str, book_author: str) -> InterviewSession:
        """创建访谈会话"""
        session_id = f"interview_{int(time.time())}"
        user_profile = self.analyze_user_profile(user_input, session_id)
        
        book_state = BookReadingState(
            book_title=book_title,
            book_author=book_author,
            reading_progress=1.0,  # 假设已读完
            current_chapter=None,
            key_impressions=[],
            emotional_response="",
            confusion_points=[],
            favorite_passages=[],
            personal_connections=[]
        )
        
        return InterviewSession(
            session_id=session_id,
            user_profile=user_profile,
            book_state=book_state,
            conversation_history=[],
            current_stage="ice_break",
            extracted_insights=[],
            creation_materials=[],
            start_time=datetime.now(),
            last_interaction=datetime.now()
        )
    
    def update_session_state(self, session: InterviewSession, user_message: str, ai_response: str):
        """更新会话状态"""
        # 添加对话历史
        session.conversation_history.append({
            "user": user_message,
            "ai": ai_response,
            "timestamp": datetime.now().isoformat(),
            "stage": session.current_stage
        })
        
        # 更新最后交互时间
        session.last_interaction = datetime.now()
        
        # 分析并提取关键信息
        self._extract_key_insights(session, user_message)
        
        # 根据对话进展更新阶段
        self._update_conversation_stage(session)
    
    def _extract_key_insights(self, session: InterviewSession, user_message: str):
        """提取关键洞察"""
        # 分析用户消息中的关键观点
        sentences = re.split(r'[。！？.!?]', user_message)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # 过滤太短的句子
                # 检查是否包含观点或感受
                if any(word in sentence for word in ["觉得", "认为", "感觉", "想", "应该", "可以"]):
                    session.extracted_insights.append(sentence)
    
    def _update_conversation_stage(self, session: InterviewSession):
        """更新对话阶段"""
        conversation_count = len(session.conversation_history)
        
        if conversation_count < 3:
            session.current_stage = "ice_break"
        elif conversation_count < 8:
            session.current_stage = "deep_dive"
        elif conversation_count < 12:
            session.current_stage = "perspective_clash"
        else:
            session.current_stage = "creative_inspiration"

# 全局会话存储
interview_sessions: Dict[str, InterviewSession] = {}

def get_session(session_id: str) -> Optional[InterviewSession]:
    """获取会话"""
    return interview_sessions.get(session_id)

def create_new_session(user_input: str, book_title: str, book_author: str) -> InterviewSession:
    """创建新会话"""
    analyzer = UserStateAnalyzer()
    session = analyzer.create_session(user_input, book_title, book_author)
    interview_sessions[session.session_id] = session
    return session

def update_session(session_id: str, user_message: str, ai_response: str):
    """更新会话"""
    session = get_session(session_id)
    if session:
        analyzer = UserStateAnalyzer()
        analyzer.update_session_state(session, user_message, ai_response)