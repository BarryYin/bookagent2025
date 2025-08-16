"""
智能对话引导系统
"""
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from openai import AsyncOpenAI
from interview_user_model import InterviewSession, UserReadingProfile, get_session, update_session

# 配置LLM
QWEN_BASE_URL = "https://api-inference.modelscope.cn/v1/"
QWEN_API_KEY = "ms-076e7668-1000-4ce8-be4e-f475ddfeead7"
QWEN_MODEL = "Qwen/Qwen3-Coder-480B-A35B-Instruct"

llm_client = AsyncOpenAI(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL)

class DialogueStrategy:
    """对话策略基类"""
    
    def __init__(self):
        self.stage_prompts = {
            "ice_break": "开场破冰",
            "deep_dive": "深度挖掘",
            "perspective_clash": "观点碰撞",
            "creative_inspiration": "创作启发"
        }
    
    def generate_opening_question(self, session: InterviewSession) -> str:
        """生成开场问题"""
        profile = session.user_profile
        book = session.book_state.book_title
        
        # 根据用户画像生成个性化开场
        if profile.age_group == "teenager":
            return f"看起来你刚读完《{book}》，作为年轻人，这本书最让你震撼的是什么？"
        elif profile.profession == "student":
            return f"作为学生读《{book}》，有没有什么特别触动你的地方？"
        elif profile.profession == "parent":
            return f"作为家长读《{book}》，现在的感受怎么样？有什么特别想分享的吗？"
        else:
            return f"刚读完《{book}》，第一感觉如何？有什么想法想要分享吗？"
    
    def generate_follow_up_question(self, session: InterviewSession, user_message: str) -> str:
        """生成后续问题"""
        stage = session.current_stage
        profile = session.user_profile
        
        if stage == "ice_break":
            return self._ice_break_follow_up(profile, user_message)
        elif stage == "deep_dive":
            return self._deep_dive_follow_up(profile, user_message, session.book_state.book_title)
        elif stage == "perspective_clash":
            return self._perspective_clash_follow_up(profile, user_message)
        elif stage == "creative_inspiration":
            return self._creative_inspiration_follow_up(profile, user_message, session.book_state.book_title)
        else:
            return "能再多说一些你的想法吗？"
    
    def _ice_break_follow_up(self, profile: UserReadingProfile, user_message: str) -> str:
        """破冰阶段后续问题"""
        # 根据情感倾向调整问题
        if profile.emotional_tendency == "sensitive":
            return "这种感觉很正常，能具体说说哪个部分最触动你吗？"
        elif profile.emotional_tendency == "rational":
            return "很有意思的分析角度。你觉得这本书最想传达什么核心信息？"
        else:
            return "这个观点很独特。能再深入聊聊吗？"
    
    def _deep_dive_follow_up(self, profile: UserReadingProfile, user_message: str, book_title: str) -> str:
        """深度挖掘后续问题"""
        # 根据认知模式调整问题
        if profile.cognitive_pattern == "logical":
            return "从逻辑角度分析，你觉得这个角色的选择合理吗？为什么？"
        elif profile.cognitive_pattern == "intuitive":
            return "如果让你用直觉来感受，这个故事最打动你的是什么？"
        else:
            return f"让我们换个角度思考：如果你是《{book_title}》中的主角，你会做出不同的选择吗？"
    
    def _perspective_clash_follow_up(self, profile: UserReadingProfile, user_message: str) -> str:
        """观点碰撞后续问题"""
        # 引入不同视角
        contrast_questions = [
            "不过，有没有可能从另一个角度理解这个问题？",
            "这个观点很有意思，但考虑到当时的历史背景，你觉得呢？",
            "我理解你的看法，但如果我们站在其他角色的立场，会有什么不同的感受？",
            "这个观点很深刻，不过有没有可能被作者误导了？"
        ]
        
        import random
        return random.choice(contrast_questions)
    
    def _creative_inspiration_follow_up(self, profile: UserReadingProfile, user_message: str, book_title: str) -> str:
        """创作启发后续问题"""
        creative_prompts = [
            f"如果你来续写《{book_title}》的故事，下一步会发生什么？",
            f"想象一下，你要给没读过这本书的朋友推荐，你会怎么用三句话描述它？",
            f"如果《{book_title}》中的角色来到现实世界，你最想和谁对话？问什么问题？",
            f"根据你的理解，这本书最适合什么样的人阅读？为什么？"
        ]
        
        import random
        return random.choice(creative_prompts)

class InterviewDialogueEngine:
    """访谈对话引擎"""
    
    def __init__(self):
        self.strategy = DialogueStrategy()
        self.session_history = {}
    
    async def process_user_message(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """处理用户消息"""
        session = get_session(session_id)
        if not session:
            return {"error": "会话不存在"}
        
        # 生成AI回复
        ai_response = await self.generate_ai_response(session, user_message)
        
        # 更新会话状态
        update_session(session_id, user_message, ai_response)
        
        return {
            "response": ai_response,
            "stage": session.current_stage,
            "session_id": session_id,
            "suggestions": self.get_follow_up_suggestions(session)
        }
    
    async def generate_ai_response(self, session: InterviewSession, user_message: str) -> str:
        """生成AI回复"""
        conversation_count = len(session.conversation_history)
        
        if conversation_count == 0:
            # 第一次回复，使用开场问题
            return self.strategy.generate_opening_question(session)
        else:
            # 使用LLM生成智能回复
            return await self._generate_llm_response(session, user_message)
    
    async def _generate_llm_response(self, session: InterviewSession, user_message: str) -> str:
        """使用LLM生成智能回复"""
        profile = session.user_profile
        book_title = session.book_state.book_title
        stage = session.current_stage
        
        # 构建对话历史
        conversation_history = ""
        for conv in session.conversation_history[-3:]:  # 只使用最近3轮对话
            conversation_history += f"用户: {conv['user']}\n"
            conversation_history += f"访谈助手: {conv['ai']}\n"
        
        # 根据阶段和用户画像构建系统提示
        system_prompt = self._build_system_prompt(profile, book_title, stage)
        
        # 构建用户消息
        user_prompt = f"""
书籍：《{book_title}》
用户画像：{profile.age_group}，{profile.profession}，表达风格{profile.expression_style}
当前阶段：{stage}

对话历史：
{conversation_history}

用户最新消息：{user_message}

请根据用户的情况和当前访谈阶段，生成一个合适的回复。要求：
1. 语气友好自然，像真实的访谈对话
2. 根据用户画像调整表达方式
3. 引导用户进行更深度的思考
4. 保持对话的连贯性和深度
5. 回复长度在100-200字之间
"""
        
        try:
            response = await llm_client.chat.completions.create(
                model=QWEN_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content.strip()
            return ai_response
            
        except Exception as e:
            print(f"LLM调用失败: {e}")
            # 降级到模板回复
            return self.strategy.generate_follow_up_question(session, user_message)
    
    def _build_system_prompt(self, profile: UserReadingProfile, book_title: str, stage: str) -> str:
        """构建系统提示"""
        stage_descriptions = {
            "ice_break": "开场破冰阶段：让用户放松，建立信任，了解初步感受",
            "deep_dive": "深度挖掘阶段：深入探讨书籍内容，挖掘深层思考",
            "perspective_clash": "观点碰撞阶段：引入不同视角，激发思辨和讨论",
            "creative_inspiration": "创作启发阶段：引导用户进行创造性思考和个人表达"
        }
        
        profile_descriptions = {
            "teenager": "年轻读者，思维活跃，需要轻松活泼的交流方式",
            "young_adult": "年轻成年人，有一定的社会经验，可以进行深度交流",
            "adult": "成年读者，生活阅历丰富，能够进行成熟的思想交流",
            "middle_aged": "中年读者，人生经验丰富，可以进行深度的人生哲理讨论",
            "senior": "年长读者，智慧丰富，可以进行深刻的生命感悟交流"
        }
        
        stage_desc = stage_descriptions.get(stage, "深度交流")
        profile_desc = profile_descriptions.get(profile.age_group, "普通读者")
        
        return f"""
你是一位专业的读后感访谈助手，正在与读者进行关于《{book_title}》的深度对话。

当前阶段：{stage_desc}
用户特点：{profile_desc}

你的任务是：
1. 根据当前阶段的目标，引导用户进行相应的思考和表达
2. 使用适合用户特点的语言风格和交流方式
3. 通过有深度的问题，激发用户的思考和创造力
4. 保持对话的自然流畅，避免生硬的问答模式
5. 适时给予肯定和鼓励，建立良好的访谈氛围

请以访谈助手的身份回复，语气要自然、真诚、有启发性。
"""
    
    def get_follow_up_suggestions(self, session: InterviewSession) -> List[str]:
        """获取后续建议"""
        stage = session.current_stage
        profile = session.user_profile
        
        if stage == "ice_break":
            return [
                "分享你的第一感受",
                "谈谈最触动你的部分",
                "说说为什么选择这本书"
            ]
        elif stage == "deep_dive":
            return [
                "分析角色的内心世界",
                "探讨故事的主题思想",
                "联系个人经历思考"
            ]
        elif stage == "perspective_clash":
            return [
                "考虑不同的观点",
                "质疑自己的理解",
                "探索深层含义"
            ]
        elif stage == "creative_inspiration":
            return [
                "想象故事的延续",
                "创作相关内容",
                "分享给他人"
            ]
        else:
            return []
    
    def start_interview(self, book_title: str, book_author: str, user_intro: str) -> Dict[str, Any]:
        """开始访谈"""
        from interview_user_model import create_new_session
        
        # 创建新会话
        session = create_new_session(user_intro, book_title, book_author)
        
        # 生成开场白
        opening_response = self.strategy.generate_opening_question(session)
        
        # 记录第一次交互
        update_session(session.session_id, user_intro, opening_response)
        
        return {
            "session_id": session.session_id,
            "opening_message": opening_response,
            "user_profile": session.user_profile.dict(),
            "stage": session.current_stage
        }
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """获取会话总结"""
        session = get_session(session_id)
        if not session:
            return {"error": "会话不存在"}
        
        return {
            "session_id": session_id,
            "duration": (session.last_interaction - session.start_time).total_seconds(),
            "conversation_count": len(session.conversation_history),
            "current_stage": session.current_stage,
            "extracted_insights": session.extracted_insights,
            "user_profile": session.user_profile.dict()
        }

# 全局对话引擎
dialogue_engine = InterviewDialogueEngine()

def get_dialogue_engine() -> InterviewDialogueEngine:
    """获取对话引擎实例"""
    return dialogue_engine