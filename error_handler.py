"""
书籍介绍系统 - 错误处理
"""
import logging
from typing import Dict, Any, Optional, Callable, Awaitable

from models import ProcessContext

# 配置日志
logger = logging.getLogger(__name__)

class ErrorHandler:
    """错误处理器"""
    
    def __init__(self):
        # 注册错误处理策略
        self.error_strategies = {
            "BookInfoCollector": self.handle_info_collection_error,
            "GuidewordGenerator": self.handle_guideword_generation_error,
            "PPTContentGenerator": self.handle_content_generation_error,
            "SpeechGenerator": self.handle_speech_generation_error,
            "HTMLGenerator": self.handle_html_generation_error,
            "AudioGenerator": self.handle_audio_generation_error,
        }
    
    async def handle_error(self, processor_name: str, error: Exception, context: ProcessContext) -> ProcessContext:
        """处理错误"""
        logger.error(f"{processor_name} 处理过程中发生错误: {error}", exc_info=True)
        
        # 查找对应的错误处理策略
        handler = self.error_strategies.get(processor_name)
        if handler:
            try:
                return await handler(error, context)
            except Exception as e:
                logger.error(f"错误处理失败: {e}", exc_info=True)
        
        # 如果没有特定处理策略或处理失败，记录错误并返回原始上下文
        context.current_output = {
            "error": True,
            "message": f"处理失败: {str(error)}",
            "processor": processor_name
        }
        return context
    
    async def handle_info_collection_error(self, error: Exception, context: ProcessContext) -> ProcessContext:
        """处理信息收集错误"""
        logger.warning(f"信息收集失败，使用基本信息: {error}")
        
        # 设置错误标志和消息
        context.current_output = {
            "error": True,
            "message": "无法收集完整的书籍信息，将使用基本信息继续",
            "details": str(error)
        }
        
        return context
    
    async def handle_guideword_generation_error(self, error: Exception, context: ProcessContext) -> ProcessContext:
        """处理引导词生成错误"""
        logger.warning(f"引导词生成失败，使用默认模板: {error}")
        
        # 创建默认引导词
        default_guidewords = f"""
        核心主题：{context.book_info.title} 书籍介绍
        
        关键观点：
        1. 作者 {context.book_info.author} 的写作风格和背景
        2. 本书的主要内容和结构
        3. 本书的社会影响和评价
        
        目标受众：
        - 对该主题感兴趣的读者
        - 文学爱好者
        
        推荐理由：
        - 内容独特
        - 见解深刻
        
        内容结构建议：
        1. 书籍和作者介绍
        2. 主要内容概述
        3. 精彩片段
        4. 阅读建议
        """
        
        context.guidewords = default_guidewords
        context.current_output = {
            "error": True,
            "message": "引导词生成失败，使用默认模板",
            "guidewords_preview": default_guidewords[:100] + "...",
            "details": str(error)
        }
        
        return context
    
    async def handle_content_generation_error(self, error: Exception, context: ProcessContext) -> ProcessContext:
        """处理内容生成错误"""
        logger.warning(f"内容生成失败: {error}")
        
        context.current_output = {
            "error": True,
            "message": "PPT内容生成失败，请重试",
            "details": str(error)
        }
        
        return context
    
    async def handle_speech_generation_error(self, error: Exception, context: ProcessContext) -> ProcessContext:
        """处理演讲稿生成错误"""
        logger.warning(f"演讲稿生成失败: {error}")
        
        context.current_output = {
            "error": True,
            "message": "演讲稿生成失败，将只提供PPT内容",
            "details": str(error)
        }
        
        return context
    
    async def handle_html_generation_error(self, error: Exception, context: ProcessContext) -> ProcessContext:
        """处理HTML生成错误"""
        logger.warning(f"HTML生成失败: {error}")
        
        context.current_output = {
            "error": True,
            "message": "HTML生成失败，请重试",
            "details": str(error)
        }
        
        return context
    
    async def handle_audio_generation_error(self, error: Exception, context: ProcessContext) -> ProcessContext:
        """处理音频生成错误"""
        logger.warning(f"音频生成失败: {error}")
        
        context.current_output = {
            "error": True,
            "message": "音频生成失败，将提供无音频版本",
            "details": str(error)
        }
        
        return context