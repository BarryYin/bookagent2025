"""
引导式书籍推荐智能体
基于用户阅读数据和智能对话的个性化书籍推荐系统
集成增强版推荐引擎和用户画像分析
"""

import json
import sqlite3
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import asyncio
import random

# 导入增强版推荐引擎
try:
    from enhanced_recommendation_engine import EnhancedRecommendationEngine
    from user_profile_aggregator import UserProfileAggregator
    ENHANCED_ENGINE_AVAILABLE = True
except ImportError:
    ENHANCED_ENGINE_AVAILABLE = False
    print("警告: 增强版推荐引擎不可用，将使用基础功能")

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
    """增强版引导推荐智能体"""
    
    def __init__(self, db_path: str = "fogsight.db"):
        self.db_path = db_path
        self.analyzer = ReadingAnalyzer(db_path)
        self.dialogue_system = GuidedDialogueSystem()
        self.recommendation_engine = RecommendationEngine()
        self.conversation_context = {}
        
        # 初始化增强版推荐引擎
        if ENHANCED_ENGINE_AVAILABLE:
            self.enhanced_engine = EnhancedRecommendationEngine(db_path)
            self.profile_aggregator = UserProfileAggregator(db_path)
            print("增强版推荐引擎已启用")
        else:
            self.enhanced_engine = None
            self.profile_aggregator = None
            print("使用基础推荐引擎")
    
    async def start_recommendation_session(self, user_id: int) -> Dict[str, Any]:
        """开始推荐会话（增强版）"""
        try:
            if self.enhanced_engine:
                return await self._start_enhanced_session(user_id)
            else:
                return await self._start_basic_session(user_id)
        except Exception as e:
            print(f"启动推荐会话失败: {e}")
            return await self._start_fallback_session(user_id)
    
    async def _start_enhanced_session(self, user_id: int) -> Dict[str, Any]:
        """启动增强版会话"""
        # 获取用户画像和推荐数据
        enhanced_data = self.enhanced_engine.get_enhanced_recommendations(user_id, 5)
        user_context = enhanced_data['user_context']
        recommendations = enhanced_data['recommendations']
        explanations = enhanced_data['explanations']
        
        # 构建个性化开场白
        greeting = self._create_personalized_greeting(user_context, recommendations)
        
        # 初始化对话上下文
        self.conversation_context[user_id] = {
            "user_profile": user_context,
            "turn": 0,
            "recommendations": recommendations,
            "explanations": explanations,
            "enhanced_data": enhanced_data,
            "conversation_history": []
        }
        
        return {
            "message": greeting,
            "recommendations": self._format_recommendations(recommendations[:3], explanations[:3]),
            "user_profile": user_context,
            "session_id": f"enhanced_session_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "metadata": enhanced_data['recommendation_metadata']
        }
    
    async def _start_basic_session(self, user_id: int) -> Dict[str, Any]:
        """启动基础版会话"""
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
    
    async def _start_fallback_session(self, user_id: int) -> Dict[str, Any]:
        """降级会话"""
        return {
            "message": "你好！我是你的阅读顾问。请告诉我你最近在读什么书，或者想要什么类型的推荐？",
            "recommendations": [],
            "session_id": f"fallback_session_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
    
    def _create_personalized_greeting(self, user_context: Dict, recommendations: List[Dict]) -> str:
        """创建个性化开场白"""
        reading_level = user_context.get('reading_level', '未知')
        interests = user_context.get('primary_interests', [])
        needs_diversification = user_context.get('needs_diversification', False)
        
        if reading_level == "高频":
            greeting = "你好！我注意到你是一位非常活跃的读者，"
        elif reading_level == "中频":
            greeting = "你好！看到你保持着很好的阅读习惯，"
        else:
            greeting = "你好！很高兴看到你开始探索阅读的世界，"
        
        if interests:
            greeting += f"特别关注{', '.join(interests[:2])}等领域。"
        else:
            greeting += "兴趣涉猎很广泛。"
        
        if needs_diversification:
            greeting += "我发现你的阅读可能需要一些新的方向，"
        else:
            greeting += "你在自己感兴趣的领域已经有了很好的积累，"
        
        greeting += f"基于你的阅读画像，我为你精选了几本书。我们可以聊聊你现在最想了解什么类型的内容？"
        
        return greeting
    
    def _format_recommendations(self, recommendations: List[Dict], explanations: List[str]) -> List[Dict]:
        """格式化推荐结果"""
        formatted = []
        for i, (book, explanation) in enumerate(zip(recommendations, explanations)):
            formatted.append({
                "title": book.get('title', ''),
                "author": book.get('author', ''),
                "category": book.get('category_name', ''),
                "description": book.get('description', ''),
                "reason": explanation,
                "cover_url": book.get('cover_url', ''),
                "rank": i + 1
            })
        return formatted
    
    async def continue_conversation(self, user_id: int, user_response: str) -> Dict[str, Any]:
        """继续对话（增强版）"""
        
        if user_id not in self.conversation_context:
            return await self.start_recommendation_session(user_id)
        
        context = self.conversation_context[user_id]
        context["turn"] += 1
        context["conversation_history"].append(("user", user_response))
        
        # 根据是否有增强引擎选择不同的处理方式
        if self.enhanced_engine and "enhanced_data" in context:
            return await self._continue_enhanced_conversation(user_id, user_response, context)
        else:
            return await self._continue_basic_conversation(user_id, user_response, context)
    
    async def _continue_enhanced_conversation(self, user_id: int, user_response: str, context: Dict) -> Dict[str, Any]:
        """增强版对话处理"""
        try:
            # 分析用户输入
            user_response_lower = user_response.lower()
            
            # 意图识别
            if any(keyword in user_response_lower for keyword in ['推荐', '建议', '什么书', '书籍']):
                reply = await self._handle_recommendation_request(context)
            elif any(keyword in user_response_lower for keyword in ['喜欢', '兴趣', '偏好']):
                reply = await self._handle_preference_inquiry(user_response, context)
            elif any(keyword in user_response_lower for keyword in ['时间', '忙', '短', '长']):
                reply = await self._handle_time_constraints(user_response, context)
            elif any(keyword in user_response_lower for keyword in ['详细', '介绍', '更多']):
                reply = await self._handle_detail_request(user_response, context)
            else:
                reply = await self._handle_general_response(user_response, context)
            
            context["conversation_history"].append(("agent", reply["message"]))
            
            return reply
            
        except Exception as e:
            print(f"增强对话处理失败: {e}")
            return {
                "message": "抱歉，我现在有点困惑。能再说一遍你的需求吗？",
                "recommendations": [],
                "turn": context["turn"]
            }
    
    async def _handle_recommendation_request(self, context: Dict) -> Dict[str, Any]:
        """处理推荐请求"""
        recommendations = context.get("recommendations", [])
        explanations = context.get("explanations", [])
        
        if recommendations:
            message = "基于我对你阅读习惯的深度分析，我特别推荐以下几本书：\n\n"
            
            for i, (book, explanation) in enumerate(zip(recommendations[:3], explanations[:3])):
                message += f"{i+1}. 《{book['title']}》- {book['author']} ({book['category_name']})\n"
                message += f"   推荐理由：{explanation}\n\n"
            
            message += "你对哪本书比较感兴趣？或者告诉我你更偏向什么类型的内容？"
            
            return {
                "message": message,
                "recommendations": self._format_recommendations(recommendations[:3], explanations[:3]),
                "turn": context["turn"],
                "should_recommend": True
            }
        else:
            return {
                "message": "让我了解一下你的偏好，然后为你推荐合适的书籍。你平时喜欢读什么类型的书？",
                "recommendations": [],
                "turn": context["turn"]
            }
    
    async def _handle_preference_inquiry(self, user_response: str, context: Dict) -> Dict[str, Any]:
        """处理偏好询问"""
        # 提取用户提到的偏好
        preferences = self._extract_preferences_from_message(user_response)
        
        if preferences:
            message = f"了解了！你喜欢{', '.join(preferences)}类的书籍。这很有趣，"
            
            # 根据偏好调整推荐策略
            if preferences[0] in context.get("user_profile", {}).get("primary_interests", []):
                message += "这正好是你的强项领域。我可以推荐一些这个领域的进阶内容。"
            else:
                message += "这是一个新的探索方向。我来为你挑选一些入门但高质量的作品。"
            
            message += "\n\n有什么特定的主题或作者你特别想了解吗？"
        else:
            message = "能具体说说你喜欢什么类型的书吗？比如心理学、历史、小说、传记、科技等？"
        
        return {
            "message": message,
            "recommendations": context.get("recommendations", [])[:3],
            "turn": context["turn"]
        }
    
    async def _handle_time_constraints(self, user_response: str, context: Dict) -> Dict[str, Any]:
        """处理时间限制"""
        if any(word in user_response.lower() for word in ['忙', '短', '快', '时间少']):
            message = "理解你的时间比较紧张。基于你的阅读画像，我建议你选择："
            message += "\n• 结构清晰、可以碎片化阅读的内容"
            message += "\n• 篇幅适中但信息密度高的书籍"
            message += "\n• 或者优质的有声书版本"
            
            # 从现有推荐中筛选适合忙碌人群的书籍
            filtered_recommendations = []
            for book in context.get("recommendations", []):
                if any(keyword in book.get('category_name', '').lower() for keyword in ['心理', '技能', '管理']):
                    filtered_recommendations.append(book)
            
            message += "\n\n从我的推荐中，你比较倾向于哪种类型？"
            
            return {
                "message": message,
                "recommendations": self._format_recommendations(filtered_recommendations[:3], 
                                                              context.get("explanations", [])[:3]),
                "turn": context["turn"]
            }
        else:
            message = "看起来你有充足的时间深度阅读，这很棒！我可以推荐一些更有挑战性和深度的作品。"
            message += "你想要更有挑战性的内容，还是偏向轻松一些的阅读体验？"
            
            return {
                "message": message,
                "recommendations": context.get("recommendations", [])[:3],
                "turn": context["turn"]
            }
    
    async def _handle_detail_request(self, user_response: str, context: Dict) -> Dict[str, Any]:
        """处理详细信息请求"""
        # 简单的书名提取（实际应用中可以用更复杂的NLP）
        recommendations = context.get("recommendations", [])
        
        for book in recommendations:
            if book['title'] in user_response:
                message = f"关于《{book['title']}》的详细介绍：\n\n"
                message += f"作者：{book['author']}\n"
                message += f"分类：{book['category_name']}\n"
                message += f"推荐理由：{context.get('explanations', [''])[0]}\n\n"
                message += "这本书你感兴趣吗？还想了解其他推荐吗？"
                
                return {
                    "message": message,
                    "recommendations": [book],
                    "turn": context["turn"]
                }
        
        # 如果没有找到特定书籍，提供一般性回复
        message = "我可以为你详细介绍任何一本推荐的书。请告诉我你想了解哪本书？"
        
        return {
            "message": message,
            "recommendations": recommendations[:3],
            "turn": context["turn"]
        }
    
    async def _handle_general_response(self, user_response: str, context: Dict) -> Dict[str, Any]:
        """处理一般性回复"""
        # 简单的情感分析
        positive_words = ['好', '喜欢', '有趣', '不错', '谢谢']
        negative_words = ['不喜欢', '没兴趣', '不好', '不要']
        
        is_positive = any(word in user_response for word in positive_words)
        is_negative = any(word in user_response for word in negative_words)
        
        if is_positive:
            message = "很高兴你喜欢！基于你的反馈，我会继续为你推荐类似风格的内容。"
            message += "还想了解什么类型的书籍吗？"
        elif is_negative:
            message = "我明白了，那让我们换个方向。能告诉我你更偏向什么类型的内容吗？"
        else:
            message = "我理解。为了给你更好的推荐，你希望我介绍具体的书籍，还是想先聊聊你的阅读偏好？"
        
        return {
            "message": message,
            "recommendations": context.get("recommendations", [])[:3],
            "turn": context["turn"]
        }
    
    def _extract_preferences_from_message(self, message: str) -> List[str]:
        """从用户消息中提取偏好"""
        categories = ['心理学', '历史', '文学', '科技', '哲学', '传记', '小说', '散文', '经济', '管理', '艺术', '科普', '职场', '成长']
        found_preferences = []
        
        for category in categories:
            if category in message:
                found_preferences.append(category)
        
        return found_preferences
    async def _continue_basic_conversation(self, user_id: int, user_response: str, context: Dict) -> Dict[str, Any]:
        """基础版对话处理"""
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