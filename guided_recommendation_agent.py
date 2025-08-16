"""
引导式书籍推荐智能体
基于用户阅读数据和智能对话的个性化书籍推荐系统
"""

import json
import sqlite3
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import asyncio
import random

@dataclass
class Book:
    """书籍信息"""
    title: str
    author: str
    category: str
    description: str
    tags: List[str]
    difficulty_level: str  # "入门", "进阶", "专业"
    emotional_tone: str  # "治愈", "励志", "思考", "轻松"
    reading_time: str  # "短篇", "中篇", "长篇"

@dataclass
class ReadingHistory:
    """用户阅读历史"""
    book_title: str
    completion_date: datetime
    rating: Optional[int] = None
    notes: Optional[str] = None

@dataclass
class UserProfile:
    """用户画像"""
    reading_frequency: str  # "高频", "中频", "低频"
    preferred_categories: List[str]
    reading_patterns: List[str]  # "周末集中", "碎片化", "通勤阅读"
    current_life_stage: str  # "职场新人", "中年转型", "退休生活"
    emotional_needs: List[str]  # "成长指导", "心理治愈", "知识拓展"
    cognitive_level: str  # "入门", "进阶", "专家"

class ReadingAnalyzer:
    """阅读数据分析器"""
    
    def __init__(self, db_path: str = "fogsight.db"):
        self.db_path = db_path
        
    def analyze_reading_patterns(self, user_id: int) -> Dict[str, Any]:
        """分析用户阅读模式"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取用户阅读历史
        cursor.execute("""
            SELECT book_title, completion_date, rating, notes 
            FROM reading_history 
            WHERE user_id = ? 
            ORDER BY completion_date DESC
        """, (user_id,))
        
        history = cursor.fetchall()
        conn.close()
        
        if not history:
            return {"message": "暂无阅读数据"}
        
        # 分析阅读频率
        reading_times = [datetime.fromisoformat(row[1]) for row in history]
        frequency = self._calculate_reading_frequency(reading_times)
        
        # 分析偏好类别
        categories = self._analyze_categories([row[0] for row in history])
        
        # 识别阅读模式变化
        pattern_changes = self._detect_pattern_changes(history)
        
        # 推断当前生活阶段
        life_stage = self._infer_life_stage(categories, pattern_changes)
        
        # 识别情感需求
        emotional_needs = self._identify_emotional_needs(history)
        
        return {
            "reading_frequency": frequency,
            "preferred_categories": categories,
            "pattern_changes": pattern_changes,
            "current_life_stage": life_stage,
            "emotional_needs": emotional_needs,
            "recent_books": [row[0] for row in history[:5]]
        }
    
    def _calculate_reading_frequency(self, reading_times: List[datetime]) -> str:
        """计算阅读频率"""
        if len(reading_times) < 2:
            return "低频"
        
        # 计算平均阅读间隔（天）
        intervals = []
        for i in range(1, len(reading_times)):
            interval = (reading_times[i-1] - reading_times[i]).days
            intervals.append(interval)
        
        avg_interval = sum(intervals) / len(intervals)
        
        if avg_interval <= 7:
            return "高频"
        elif avg_interval <= 30:
            return "中频"
        else:
            return "低频"
    
    def _analyze_categories(self, book_titles: List[str]) -> List[str]:
        """分析书籍类别偏好"""
        # 简化的类别映射
        category_map = {
            "高效能": "职场技能",
            "金字塔原理": "职场技能",
            "非暴力沟通": "职场技能",
            "刻意练习": "职场技能",
            "深度工作": "职场技能",
            "房思琪": "女性议题",
            "82年生的金智英": "女性议题",
            "我们仨": "女性议题",
            "活着": "人生思考",
            "人类简史": "历史",
            "万历十五年": "历史",
            "明朝那些事儿": "历史"
        }
        
        categories = []
        for title in book_titles:
            for keyword, category in category_map.items():
                if keyword.lower() in title.lower():
                    categories.append(category)
                    break
        
        # 返回最常见的3个类别
        category_counts = {}
        for cat in categories:
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        return sorted(category_counts.keys(), key=lambda x: category_counts[x], reverse=True)[:3]
    
    def _detect_pattern_changes(self, history: List[tuple]) -> List[str]:
        """检测阅读模式变化"""
        if len(history) < 3:
            return ["数据不足，无法检测模式变化"]
        
        # 简化的模式变化检测
        recent_books = [row[0] for row in history[:3]]
        older_books = [row[0] for row in history[-3:]]
        
        recent_categories = self._analyze_categories(recent_books)
        older_categories = self._analyze_categories(older_books)
        
        changes = []
        if set(recent_categories) != set(older_categories):
            changes.append("阅读兴趣发生转变")
        
        return changes
    
    def _infer_life_stage(self, categories: List[str], changes: List[str]) -> str:
        """推断用户当前生活阶段"""
        if "职场技能" in categories and len(categories) == 1:
            return "职场新人"
        elif "女性议题" in categories and "育儿" in str(categories):
            return "中年妈妈"
        elif "历史" in categories and len(categories) >= 2:
            return "退休学者"
        else:
            return "多元探索者"
    
    def _identify_emotional_needs(self, history: List[tuple]) -> List[str]:
        """识别情感需求"""
        needs = []
        
        # 基于书籍标题的关键词分析
        titles = [row[0] for row in history]
        all_titles = " ".join(titles).lower()
        
        if "高效" in all_titles or "成功" in all_titles:
            needs.append("成长指导")
        
        if "治愈" in all_titles or "温暖" in all_titles:
            needs.append("心理治愈")
        
        if "历史" in all_titles or "人类" in all_titles:
            needs.append("知识拓展")
        
        if not needs:
            needs.append("兴趣探索")
        
        return needs

class GuidedDialogueSystem:
    """智能对话引导系统"""
    
    def __init__(self):
        self.conversation_state = {}
        self.dialogue_templates = self._load_dialogue_templates()
    
    def _load_dialogue_templates(self) -> Dict[str, List[str]]:
        """加载对话模板"""
        return {
            "职场新人": [
                "我看你最近读了很多职场技能类的书，是刚开始工作吗？",
                "我理解这种焦虑。不过我注意到你读的这些书都很'硬核'，全是方法论。你有多久没读过让自己放松的书了？",
                "其实适当的放松阅读能帮你更好地消化这些职场技能。而且，你读了这么多沟通和思维的书，我觉得你可能会喜欢一些有趣的心理学书籍。要不要试试？"
            ],
            "中年妈妈": [
                "我看你既关注孩子教育，也在思考女性话题，最近读这些书是有什么特别的触动吗？",
                "这种思考很有意义。我注意到你很久没有为自己读过书了，都是围绕孩子和女性身份。你有没有想过重新找回一些纯粹属于自己的兴趣？",
                "其实文学能给你更多思考女性和人生的角度。比如一些优秀的文学作品，既能放松又能让你从另一个维度思考。"
            ],
            "退休学者": [
                "您的阅读品味很棒！从宏观历史到个人传记，涵盖面很广。我发现您特别喜欢从历史中思考人性和社会。",
                "您读了这么多中国历史，有没有想过对比一下西方的历史视角？或者，基于您对人性的思考，一些心理学经典也很值得读。",
                "不会的，我推荐的都是很好读的。而且以您的阅读基础，完全没问题。"
            ]
        }
    
    def start_conversation(self, user_profile: Dict[str, Any], user_id: int) -> str:
        """开始对话"""
        life_stage = user_profile.get("current_life_stage", "多元探索者")
        
        if life_stage in self.dialogue_templates:
            greeting = f"你好！我是你的私人阅读顾问。"
            if user_profile.get("recent_books"):
                greeting += f"我注意到你最近读了《{'》、《'.join(user_profile['recent_books'][:3])}》..."
            
            question = self.dialogue_templates[life_stage][0]
            return f"{greeting}{question}"
        else:
            return "你好！我是你的私人阅读顾问。为了更好地了解你的阅读需求，能和我聊聊你最近在读什么书吗？"
    
    def continue_conversation(self, user_response: str, context: Dict[str, Any]) -> str:
        """继续对话"""
        life_stage = context.get("life_stage", "多元探索者")
        turn = context.get("turn", 0)
        
        if life_stage in self.dialogue_templates and turn < len(self.dialogue_templates[life_stage]):
            return self.dialogue_templates[life_stage][turn]
        else:
            # 生成个性化推荐
            return self._generate_recommendation(context)
    
    def _generate_recommendation(self, context: Dict[str, Any]) -> str:
        """生成个性化推荐"""
        emotional_needs = context.get("emotional_needs", [])
        life_stage = context.get("life_stage", "多元探索者")
        
        recommendations = {
            "职场新人": {
                "成长指导": "《乌合之众》- 有趣的心理学书籍，既能放松又能加深对人性的理解",
                "心理治愈": "《被讨厌的勇气》- 阿德勒心理学入门，帮你建立健康的自我认知",
                "知识拓展": "《思考，快与慢》- 了解思维模式，提升决策能力"
            },
            "中年妈妈": {
                "心理治愈": "《使女的故事》- 优秀的文学作品，从另一个维度思考女性处境",
                "兴趣探索": "《小王子》- 重新找回童心，简短但深刻的阅读体验",
                "知识拓展": "《第二性》- 女性主义经典，深度思考女性身份"
            },
            "退休学者": {
                "知识拓展": "《罗马人的故事》- 了解西方文明发展，与东方历史形成对比",
                "思考启发": "《人性的弱点》- 基于你丰富的人生经验，深度理解人性",
                "兴趣拓展": "《万物简史》- 用科学视角重新理解世界"
            }
        }
        
        if life_stage in recommendations and emotional_needs:
            need = emotional_needs[0]  # 取第一个需求
            if need in recommendations[life_stage]:
                book = recommendations[life_stage][need]
                return f"基于你的阅读偏好和当前状态，我特别推荐{book}。这本书{self._get_book_reason(book, life_stage, need)}"
        
        return "基于我们的对话，我觉得你可以尝试一些不同类型的书籍，拓宽阅读视野。有什么具体的主题你感兴趣吗？"
    
    def _get_book_reason(self, book: str, life_stage: str, need: str) -> str:
        """获取推荐理由"""
        reasons = {
            ("职场新人", "成长指导"): "能让你在紧张的职场学习中找到平衡，同时加深对人性的理解",
            ("中年妈妈", "心理治愈"): "既满足文学需求，又能让你从新的角度思考女性话题",
            ("退休学者", "知识拓展"): "能让你看到完全不同的文明发展路径，丰富你的历史视野"
        }
        
        return reasons.get((life_stage, need), "能为你带来新的思考和启发")

class RecommendationEngine:
    """推荐引擎"""
    
    def __init__(self):
        self.books_db = self._load_books_database()
    
    def _load_books_database(self) -> List[Book]:
        """加载书籍数据库"""
        return [
            Book("乌合之众", "古斯塔夫·勒庞", "心理学", "群体心理学的经典之作", ["心理学", "社会", "人性"], "入门", "思考", "中篇"),
            Book("被讨厌的勇气", "岸见一郎", "心理学", "阿德勒心理学入门", ["心理学", "自我成长", "哲学"], "入门", "治愈", "中篇"),
            Book("思考，快与慢", "丹尼尔·卡尼曼", "心理学", "思维模式的深度解析", ["心理学", "思维", "决策"], "进阶", "思考", "长篇"),
            Book("使女的故事", "玛格丽特·阿特伍德", "文学", "女性主义反乌托邦经典", ["女性", "文学", "政治"], "进阶", "思考", "中篇"),
            Book("小王子", "安托万·德·圣埃克苏佩里", "文学", "童心未泯的哲学寓言", ["文学", "哲学", "童话"], "入门", "治愈", "短篇"),
            Book("第二性", "西蒙娜·德·波伏娃", "哲学", "女性主义奠基之作", ["女性", "哲学", "社会学"], "专业", "思考", "长篇"),
            Book("罗马人的故事", "盐野七生", "历史", "罗马帝国的兴衰史", ["历史", "罗马", "文明"], "进阶", "思考", "长篇"),
            Book("人性的弱点", "戴尔·卡耐基", "心理学", "人际关系的艺术", ["心理学", "人际", "成功"], "入门", "励志", "中篇"),
            Book("万物简史", "比尔·布莱森", "科普", "用科学视角看世界", ["科学", "历史", "知识"], "入门", "启发", "长篇")
        ]
    
    def recommend_books(self, user_profile: Dict[str, Any], dialogue_context: Dict[str, Any]) -> List[Book]:
        """基于用户画像和对话上下文推荐书籍"""
        
        emotional_needs = user_profile.get("emotional_needs", [])
        life_stage = user_profile.get("current_life_stage", "多元探索者")
        
        # 根据生活阶段和情感需求筛选书籍
        filtered_books = []
        
        for book in self.books_db:
            score = 0
            
            # 根据情感需求评分
            if book.emotional_tone in emotional_needs:
                score += 3
            
            # 根据阅读难度评分
            if life_stage == "职场新人" and book.difficulty_level == "入门":
                score += 2
            elif life_stage == "退休学者" and book.difficulty_level in ["进阶", "专业"]:
                score += 2
            
            # 根据阅读时间偏好评分
            if life_stage == "中年妈妈" and book.reading_time in ["短篇", "中篇"]:
                score += 1
            
            if score > 0:
                filtered_books.append((book, score))
        
        # 按评分排序，返回前3本
        filtered_books.sort(key=lambda x: x[1], reverse=True)
        return [book for book, score in filtered_books[:3]]

class GuidedRecommendationAgent:
    """引导式书籍推荐智能体"""
    
    def __init__(self, db_path: str = "fogsight.db"):
        self.analyzer = ReadingAnalyzer(db_path)
        self.dialogue_system = GuidedDialogueSystem()
        self.recommendation_engine = RecommendationEngine()
        self.conversation_context = {}
    
    async def start_recommendation_session(self, user_id: int) -> Dict[str, Any]:
        """开始推荐会话"""
        
        # 分析用户阅读数据
        user_profile = self.analyzer.analyze_reading_patterns(user_id)
        
        # 初始化对话上下文
        self.conversation_context[user_id] = {
            "user_profile": user_profile,
            "turn": 0,
            "life_stage": user_profile.get("current_life_stage", "多元探索者"),
            "emotional_needs": user_profile.get("emotional_needs", [])
        }
        
        # 开始对话
        greeting = self.dialogue_system.start_conversation(user_profile, user_id)
        
        return {
            "message": greeting,
            "user_profile": user_profile,
            "session_id": f"session_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
    
    async def continue_conversation(self, user_id: int, user_response: str) -> Dict[str, Any]:
        """继续对话"""
        
        if user_id not in self.conversation_context:
            return await self.start_recommendation_session(user_id)
        
        context = self.conversation_context[user_id]
        context["turn"] += 1
        
        # 生成回复
        reply = self.dialogue_system.continue_conversation(user_response, context)
        
        # 检查是否应该生成推荐
        should_recommend = context["turn"] >= 3 or "推荐" in user_response
        
        recommendations = []
        if should_recommend:
            recommendations = self.recommendation_engine.recommend_books(
                context["user_profile"], context
            )
        
        return {
            "message": reply,
            "recommendations": [
                {
                    "title": book.title,
                    "author": book.author,
                    "category": book.category,
                    "description": book.description,
                    "reason": self._generate_recommendation_reason(book, context)
                }
                for book in recommendations
            ],
            "turn": context["turn"],
            "should_recommend": should_recommend
        }
    
    def _generate_recommendation_reason(self, book: Book, context: Dict[str, Any]) -> str:
        """生成推荐理由"""
        life_stage = context.get("life_stage", "多元探索者")
        
        reasons = {
            "职场新人": f"这本书能让你在{book.category}领域获得新的视角，对职场发展很有帮助",
            "中年妈妈": f"这本书{book.reading_time}适中，内容既有深度又不会过于沉重，很适合你现在的状态",
            "退休学者": f"以你的阅读基础，这本书能让你在{book.category}领域有更深入的理解",
            "多元探索者": f"这本书能帮你拓展在{book.category}领域的知识边界"
        }
        
        return reasons.get(life_stage, f"这本书很适合你当前的阅读需求")

# 全局智能体实例
agent = GuidedRecommendationAgent()

# API接口函数
async def start_recommendation(user_id: int) -> Dict[str, Any]:
    """开始推荐会话的API接口"""
    return await agent.start_recommendation_session(user_id)

async def chat_with_agent(user_id: int, message: str) -> Dict[str, Any]:
    """与智能体对话的API接口"""
    return await agent.continue_conversation(user_id, message)