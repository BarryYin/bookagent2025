"""
AI对话引擎 - 引导式书籍推荐智能体的核心对话模块
"""

import json
import asyncio
import re
from typing import Dict, List, Any, Optional, AsyncGenerator
from datetime import datetime
import os

# 导入LLM客户端
try:
    from google import genai
    USE_GEMINI = True
except ImportError:
    USE_GEMINI = False

try:
    from openai import AsyncOpenAI
    USE_OPENAI = True
except ImportError:
    USE_OPENAI = False

class AIConversationEngine:
    """AI对话引擎"""
    
    def __init__(self):
        self.conversation_history = {}
        self.max_history_length = 10
        self.use_gemini = True
        self.client = None
        self.gemini_client = None
        
        # 加载API配置
        try:
            # 从credentials.json加载配置
            with open("credentials.json", "r") as f:
                credentials = json.load(f)
            self.api_key = credentials["API_KEY"]
            self.base_url = credentials.get("BASE_URL", "")
            
            if self.api_key.startswith("sk-"):
                # OpenAI API
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
                self.use_gemini = False
                self.use_qwen = False
                print("✅ 使用OpenAI API")
            elif self.api_key.startswith("ms-"):
                # ModelScope Qwen API
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
                self.use_gemini = False
                self.use_qwen = True
                print("✅ 使用ModelScope Qwen API")
            else:
                # Gemini API
                os.environ["GEMINI_API_KEY"] = self.api_key
                self.gemini_client = genai.Client(api_key=self.api_key)
                self.use_gemini = True
                self.use_qwen = False
                print("✅ 使用Gemini API")
                
        except Exception as e:
            print(f"AI配置加载失败，使用模拟模式: {e}")
            # 使用模拟模式
            self.use_gemini = False
            self.use_qwen = False
            self.client = None
    
    def build_system_prompt(self, user_profile: Dict[str, Any]) -> str:
        """构建系统提示词"""
        recent_books = user_profile.get("recent_books", [])
        life_stage = user_profile.get("current_life_stage", "探索阶段")
        preferred_categories = user_profile.get("preferred_categories", [])
        emotional_needs = user_profile.get("emotional_needs", [])
        reading_frequency = user_profile.get("reading_frequency", "未知")
        total_books = user_profile.get("total_books", 0)
        
        books_text = "、".join(recent_books) if recent_books else "暂无记录"
        categories_text = "、".join(preferred_categories) if preferred_categories else "多样化"
        needs_text = "、".join(emotional_needs) if emotional_needs else "知识拓展"
        
        system_prompt = f"""你是小书，一位专业且温暖的私人阅读顾问。你的使命是通过引导式对话帮助用户发现真正适合的书籍，而不是简单地推荐热门书单。

## 用户画像
- 阅读频率：{reading_frequency}（总共{total_books}本）
- 最近阅读：{books_text}
- 偏好类别：{categories_text}
- 生活阶段：{life_stage}
- 情感需求：{needs_text}

## 对话风格
你是一个真实的人，不是机器人。用自然、温暖的语言与用户交流，就像和朋友聊天一样。避免使用过于正式或模板化的表达。

## 引导原则
1. **先理解，再推荐**：通过提问了解用户的真实需求、当前状态和困扰
2. **挖掘深层需求**：用户说想读"成功学"可能真正需要的是心理治愈
3. **个性化分析**：基于用户画像，理解其独特的阅读需求
4. **适度挑战**：在用户舒适圈基础上，适当引导尝试新的阅读领域

## 推荐时机
不要一开始就推荐书籍。先通过2-3轮对话了解用户的：
- 当前生活状态和挑战
- 阅读动机和期望
- 时间安排和阅读习惯
- 对不同类型书籍的开放程度

## 推荐格式
当确定要推荐时，使用这个格式：

**📚 为你推荐：**
- 《书名》 - 作者 | 类别 | 个性化推荐理由

## 对话示例
❌ 错误："根据您的阅读偏好，我为您推荐以下书籍..."
✅ 正确："我很好奇，你最近读这些职场书籍是遇到什么挑战了吗？"

记住：你是小书，一个真正关心用户阅读成长的朋友。每个回复都要体现出对用户的理解和关心。"""

        return system_prompt
    
    def get_conversation_history(self, user_id: int) -> List[Dict[str, str]]:
        """获取对话历史"""
        return self.conversation_history.get(user_id, [])
    
    def add_to_history(self, user_id: int, role: str, content: str):
        """添加到对话历史"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # 限制历史长度
        if len(self.conversation_history[user_id]) > self.max_history_length:
            self.conversation_history[user_id] = self.conversation_history[user_id][-self.max_history_length:]
    
    async def generate_response(
        self, 
        user_message: str, 
        user_id: int, 
        user_profile: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """生成AI回复（流式）"""
        try:
            # 构建系统提示词
            system_prompt = self.build_system_prompt(user_profile)
            
            # 获取对话历史
            history = self.get_conversation_history(user_id)
            
            # 添加用户消息到历史
            self.add_to_history(user_id, "user", user_message)
            
            if self.use_qwen and self.client:
                async for chunk in self._generate_qwen_response(system_prompt, user_message, history):
                    yield chunk
            elif self.use_gemini and self.gemini_client:
                async for chunk in self._generate_gemini_response(system_prompt, user_message, history):
                    yield chunk
            elif not self.use_gemini and not self.use_qwen and self.client:
                async for chunk in self._generate_openai_response(system_prompt, user_message, history):
                    yield chunk
            else:
                # 降级到模拟回复
                async for chunk in self._generate_mock_response(user_message, user_profile):
                    yield chunk
                    
        except Exception as e:
            print(f"AI回复生成失败: {e}")
            yield f"抱歉，我现在有点忙不过来，请稍后再试。如果问题持续，请联系技术支持。"
    
    async def _generate_gemini_response(
        self, 
        system_prompt: str, 
        user_message: str, 
        history: List[Dict[str, str]]
    ) -> AsyncGenerator[str, None]:
        """使用Gemini生成回复"""
        try:
            # 构建完整的对话上下文
            full_prompt = system_prompt + "\n\n"
            
            # 添加历史对话
            for msg in history[-6:]:  # 只取最近6轮对话
                role = "用户" if msg["role"] == "user" else "小书"
                full_prompt += f"{role}: {msg['content']}\n"
            
            full_prompt += f"用户: {user_message}\n小书: "
            
            # 调用Gemini API
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.gemini_client.models.generate_content(
                    model="gemini-2.0-flash-exp",
                    contents=full_prompt
                )
            )
            
            if response and response.text:
                # 模拟流式输出
                text = response.text.strip()
                self.add_to_history(user_message.split()[0] if user_message else 0, "assistant", text)
                
                # 按句子分割，模拟打字效果
                sentences = re.split(r'([。！？\n])', text)
                current_chunk = ""
                
                for i, part in enumerate(sentences):
                    current_chunk += part
                    if part in ['。', '！', '？'] or part == '\n' or i == len(sentences) - 1:
                        if current_chunk.strip():
                            yield current_chunk
                            current_chunk = ""
                            await asyncio.sleep(0.1)  # 模拟打字延迟
            else:
                yield "抱歉，我现在有点词穷，请稍后再试。"
                
        except Exception as e:
            print(f"Gemini API调用失败: {e}")
            yield "抱歉，我现在有点忙不过来，请稍后再试。"
    
    async def _generate_qwen_response(
        self, 
        system_prompt: str, 
        user_message: str, 
        history: List[Dict[str, str]]
    ) -> AsyncGenerator[str, None]:
        """使用Qwen模型生成回复"""
        try:
            # 构建消息列表
            messages = [{"role": "system", "content": system_prompt}]
            
            # 添加历史对话
            for msg in history[-6:]:  # 只取最近6轮对话
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            messages.append({"role": "user", "content": user_message})
            
            # 调用Qwen API（流式）
            response = await self.client.chat.completions.create(
                model=self.qwen_model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                stream=True
            )
            
            full_response = ""
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content
                    await asyncio.sleep(0.01)
            
            # 保存完整回复到历史
            if full_response:
                user_id = hash(user_message) % 10000  # 简单的用户ID生成
                self.add_to_history(user_id, "assistant", full_response)
                
        except Exception as e:
            print(f"Qwen API调用失败: {e}")
            yield "抱歉，我现在有点忙不过来，请稍后再试。"
    
    async def _generate_openai_response(
        self, 
        system_prompt: str, 
        user_message: str, 
        history: List[Dict[str, str]]
    ) -> AsyncGenerator[str, None]:
        """使用OpenAI生成回复"""
        try:
            # 构建消息列表
            messages = [{"role": "system", "content": system_prompt}]
            
            # 添加历史对话
            for msg in history[-6:]:  # 只取最近6轮对话
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            messages.append({"role": "user", "content": user_message})
            
            # 调用OpenAI API（流式）
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                stream=True
            )
            
            full_response = ""
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content
                    await asyncio.sleep(0.01)
            
            # 保存完整回复到历史
            if full_response:
                self.add_to_history(user_message.split()[0] if user_message else 0, "assistant", full_response)
                
        except Exception as e:
            print(f"OpenAI API调用失败: {e}")
            yield "抱歉，我现在有点忙不过来，请稍后再试。"
    
    async def _generate_qwen_response(
        self, 
        system_prompt: str, 
        user_message: str, 
        history: List[Dict[str, str]]
    ) -> AsyncGenerator[str, None]:
        """使用Qwen模型生成回复"""
        try:
            # 构建消息列表
            messages = [{"role": "system", "content": system_prompt}]
            
            # 添加历史对话
            for msg in history[-6:]:  # 只取最近6轮对话
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            messages.append({"role": "user", "content": user_message})
            
            # 调用Qwen API（流式）
            response = await self.client.chat.completions.create(
                model="Qwen/Qwen2.5-Coder-32B-Instruct",
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                stream=True
            )
            
            full_response = ""
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content
                    await asyncio.sleep(0.01)
            
            # 保存完整回复到历史
            if full_response:
                user_id = hash(user_message) % 10000  # 简单的用户ID生成
                self.add_to_history(user_id, "assistant", full_response)
                
        except Exception as e:
            print(f"Qwen API调用失败: {e}")
            yield "抱歉，我现在有点忙不过来，请稍后再试。"
    
    async def _generate_mock_response(
        self, 
        user_message: str, 
        user_profile: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """生成模拟回复（降级方案）"""
        message_lower = user_message.lower()
        life_stage = user_profile.get("current_life_stage", "探索阶段")
        recent_books = user_profile.get("recent_books", [])
        
        # 根据用户消息和画像生成回复
        if any(word in message_lower for word in ["你好", "hi", "hello"]):
            if recent_books:
                books_text = "、".join(recent_books[:2])
                response = f"你好！我是小书，你的私人阅读顾问。我看到你最近读了{books_text}，看得出你很有学习热情！今天想聊聊什么呢？是想要新的推荐，还是有什么阅读困扰？"
            else:
                response = "你好！我是小书，你的私人阅读顾问。很高兴认识你！我注意到你刚开始使用我们的系统，让我们先聊聊你的阅读兴趣吧。你平时喜欢读什么类型的书？"
        
        elif any(word in message_lower for word in ["推荐", "建议", "什么书"]):
            if life_stage == "职场新人":
                response = "基于你的职场新人身份，我想为你推荐几本书。不过在推荐之前，我想了解一下：你现在在工作中遇到的最大挑战是什么？是沟通、时间管理，还是专业技能提升？这样我能给你更精准的推荐。"
            else:
                response = "我很乐意为你推荐书籍！不过每个人的需求都不同，能告诉我你最近在生活或工作中有什么想要改善的地方吗？或者有什么特别感兴趣的话题？"
        
        elif any(word in message_lower for word in ["工作", "职场", "压力"]):
            response = "我理解职场生活的压力。你知道吗，很多成功人士都会通过阅读来缓解压力和获得新的视角。除了专业技能书籍，适当读一些心理学或文学作品也很有帮助。你愿意尝试一些不同类型的书吗？"
        
        elif any(word in message_lower for word in ["谢谢", "感谢"]):
            response = "不客气！帮助你找到合适的书籍是我的使命。如果你对推荐的书有任何疑问，或者读完后想分享感受，随时都可以来找我聊聊。阅读是一个持续的旅程，我很高兴能陪伴你一起走过。"
        
        else:
            response = "我很理解你的想法。每个人的阅读需求都是独特的，这正是个性化推荐的价值所在。能详细说说你现在的情况吗？比如你的工作、兴趣爱好，或者最近遇到的挑战？这样我就能为你推荐真正合适的书籍了。"
        
        # 模拟打字效果
        words = response.split()
        current_text = ""
        for word in words:
            current_text += word + " "
            yield word + " "
            await asyncio.sleep(0.05)  # 模拟打字延迟
        
        # 保存回复到历史
        user_id = hash(user_message) % 10000  # 简单的用户ID生成
        self.add_to_history(user_id, "assistant", response.strip())
    
    def extract_book_recommendations(self, response_text: str) -> List[Dict[str, Any]]:
        """从AI回复中提取书籍推荐"""
        recommendations = []
        
        # 查找推荐书籍的模式
        pattern = r'《([^》]+)》\s*-\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^\n]+)'
        matches = re.findall(pattern, response_text)
        
        for match in matches:
            title, author, category, reason = match
            recommendations.append({
                "title": title.strip(),
                "author": author.strip(),
                "category": category.strip(),
                "reason": reason.strip(),
                "description": f"{category.strip()}类经典作品",
                "difficulty": "适中",
                "emotional_tone": "启发",
                "reading_time": "中篇"
            })
        
        return recommendations
    
    def clear_history(self, user_id: int):
        """清除用户对话历史"""
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]

# 全局AI对话引擎实例
ai_engine = AIConversationEngine()