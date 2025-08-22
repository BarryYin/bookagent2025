#!/usr/bin/env python3
"""
双AI协作访谈引擎
对话AI + 播客生成AI 协作系统
"""
import json
import asyncio
import re
import uuid
import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from openai import AsyncOpenAI

# 异步HTTP和文件操作依赖
try:
    import aiohttp
    import aiofiles
except ImportError:
    print("警告：缺少异步依赖，请安装: pip install aiohttp aiofiles")
    aiohttp = None
    aiofiles = None

# 导入播客数据库功能
try:
    from podcast_database import save_podcast_to_database, init_podcast_database
except ImportError:
    print("警告：无法导入播客数据库模块，播客将不会保存到数据库")
    def save_podcast_to_database(*args, **kwargs):
        return None
    def init_podcast_database():
        pass

# Qwen配置
QWEN_BASE_URL = "https://api-inference.modelscope.cn/v1/"
QWEN_API_KEY = "ms-076e7668-1000-4ce8-be4e-f475ddfeead7"
QWEN_MODEL = "Qwen/Qwen3-Coder-480B-A35B-Instruct"

qwen_client = AsyncOpenAI(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL)

class InterviewQuestion:
    """访谈问题模型"""
    def __init__(self, question: str, question_type: str, expected_content: str):
        self.question = question
        self.question_type = question_type  # opening, detail, emotion, reflection, creative
        self.expected_content = expected_content

class DualAISession:
    """双AI会话状态"""
    def __init__(self, session_id: str, book_title: str, book_author: str):
        self.session_id = session_id
        self.book_title = book_title
        self.book_author = book_author
        self.questions_asked = 0
        self.total_questions = 5
        self.conversation_history = []
        self.user_answers = []
        self.created_at = datetime.now()
        self.is_completed = False
        self.podcast_generated = False
        
    def add_qa_pair(self, question: str, answer: str):
        """添加问答对"""
        self.conversation_history.append({
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        })
        self.user_answers.append(answer)
        self.questions_asked += 1
        
    def is_ready_for_podcast(self) -> bool:
        """检查是否准备好生成播客"""
        return self.questions_asked >= self.total_questions and not self.podcast_generated

class ChatAI:
    """对话AI - 负责引导用户回答读后感问题"""
    
    def __init__(self):
        self.question_templates = {
            "opening": [
                "首先，能简单分享一下你对《{book_title}》的整体感受吗？这本书最打动你的是什么？",
                "读完《{book_title}》后，你的第一反应是什么？有什么特别深刻的印象吗？",
                "《{book_title}》这本书，哪个部分最让你印象深刻？为什么？"
            ],
            "detail": [
                "你觉得《{book_title}》中哪个角色或情节最能引起你的共鸣？能具体说说吗？",
                "这本书中有哪些观点或思想让你觉得很有启发？你是怎么理解的？",
                "读《{book_title}》的过程中，有没有让你重新思考某些问题的地方？"
            ],
            "emotion": [
                "在读《{book_title}》的时候，你的情感经历了怎样的变化？",
                "这本书是否改变了你对某些事情的看法？能分享一下吗？",
                "《{book_title}》让你联想到了自己生活中的哪些经历？"
            ],
            "reflection": [
                "读完《{book_title}》后，你觉得自己有什么收获或成长？",
                "如果要向朋友推荐这本书，你会怎么介绍它的价值？",
                "这本书对你今后的生活或思考方式有什么影响？"
            ],
            "creative": [
                "如果你是《{book_title}》的作者，你会如何继续这个故事？",
                "你觉得《{book_title}》还有哪些值得深入探讨的话题？",
                "读了这本书，你想对作者说些什么？或者有什么想法想分享给其他读者？"
            ]
        }
    
    async def generate_next_question(self, session: DualAISession) -> str:
        """生成下一个问题"""
        question_types = ["opening", "detail", "emotion", "reflection", "creative"]
        current_type = question_types[min(session.questions_asked, len(question_types) - 1)]
        
        # 使用LLM生成个性化问题
        system_prompt = f"""你是一个专业的读后感访谈主持人，善于引导读者深度分享读书感受。

当前访谈进度：第{session.questions_asked + 1}个问题（共{session.total_questions}个）
书籍：《{session.book_title}》作者：{session.book_author}
问题类型：{current_type}

请根据以下要求生成问题：
1. 问题要自然友好，像朋友间的对话
2. 避免过于学术化或刻板的表达
3. 引导用户分享具体的感受和思考
4. 问题长度控制在50字以内
5. 要体现对这本具体书籍的了解

历史对话：
{self._format_conversation_history(session)}"""

        user_prompt = f"请为《{session.book_title}》生成一个{current_type}类型的访谈问题。"
        
        try:
            response = await qwen_client.chat.completions.create(
                model=QWEN_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                max_tokens=200
            )
            
            question = response.choices[0].message.content.strip()
            # 清理可能的引号
            question = question.strip('"').strip("'").strip()
            return question
            
        except Exception as e:
            print(f"生成问题失败，使用模板: {e}")
            # 降级到模板问题
            import random
            templates = self.question_templates[current_type]
            question = random.choice(templates).format(book_title=session.book_title)
            return question
    
    def _format_conversation_history(self, session: DualAISession) -> str:
        """格式化对话历史"""
        if not session.conversation_history:
            return "（首次对话）"
        
        history = ""
        for qa in session.conversation_history[-2:]:  # 只显示最近2轮
            history += f"问：{qa['question']}\n答：{qa['answer']}\n\n"
        return history
    
    async def generate_completion_message(self, session: DualAISession) -> str:
        """生成访谈完成消息"""
        return f"""太棒了！我们的访谈已经完成了。通过这{session.questions_asked}个问题，我了解到了你对《{session.book_title}》的深度思考和感受。

现在，我将把你的精彩分享整理成一个个人读后感播客，让更多人能听到你独特的见解。点击下面的"生成播客"按钮开始制作吧！"""

class PodcastAI:
    """播客生成AI - 负责调用API生成播客内容"""
    
    def __init__(self):
        self.api_config = {
            "headers": {
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
                "Authorization": "Bearer f2d4b9650c13355fc8286ac3fc34bf6e:NzRkOWNlZDUzZThjMDI5NzI0N2EyMGRh",
            },
            "url": "https://xingchen-api.xf-yun.com/workflow/v1/chat/completions",
            "flow_id": "7362488342038495234"
        }
    
    async def generate_podcast(self, session: DualAISession) -> Dict[str, Any]:
        """生成播客内容"""
        try:
            # 整理用户回答
            user_content = self._compile_user_answers(session)
            
            # 调用星火API生成播客
            import aiohttp
            import json
            import re
            import aiofiles
            from datetime import datetime
            
            data = {
                "flow_id": self.api_config["flow_id"],
                "uid": session.session_id,
                "parameters": {
                    "AGENT_USER_INPUT": f"请根据以下读后感内容，生成一个个人读后感播客：\n\n书籍：《{session.book_title}》作者：{session.book_author}\n\n{user_content}"
                },
                "ext": {"bot_id": "dual_ai_interview", "caller": "workflow"},
                "stream": False,
            }
            
            # 使用异步HTTP客户端
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=120)) as session_http:
                async with session_http.post(
                    self.api_config["url"],
                    json=data,
                    headers=self.api_config["headers"]
                ) as response:
                    response_data = await response.text()
            
            # 解析流式响应
            print(f"播客API原始响应: {response_data[:500]}...")  # 调试信息
            
            if not response_data.strip():
                raise Exception("API返回空响应")
            
            # 处理流式响应格式 "data: {json}"
            html_content = ""
            try:
                if response_data.startswith("data: "):
                    # 解析流式响应
                    json_str = response_data[6:]  # 去掉 "data: " 前缀
                    response_json = json.loads(json_str)
                else:
                    # 普通JSON响应
                    response_json = json.loads(response_data)
                
                # 检查是否有错误
                if response_json.get("code") and response_json.get("code") != 200:
                    raise Exception(f"API错误: {response_json.get('message', '未知错误')}")
                
                html_content = response_json.get("choices", [{}])[0].get("delta", {}).get("content", "")
                
            except json.JSONDecodeError as e:
                raise Exception(f"API返回非JSON格式: {e} - 响应内容: {response_data[:200]}")
            except Exception as e:
                if "API错误" in str(e):
                    raise
                else:
                    raise Exception(f"解析响应失败: {e}")
            
            if not html_content:
                raise Exception("API返回内容为空")
            
            # 提取音频URL
            match = re.search(r'src="([^"]+)"', html_content)
            if not match:
                raise Exception("未找到音频URL")
            
            audio_url = match.group(1)
            
            # 异步下载音频文件
            async with aiohttp.ClientSession() as session_http:
                async with session_http.get(audio_url) as response:
                    if response.status != 200:
                        raise Exception(f"下载音频失败: HTTP {response.status}")
                    audio_data = await response.read()
            
            # 异步保存音频文件
            output_dir = "podcast_audio"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"reading_podcast_{session.session_id}_{timestamp}.mp3"
            file_path = os.path.join(output_dir, file_name)
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(audio_data)
            
            # 标记播客已生成
            session.podcast_generated = True
            
            # 保存到播客数据库
            try:
                init_podcast_database()  # 确保数据库已初始化
                
                # 生成播客描述
                description = f"关于《{session.book_title}》的读后感播客，分享了深刻的阅读感悟和思考。"
                
                podcast_id = save_podcast_to_database(
                    session_id=session.session_id,
                    book_title=session.book_title,
                    book_author=session.book_author,
                    description=description,
                    script_content=html_content,
                    audio_url=audio_url,
                    audio_file_path=file_path
                )
                
                if podcast_id:
                    print(f"✅ 播客已保存到数据库: ID {podcast_id}")
                else:
                    print(f"⚠️ 播客保存到数据库失败")
                    
            except Exception as db_error:
                print(f"保存播客到数据库失败: {db_error}")
                # 不影响主流程，继续返回结果
            
            return {
                "success": True,
                "audio_url": audio_url,
                "local_file": file_path,
                "script": html_content,
                "session_id": session.session_id,
                "book_title": session.book_title,
                "book_author": session.book_author
            }
            
        except Exception as e:
            print(f"播客生成失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session.session_id
            }
    
    def _compile_user_answers(self, session: DualAISession) -> str:
        """整理用户回答"""
        content = f"读者对《{session.book_title}》的深度分享：\n\n"
        
        for i, qa in enumerate(session.conversation_history, 1):
            content += f"问题{i}：{qa['question']}\n"
            content += f"回答：{qa['answer']}\n\n"
        
        return content

class DualAIInterviewEngine:
    """双AI协作访谈引擎"""
    
    def __init__(self):
        self.chat_ai = ChatAI()
        self.podcast_ai = PodcastAI()
        self.sessions = {}  # 内存中的会话存储
    
    def start_interview(self, book_title: str, book_author: str, user_intro: str = "") -> Dict[str, Any]:
        """开始访谈"""
        # 生成短的session_id（API要求不超过40字符）
        session_id = f"ai_{str(uuid.uuid4()).replace('-', '')[:30]}"
        session = DualAISession(session_id, book_title, book_author)
        self.sessions[session_id] = session
        
        # 生成开场白
        opening_message = f"""你好！很高兴你选择分享对《{book_title}》的读后感。我是你的访谈助手，将通过几个问题来了解你的阅读体验和感受。

我们的对话会很轻松自然，就像朋友间的读书交流。准备好了吗？让我们开始吧！"""
        
        return {
            "session_id": session_id,
            "opening_message": opening_message,
            "total_questions": session.total_questions,
            "current_question": 0,
            "book_title": book_title,
            "book_author": book_author
        }
    
    async def process_user_message(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """处理用户消息"""
        if session_id not in self.sessions:
            return {"error": "会话不存在"}
        
        session = self.sessions[session_id]
        
        if session.is_completed:
            return {"error": "访谈已完成"}
        
        # 如果是第一条消息（用户说"开始访谈"），生成第一个问题
        if session.questions_asked == 0 and user_message in ["开始访谈", "start"]:
            question = await self.chat_ai.generate_next_question(session)
            return {
                "type": "question",
                "question": question,
                "current_question": 1,
                "total_questions": session.total_questions,
                "session_id": session_id
            }
        
        # 处理用户的实际回答
        if session.conversation_history and session.conversation_history[-1]["answer"] == "":
            # 用户正在回答最后一个问题
            last_question = session.conversation_history[-1]["question"]
            session.conversation_history[-1]["answer"] = user_message
            session.questions_asked += 1
            
            # 检查是否完成访谈
            if session.is_ready_for_podcast():
                session.is_completed = True
                completion_message = await self.chat_ai.generate_completion_message(session)
                return {
                    "type": "completion",
                    "message": completion_message,
                    "ready_for_podcast": True,
                    "session_id": session_id,
                    "total_answered": session.questions_asked
                }
            
            # 生成下一个问题
            next_question = await self.chat_ai.generate_next_question(session)
            # 添加问题到历史（等待用户回答）
            session.conversation_history.append({
                "question": next_question,
                "answer": "",  # 等待回答
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "type": "question",
                "question": next_question,
                "current_question": session.questions_asked + 1,
                "total_questions": session.total_questions,
                "session_id": session_id
            }
        
        # 如果没有待回答的问题，可能是第一次真正的用户输入
        if not session.conversation_history:
            # 将用户输入作为第一个问题的回答
            first_question = await self.chat_ai.generate_next_question(session)
            session.conversation_history.append({
                "question": first_question,
                "answer": user_message,
                "timestamp": datetime.now().isoformat()
            })
            session.questions_asked += 1
            
            # 检查是否完成访谈
            if session.is_ready_for_podcast():
                session.is_completed = True
                completion_message = await self.chat_ai.generate_completion_message(session)
                return {
                    "type": "completion",
                    "message": completion_message,
                    "ready_for_podcast": True,
                    "session_id": session_id,
                    "total_answered": session.questions_asked
                }
            
            # 生成下一个问题
            next_question = await self.chat_ai.generate_next_question(session)
            session.conversation_history.append({
                "question": next_question,
                "answer": "",  # 等待回答
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "type": "question",
                "question": next_question,
                "current_question": session.questions_asked + 1,
                "total_questions": session.total_questions,
                "session_id": session_id
            }
        
        return {"error": "未知状态"}
    
    async def generate_podcast(self, session_id: str) -> Dict[str, Any]:
        """生成播客 - 异步处理避免阻塞"""
        if session_id not in self.sessions:
            return {"error": "会话不存在"}
        
        session = self.sessions[session_id]
        
        if not session.is_ready_for_podcast():
            return {"error": "访谈尚未完成，无法生成播客"}
        
        if session.podcast_generated:
            return {"error": "播客已经生成过了"}
        
        # 直接异步生成播客，但不阻塞API响应
        result = await self.podcast_ai.generate_podcast(session)
        return result
    
    async def _generate_podcast_background(self, session: DualAISession):
        """后台生成播客"""
        try:
            result = await self.podcast_ai.generate_podcast(session)
            # 可以在这里添加通知机制，比如WebSocket推送结果
            print(f"播客生成完成: {result}")
        except Exception as e:
            print(f"后台播客生成失败: {e}")
    
    def get_podcast_status(self, session_id: str) -> Dict[str, Any]:
        """获取播客生成状态"""
        if session_id not in self.sessions:
            return {"error": "会话不存在"}
        
        session = self.sessions[session_id]
        return {
            "session_id": session_id,
            "podcast_generated": session.podcast_generated,
            "status": "completed" if session.podcast_generated else "processing"
        }
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """获取会话状态"""
        if session_id not in self.sessions:
            return {"error": "会话不存在"}
        
        session = self.sessions[session_id]
        return {
            "session_id": session_id,
            "book_title": session.book_title,
            "book_author": session.book_author,
            "questions_asked": session.questions_asked,
            "total_questions": session.total_questions,
            "is_completed": session.is_completed,
            "ready_for_podcast": session.is_ready_for_podcast(),
            "podcast_generated": session.podcast_generated,
            "conversation_history": session.conversation_history
        }

# 全局引擎实例
_dual_ai_engine = None

def get_dual_ai_engine() -> DualAIInterviewEngine:
    """获取双AI引擎实例"""
    global _dual_ai_engine
    if _dual_ai_engine is None:
        _dual_ai_engine = DualAIInterviewEngine()
    return _dual_ai_engine

if __name__ == "__main__":
    # 测试代码
    import asyncio
    
    async def test_dual_ai():
        engine = get_dual_ai_engine()
        
        # 开始访谈
        result = engine.start_interview("三体", "刘慈欣", "我想分享读后感")
        print("开始访谈:", result)
        
        session_id = result["session_id"]
        
        # 模拟用户回答
        questions = [
            "这本书让我对宇宙有了全新的认识",
            "叶文洁这个角色很复杂，她的选择让我思考很多",
            "读的时候既震撼又恐惧，科幻设定太宏大了",
            "让我重新思考人类文明的脆弱性",
            "我觉得这本书会影响我对科学的看法"
        ]
        
        for i, answer in enumerate(questions):
            print(f"\n--- 第{i+1}轮对话 ---")
            result = await engine.process_user_message(session_id, answer)
            print(f"AI回复: {result}")
        
        # 生成播客
        print("\n--- 生成播客 ---")
        podcast_result = await engine.generate_podcast(session_id)
        print(f"播客结果: {podcast_result}")
    
    # asyncio.run(test_dual_ai())
