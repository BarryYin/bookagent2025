"""
基于workflow_openapi_demo_python.py的智能对话API
集成星火大模型工作流，为推荐代理提供对话支持
"""

import http.client
import json
import ssl
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowChatEngine:
    """基于星火工作流的对话引擎"""
    
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            "Authorization": "Bearer f2d4b9650c13355fc8286ac3fc34bf6e:NzRkOWNlZDUzZThjMDI5NzI0N2EyMGRh",
        }
        self.host = "xingchen-api.xf-yun.com"
        self.endpoint = "/workflow/v1/chat/completions"
        self.flow_id = "7362838041572466690"
        
    async def send_message(self, user_input: str, user_id: str = "123", stream: bool = False) -> Dict[str, Any]:
        """
        发送消息到工作流并获取响应
        
        Args:
            user_input: 用户输入消息
            user_id: 用户ID
            stream: 是否启用流式响应
            
        Returns:
            包含响应内容的字典
        """
        try:
            # 构建请求数据
            data = {
                "flow_id": self.flow_id,
                "uid": user_id,
                "parameters": {"AGENT_USER_INPUT": user_input},
                "ext": {"bot_id": "recommendation_agent", "caller": "workflow"},
                "stream": stream,
            }
            
            payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
            logger.info(f"发送请求到工作流: {user_input}")
            
            # 建立连接并发送请求
            conn = http.client.HTTPSConnection(self.host, timeout=120)
            conn.request("POST", self.endpoint, payload, self.headers)
            res = conn.getresponse()
            
            if stream:
                # 处理流式响应
                response_text = ""
                while chunk := res.readline():
                    chunk_text = chunk.decode("utf-8").strip()
                    if chunk_text:
                        response_text += chunk_text + "\n"
                
                return {
                    "success": True,
                    "message": response_text.strip(),
                    "timestamp": datetime.now().isoformat(),
                    "type": "stream"
                }
            else:
                # 处理普通响应
                response_data = res.read()  # 使用read()而不是readline()读取完整响应
                response_text = response_data.decode("utf-8").strip()
                
                logger.info(f"工作流原始响应: {response_text[:500]}...")  # 记录原始响应
                
                # 检查HTTP状态码
                if res.status != 200:
                    logger.error(f"工作流HTTP错误: {res.status} - {res.reason}")
                    return {
                        "success": False,
                        "message": f"工作流服务返回错误: {res.status} {res.reason}",
                        "error": f"HTTP {res.status}",
                        "timestamp": datetime.now().isoformat()
                    }
                
                # 如果响应为空
                if not response_text:
                    logger.warning("工作流返回空响应")
                    return {
                        "success": False,
                        "message": "工作流返回了空响应，可能服务暂时不可用",
                        "error": "Empty response",
                        "timestamp": datetime.now().isoformat()
                    }
                
                # 尝试解析JSON响应
                try:
                    parsed_response = json.loads(response_text)
                    logger.info(f"解析后的响应: {parsed_response}")
                    
                    # 处理工作流API的特殊响应格式
                    message = ""
                    
                    # 处理星火工作流的标准响应格式
                    if "choices" in parsed_response and len(parsed_response["choices"]) > 0:
                        choice = parsed_response["choices"][0]
                        if "delta" in choice and "content" in choice["delta"]:
                            message = choice["delta"]["content"]
                        elif "message" in choice and "content" in choice["message"]:
                            message = choice["message"]["content"]
                    
                    # 备用解析方式 - 注意：不使用"message"字段，因为它通常是状态信息
                    if not message:
                        if "output" in parsed_response:
                            message = parsed_response["output"]
                        elif "result" in parsed_response:
                            message = parsed_response["result"]
                        elif "data" in parsed_response and isinstance(parsed_response["data"], str):
                            message = parsed_response["data"]
                        # 不使用"message"字段，因为它通常是API状态信息而不是AI回复
                        # elif "message" in parsed_response:
                        #     message = parsed_response["message"]
                        else:
                            # 如果没有找到标准字段，检查是否有错误
                            if parsed_response.get("code") != 0:
                                # 错误情况，使用错误消息
                                message = parsed_response.get("message", "工作流返回了错误")
                            else:
                                # 其他情况，生成默认消息
                                message = "抱歉，我现在无法回复您的消息。"
                        
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON解析失败: {e}, 使用原始文本")
                    message = response_text
                
                # 确保message不为空
                if not message or message.strip() == "":
                    logger.warning("解析后的消息为空")
                    message = "抱歉，我收到了您的消息，但现在无法给出回复。请稍后再试。"
                
                return {
                    "success": True,
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                    "type": "normal",
                    "raw_response": response_text
                }
                
        except Exception as e:
            logger.error(f"工作流请求失败: {str(e)}")
            return {
                "success": False,
                "message": "抱歉，我现在无法回复您的消息。请稍后再试。",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        finally:
            if 'conn' in locals():
                conn.close()

    async def chat_with_context(self, user_input: str, user_id: str, conversation_history: list = None) -> Dict[str, Any]:
        """
        带上下文的对话
        
        Args:
            user_input: 用户输入
            user_id: 用户ID
            conversation_history: 对话历史
            
        Returns:
            对话响应
        """
        # 构建带上下文的输入
        if conversation_history:
            # 将历史对话添加到用户输入中作为上下文
            context = "\n".join([
                f"用户: {msg['content']}" if msg['role'] == 'user' else f"助手: {msg['content']}"
                for msg in conversation_history[-5:]  # 只保留最近5轮对话
            ])
            enhanced_input = f"对话历史:\n{context}\n\n当前问题: {user_input}"
        else:
            enhanced_input = user_input
            
        return await self.send_message(enhanced_input, user_id)

    def test_connection(self) -> bool:
        """测试连接是否正常"""
        try:
            test_response = asyncio.run(self.send_message("你好"))
            return test_response.get("success", False)
        except Exception as e:
            logger.error(f"连接测试失败: {str(e)}")
            return False

# 全局对话引擎实例
workflow_engine = WorkflowChatEngine()

async def handle_recommendation_chat(user_input: str, user_id: str, history: list = None) -> Dict[str, Any]:
    """
    处理推荐代理的对话请求
    
    Args:
        user_input: 用户输入
        user_id: 用户ID  
        history: 对话历史
        
    Returns:
        对话响应
    """
    try:
        # 极简化prompt，避免414错误
        recommendation_prompt = user_input  # 直接使用用户输入，不添加任何前缀
        
        # 直接调用send_message，避免chat_with_context添加更多上下文
        response = await workflow_engine.send_message(
            recommendation_prompt, 
            user_id
        )
        
        # 如果响应成功，可以在这里添加推荐书籍的逻辑
        if response.get("success"):
            # 这里可以集成现有的推荐系统
            response["recommendations"] = []  # 暂时为空，后续可以集成推荐逻辑
            response["should_recommend"] = "推荐" in response.get("message", "")
            
        return response
        
    except Exception as e:
        logger.error(f"处理推荐对话失败: {str(e)}")
        return {
            "success": False,
            "message": "抱歉，我暂时无法回复您的问题。请稍后再试。",
            "error": str(e)
        }

def get_simplified_user_context(user_id: str) -> str:
    """
    获取简化的用户背景信息，避免内容过长
    """
    try:
        if user_id == "test_user":
            return "偏好心理学、自我成长类书籍"
        
        # 其他用户的简化逻辑
        return "通用阅读偏好"
    except Exception as e:
        logger.error(f"获取简化用户背景失败: {e}")
        return "通用阅读偏好"

def get_user_reading_context(user_id: str) -> str:
    """
    获取用户阅读背景信息，用于个性化对话
    
    Args:
        user_id: 用户ID
        
    Returns:
        格式化的用户背景信息字符串
    """
    try:
        # 如果是测试用户，返回模拟数据
        if user_id == "test_user":
            return get_mock_user_context()
        
        # 尝试从数据库获取真实用户数据
        import sqlite3
        conn = sqlite3.connect("fogsight.db")
        cursor = conn.cursor()
        
        # 获取用户的PPT生成记录（代表用户的阅读兴趣）
        cursor.execute("""
            SELECT title, author, category_name, created_at 
            FROM ppts 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT 10
        """, (int(user_id),))
        
        user_books = cursor.fetchall()
        conn.close()
        
        if not user_books:
            return get_mock_user_context()
        
        # 分析用户偏好
        categories = {}
        recent_books = []
        
        for book in user_books:
            title, author, category, created_at = book
            recent_books.append(f"《{title}》- {author}")
            
            if category:
                categories[category] = categories.get(category, 0) + 1
        
        # 找出最喜欢的分类
        preferred_categories = sorted(categories.keys(), key=lambda x: categories[x], reverse=True)[:3]
        
        # 构建用户画像文本
        context_parts = []
        
        if recent_books:
            context_parts.append(f"- 最近关注的书籍: {', '.join(recent_books[:5])}")
        
        if preferred_categories:
            context_parts.append(f"- 偏好的书籍类别: {', '.join(preferred_categories)}")
            
        context_parts.append(f"- 用户活跃度: 生成了{len(user_books)}个书籍介绍")
        
        # 推断阅读特征
        total_books = len(user_books)
        if total_books >= 8:
            reading_level = "高频阅读者，对读书有很深的热爱"
        elif total_books >= 4:
            reading_level = "中等频率阅读者，有一定的阅读习惯"
        else:
            reading_level = "初步阅读者，刚开始培养阅读兴趣"
            
        context_parts.append(f"- 阅读特征: {reading_level}")
        
        return "\n".join(context_parts)
        
    except Exception as e:
        logger.error(f"获取用户画像失败: {str(e)}")
        return get_mock_user_context()

def get_mock_user_context() -> str:
    """
    获取模拟用户画像数据
    """
    mock_contexts = [
        """- 最近关注的书籍: 《人类简史》- 尤瓦尔·赫拉利, 《原则》- 瑞·达利欧, 《活着》- 余华
- 偏好的书籍类别: 历史传记, 职场技能, 文学经典
- 阅读特征: 高频阅读者，对读书有很深的热爱
- 特殊兴趣: 喜欢思辨性强的书籍，关注个人成长""",
        
        """- 最近关注的书籍: 《百年孤独》- 加西亚·马尔克斯, 《三体》- 刘慈欣, 《心理学与生活》- 格里格
- 偏好的书籍类别: 科幻小说, 心理学, 文学经典  
- 阅读特征: 中等频率阅读者，有一定的阅读习惯
- 特殊兴趣: 喜欢科幻和心理类书籍，注重精神世界的丰富""",
        
        """- 最近关注的书籍: 《被讨厌的勇气》- 岸见一郎, 《刻意练习》- 安德斯·艾利克森, 《金字塔原理》- 芭芭拉·明托
- 偏好的书籍类别: 心理学, 职场技能, 自我成长
- 阅读特征: 目标导向的阅读者，重视实用性
- 特殊兴趣: 专注于自我提升和职场能力发展"""
    ]
    
    import random
    return random.choice(mock_contexts)

if __name__ == "__main__":
    # 测试代码
    async def test_chat():
        engine = WorkflowChatEngine()
        
        # 测试连接
        if engine.test_connection():
            print("✅ 工作流连接正常")
        else:
            print("❌ 工作流连接失败")
            return
            
        # 测试对话
        response = await handle_recommendation_chat("能帮我推荐几本好书吗？", "test_user")
        print(f"响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
        
    # 运行测试
    asyncio.run(test_chat())
