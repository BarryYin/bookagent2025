"""
内容结构化整理与播客生成模块
"""
import json
import re
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel
from openai import AsyncOpenAI
from interview_user_model import InterviewSession, get_session, UserReadingProfile
from podcast_audio_generator import generate_podcast_audio

# 配置LLM
QWEN_BASE_URL = "https://api-inference.modelscope.cn/v1/"
QWEN_API_KEY = "ms-076e7668-1000-4ce8-be4e-f475ddfeead7"
QWEN_MODEL = "Qwen/Qwen3-Coder-480B-A35B-Instruct"

llm_client = AsyncOpenAI(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL)

class PodcastSegment(BaseModel):
    """播客片段"""
    segment_type: str  # intro, main_content, insight, reflection, outro
    content: str
    duration_estimate: int  # 预估时长（秒）
    emotional_tone: str  # 情感基调
    key_points: List[str]

class PodcastStructure(BaseModel):
    """播客结构"""
    title: str
    subtitle: str
    segments: List[PodcastSegment]
    total_duration: int
    target_audience: str
    key_themes: List[str]
    personal_signature: str  # 个人特色

class ContentProcessor:
    """内容处理器"""
    
    def __init__(self):
        self.insight_patterns = [
            r"我觉得.*[很真].*",
            r"我认为.*[应该].*",
            r".*[让我].*[想到].*",
            r".*[从].*[角度].*",
            r".*[如果].*[会].*"
        ]
    
    async def extract_key_insights(self, session: InterviewSession) -> List[str]:
        """提取关键洞察"""
        # 使用LLM进行智能洞察提取
        return await self._extract_insights_with_llm(session)
    
    async def _extract_insights_with_llm(self, session: InterviewSession) -> List[str]:
        """使用LLM提取关键洞察"""
        book_title = session.book_state.book_title
        profile = session.user_profile
        
        # 构建对话历史
        conversation_text = ""
        for i, conv in enumerate(session.conversation_history):
            conversation_text += f"第{i+1}轮对话:\n"
            conversation_text += f"用户: {conv['user']}\n"
            conversation_text += f"助手: {conv['ai']}\n\n"
        
        prompt = f"""
请分析以下关于《{book_title}》的访谈对话，提取出用户的核心观点和独特洞察。

用户画像：{profile.age_group}，{profile.profession}，表达风格{profile.expression_style}

访谈对话内容：
{conversation_text}

请提取5-8个最有价值的洞察，要求：
1. 每个洞察都要体现用户的个人观点和独特视角
2. 洞察应该涵盖对书籍的理解、个人感受、生活联系等方面
3. 每个洞察长度在30-100字之间
4. 洞察要有深度，避免表面的描述
5. 保持用户原有的表达风格和语气

请以JSON格式返回，包含insights数组。
"""
        
        try:
            response = await llm_client.chat.completions.create(
                model=QWEN_MODEL,
                messages=[
                    {"role": "system", "content": "你是一位专业的阅读分析师，擅长从对话中提取有价值的洞察和观点。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content.strip()
            
            # 尝试解析JSON
            try:
                data = json.loads(result)
                return data.get("insights", [])
            except json.JSONDecodeError:
                # 如果JSON解析失败，尝试手动提取
                lines = result.split('\n')
                insights = []
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 20 and not line.startswith('```'):
                        insights.append(line)
                return insights[:8]  # 限制数量
                
        except Exception as e:
            print(f"LLM洞察提取失败: {e}")
            # 降级到传统方法
            return self._extract_insights_fallback(session)
    
    def _extract_insights_fallback(self, session: InterviewSession) -> List[str]:
        """降级的洞察提取方法"""
        insights = []
        
        for conversation in session.conversation_history:
            user_message = conversation["user"]
            
            # 使用正则表达式匹配洞察模式
            for pattern in self.insight_patterns:
                matches = re.findall(pattern, user_message)
                insights.extend(matches)
            
            # 提取包含观点的句子
            sentences = re.split(r'[。！？.!?]', user_message)
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 20 and self._is_insightful(sentence):
                    insights.append(sentence)
        
        # 去重并过滤
        unique_insights = list(set(insights))
        return [insight for insight in unique_insights if len(insight) > 10][:8]
    
    def _is_insightful(self, sentence: str) -> bool:
        """判断是否为有洞察力的内容"""
        insight_keywords = [
            "觉得", "认为", "感觉", "想", "应该", "可以", "可能", 
            "理解", "明白", "发现", "意识到", "体会到", "感受到"
        ]
        
        return any(keyword in sentence for keyword in insight_keywords)
    
    async def organize_content_structure(self, session: InterviewSession) -> PodcastStructure:
        """组织内容结构"""
        profile = session.user_profile
        book_title = session.book_state.book_title
        
        # 提取关键洞察
        insights = await self.extract_key_insights(session)
        
        # 生成播客标题
        title = self._generate_podcast_title(profile, book_title, insights)
        
        # 构建播客片段
        segments = await self._build_segments(session, insights)
        
        # 计算总时长
        total_duration = sum(segment.duration_estimate for segment in segments)
        
        return PodcastStructure(
            title=title,
            subtitle=f"一个{profile.age_group}的《{book_title}》读后感",
            segments=segments,
            total_duration=total_duration,
            target_audience=self._determine_target_audience(profile),
            key_themes=self._extract_key_themes(insights),
            personal_signature=self._generate_personal_signature(profile)
        )
    
    def _generate_podcast_title(self, profile: UserReadingProfile, book_title: str, insights: List[str]) -> str:
        """生成播客标题"""
        age_descriptors = {
            "teenager": "青少年",
            "young_adult": "年轻人", 
            "adult": "职场人",
            "middle_angled": "中年人",
            "senior": "长者"
        }
        
        profession_descriptors = {
            "student": "学生",
            "teacher": "教师",
            "engineer": "工程师",
            "manager": "管理者",
            "parent": "家长"
        }
        
        age_desc = age_descriptors.get(profile.age_group, "读者")
        prof_desc = profession_descriptors.get(profile.profession, "")
        
        if prof_desc:
            return f"《{book_title}》：一位{age_desc}{prof_desc}的深度解读"
        else:
            return f"《{book_title}》：一个{age_desc}的独特视角"
    
    async def _build_segments(self, session: InterviewSession, insights: List[str]) -> List[PodcastSegment]:
        """构建播客片段"""
        profile = session.user_profile
        book_title = session.book_state.book_title
        
        segments = []
        
        # 开场白
        intro_segment = PodcastSegment(
            segment_type="intro",
            content=await self._generate_introduction_with_llm(profile, book_title),
            duration_estimate=60,
            emotional_tone="friendly",
            key_points=["自我介绍", "书籍简介", "阅读背景"]
        )
        segments.append(intro_segment)
        
        # 主要内容（根据洞察数量分配）
        main_insights = insights[:5]  # 取前5个核心洞察
        for i, insight in enumerate(main_insights):
            segment = PodcastSegment(
                segment_type="main_content",
                content=insight,
                duration_estimate=45,
                emotional_tone=self._determine_emotional_tone(insight),
                key_points=[f"观点{i+1}"]
            )
            segments.append(segment)
        
        # 个人反思
        reflection_segment = PodcastSegment(
            segment_type="reflection",
            content=await self._generate_reflection_with_llm(profile, book_title, insights),
            duration_estimate=90,
            emotional_tone="thoughtful",
            key_points=["个人收获", "生活启示", "未来思考"]
        )
        segments.append(reflection_segment)
        
        # 结束语
        outro_segment = PodcastSegment(
            segment_type="outro",
            content=await self._generate_outro_with_llm(profile, book_title),
            duration_estimate=30,
            emotional_tone="hopeful",
            key_points=["总结", "推荐", "感谢"]
        )
        segments.append(outro_segment)
        
        return segments
    
    async def _generate_introduction_with_llm(self, profile: UserReadingProfile, book_title: str) -> str:
        """使用LLM生成开场白"""
        prompt = f"""
请为一位{profile.age_group}{profile.profession}生成一个关于《{book_title}》读后感播客的开场白。

要求：
1. 语气自然亲切，符合{profile.age_group}的表达特点
2. 简要介绍为什么要分享这本书的读后感
3. 长度控制在80-120字之间
4. 体现个人特色，避免生硬的模板化表达
5. 为后续的内容做好铺垫

请直接返回开场白文本，不要添加其他说明。
"""
        
        return await self._call_llm_for_content(prompt)
    
    async def _generate_reflection_with_llm(self, profile: UserReadingProfile, book_title: str, insights: List[str]) -> str:
        """使用LLM生成个人反思"""
        insights_text = "\n".join([f"- {insight}" for insight in insights])
        
        prompt = f"""
基于以下关于《{book_title}》的洞察，为一位{profile.age_group}{profile.profession}生成一段个人反思。

核心洞察：
{insights_text}

要求：
1. 深入总结这本书对个人的影响和启发
2. 结合{profile.age_group}的生活经历和认知特点
3. 表达要真诚有深度，避免空泛的套话
4. 长度控制在120-180字之间
5. 体现个人的独特视角和真实感受

请直接返回反思内容，不要添加其他说明。
"""
        
        return await self._call_llm_for_content(prompt)
    
    async def _generate_outro_with_llm(self, profile: UserReadingProfile, book_title: str) -> str:
        """使用LLM生成结束语"""
        prompt = f"""
为一位{profile.age_group}{profile.profession}的《{book_title}》读后感播客生成结束语。

要求：
1. 总结主要观点，强调这本书的价值
2. 向听众推荐这本书，给出推荐理由
3. 语气温暖真诚，体现{profile.age_group}的表达特点
4. 长度控制在60-100字之间
5. 自然收尾，给听众留下良好印象

请直接返回结束语文本，不要添加其他说明。
"""
        
        return await self._call_llm_for_content(prompt)
    
    async def _call_llm_for_content(self, prompt: str) -> str:
        """调用LLM生成内容"""
        try:
            response = await llm_client.chat.completions.create(
                model=QWEN_MODEL,
                messages=[
                    {"role": "system", "content": "你是一位专业的播客内容创作者，擅长创作自然、有深度的读后感内容。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"LLM内容生成失败: {e}")
            # 降级到模板内容
            return "感谢大家的聆听，希望通过我的分享，能够给大家带来一些启发和思考。"
    
    def _generate_introduction(self, profile: UserReadingProfile, book_title: str) -> str:
        """生成开场白"""
        age_intro = {
            "teenager": "作为一名年轻读者",
            "young_adult": "作为一个刚刚步入社会的年轻人",
            "adult": "作为一个有着一定生活阅历的读者",
            "middle_aged": "作为一个经历过人生起伏的中年人",
            "senior": "作为一个有着丰富人生经验的长者"
        }
        
        intro = age_intro.get(profile.age_group, "作为一个读者")
        
        return f"{intro}，我今天想和大家分享我读《{book_title}》的感受和思考。这本书给了我很多启发，希望能通过我的分享，给大家带来一些新的思考角度。"
    
    def _generate_reflection(self, profile: UserReadingProfile, book_title: str) -> str:
        """生成个人反思"""
        reflection_templates = [
            f"读完整本《{book_title}》，我最大的收获是...",
            f"这本书让我重新思考了...",
            f"在今后的生活中，我会把从《{book_title}》中学到的...",
            f"《{book_title}》不仅仅是一本书，它更像是一面镜子，让我看到了..."
        ]
        
        import random
        return random.choice(reflection_templates)
    
    def _generate_outro(self, profile: UserReadingProfile, book_title: str) -> str:
        """生成结束语"""
        return f"感谢大家听我分享关于《{book_title}》的读后感。希望我的分享能给大家带来一些启发。如果大家还没有读过这本书，我强烈推荐大家去读一读，相信每个人都能从中找到属于自己的感悟。"
    
    def _determine_emotional_tone(self, content: str) -> str:
        """确定情感基调"""
        positive_words = ["快乐", "希望", "温暖", "感动", "启发", "成长"]
        negative_words = ["难过", "痛苦", "愤怒", "失望", "恐惧", "焦虑"]
        neutral_words = ["思考", "分析", "理解", "明白", "发现"]
        
        positive_count = sum(1 for word in positive_words if word in content)
        negative_count = sum(1 for word in negative_words if word in content)
        neutral_count = sum(1 for word in neutral_words if word in content)
        
        if positive_count > negative_count and positive_count > neutral_count:
            return "positive"
        elif negative_count > positive_count and negative_count > neutral_count:
            return "negative"
        else:
            return "neutral"
    
    def _determine_target_audience(self, profile: UserReadingProfile) -> str:
        """确定目标听众"""
        if profile.age_group == "teenager":
            return "年轻读者和学生"
        elif profile.profession == "parent":
            return "家长和教育工作者"
        elif profile.profession == "student":
            return "学生和年轻读者"
        else:
            return "广大阅读爱好者"
    
    def _extract_key_themes(self, insights: List[str]) -> List[str]:
        """提取关键主题"""
        themes = []
        
        # 简单的主题提取（可以后续优化）
        theme_keywords = {
            "生命": ["生命", "活着", "生存", "人生"],
            "爱情": ["爱情", "感情", "恋爱", "情感"],
            "成长": ["成长", "成熟", "学习", "进步"],
            "社会": ["社会", "时代", "历史", "文化"],
            "人性": ["人性", "善恶", "道德", "伦理"],
            "家庭": ["家庭", "亲情", "友情", "关系"]
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in " ".join(insights) for keyword in keywords):
                themes.append(theme)
        
        return themes
    
    def _generate_personal_signature(self, profile: UserReadingProfile) -> str:
        """生成个人特色描述"""
        signatures = []
        
        if profile.age_group == "teenager":
            signatures.append("年轻的声音")
        elif profile.profession == "parent":
            signatures.append("家长的视角")
        
        if profile.expression_style == "analytical":
            signatures.append("理性分析")
        elif profile.expression_style == "emotional":
            signatures.append("感性表达")
        
        return "，".join(signatures) if signatures else "独特的个人视角"

class PodcastGenerator:
    """播客生成器"""
    
    def __init__(self):
        self.content_processor = ContentProcessor()
    
    async def generate_podcast_content(self, session_id: str) -> Dict[str, Any]:
        """生成播客内容"""
        session = get_session(session_id)
        if not session:
            return {"error": "会话不存在"}
        
        # 组织内容结构
        podcast_structure = await self.content_processor.organize_content_structure(session)
        
        # 生成播客脚本
        podcast_script = self._generate_podcast_script(podcast_structure)
        
        # 生成播客元数据
        metadata = self._generate_metadata(session, podcast_structure)
        
        # 生成音频文件
        audio_result = await generate_podcast_audio(podcast_script, session_id)
        
        return {
            "session_id": session_id,
            "podcast_structure": podcast_structure.dict(),
            "podcast_script": podcast_script,
            "metadata": metadata,
            "audio_generation": audio_result,
            "suggestions": self._get_improvement_suggestions(session)
        }
    
    def _generate_podcast_script(self, structure: PodcastStructure) -> str:
        """生成播客脚本"""
        script = f"# {structure.title}\n\n"
        script += f"## {structure.subtitle}\n\n"
        
        for segment in structure.segments:
            script += f"### {segment.segment_type.upper()} (预计{segment.duration_estimate}秒)\n"
            script += f"{segment.content}\n\n"
        
        return script
    
    def _generate_metadata(self, session: InterviewSession, structure: PodcastStructure) -> Dict[str, Any]:
        """生成播客元数据"""
        return {
            "title": structure.title,
            "subtitle": structure.subtitle,
            "duration": structure.total_duration,
            "word_count": len(structure.segments),
            "target_audience": structure.target_audience,
            "key_themes": structure.key_themes,
            "personal_signature": structure.personal_signature,
            "generation_time": datetime.now().isoformat(),
            "conversation_count": len(session.conversation_history)
        }
    
    def _get_improvement_suggestions(self, session: InterviewSession) -> List[str]:
        """获取改进建议"""
        suggestions = []
        
        # 根据对话深度给出建议
        if len(session.conversation_history) < 5:
            suggestions.append("建议继续深入对话，以获得更丰富的内容")
        
        # 根据洞察数量给出建议
        if len(session.extracted_insights) < 3:
            suggestions.append("可以尝试分享更多个人感受和思考")
        
        # 根据阶段给出建议
        if session.current_stage != "creative_inspiration":
            suggestions.append("建议进入创作启发阶段，以获得更好的播客效果")
        
        return suggestions

# 全局播客生成器
podcast_generator = PodcastGenerator()

def get_podcast_generator() -> PodcastGenerator:
    """获取播客生成器实例"""
    return podcast_generator