"""
书籍介绍系统 - 处理器组件
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
import asyncio
import logging

from models import (
    BookInfo, Review, StructuredInfo, ProcessContext, 
    SlidesStructure, SlidesContent, SpeechScript, StyleConfig
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BaseProcessor(ABC):
    """处理器基类"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.logger = logging.getLogger(f"processor.{self.name}")
    
    @abstractmethod
    async def process(self, context: ProcessContext) -> ProcessContext:
        """处理方法，需要被子类实现"""
        pass
    
    async def handle_error(self, error: Exception, context: ProcessContext) -> ProcessContext:
        """错误处理方法，可被子类覆盖"""
        self.logger.error(f"处理错误: {error}", exc_info=True)
        raise error

class BookInfoCollector(BaseProcessor):
    """书籍信息收集器"""
    
    async def process(self, context: ProcessContext) -> ProcessContext:
        self.logger.info(f"开始收集书籍 '{context.book_info.title}' 的信息")
        
        try:
            # 搜索网络评价
            reviews = await self.search_reviews(context.book_info)
            self.logger.info(f"收集到 {len(reviews)} 条评价")
            
            # 结构化整理信息
            structured_info = await self.structure_information(context.book_info, reviews)
            context.structured_info = structured_info
            context.current_output = {
                "message": f"已收集 {context.book_info.title} 的信息和评价",
                "reviews_count": len(reviews)
            }
            
            return context
        except Exception as e:
            return await self.handle_error(e, context)
    
    async def search_reviews(self, book_info: BookInfo) -> List[Review]:
        """搜索书籍评价"""
        # 这里将来会实现实际的搜索逻辑
        # 目前返回模拟数据
        self.logger.info(f"搜索 '{book_info.title}' 的评价")
        await asyncio.sleep(1)  # 模拟网络请求延迟
        
        # 返回模拟评价
        return [
            Review(
                source="模拟评价源",
                rating=4.5,
                content=f"{book_info.title} 是一本非常精彩的书，作者 {book_info.author} 的写作风格独特。",
                reviewer="模拟评论者"
            )
        ]
    
    async def structure_information(self, book_info: BookInfo, reviews: List[Review]) -> StructuredInfo:
        """结构化整理信息"""
        # 这里将来会使用LLM进行信息整理
        # 目前返回模拟数据
        self.logger.info(f"结构化整理 '{book_info.title}' 的信息")
        await asyncio.sleep(1)  # 模拟处理延迟
        
        return StructuredInfo(
            book_details=book_info,
            reviews_summary="整体评价积极，读者普遍认为内容丰富，见解独到。",
            key_themes=["主题1", "主题2", "主题3"],
            target_audience="对该领域感兴趣的读者",
            strengths=["优点1", "优点2", "优点3"],
            criticisms=["批评1", "批评2"]
        )
    
    async def handle_error(self, error: Exception, context: ProcessContext) -> ProcessContext:
        """错误处理：如果网络搜索失败，使用模拟数据"""
        self.logger.warning(f"信息收集失败，使用模拟数据: {error}")
        
        # 创建基本的结构化信息
        context.structured_info = StructuredInfo(
            book_details=context.book_info,
            reviews_summary="无法获取在线评价，使用基本信息生成内容。",
            key_themes=["未知主题"],
            target_audience="一般读者",
            strengths=["未知优点"],
            criticisms=["未知缺点"]
        )
        
        context.current_output = {
            "message": f"无法获取 {context.book_info.title} 的在线评价，将使用基本信息",
            "reviews_count": 0,
            "error": str(error)
        }
        
        return context

class GuidewordGenerator(BaseProcessor):
    """引导词生成器"""
    
    async def process(self, context: ProcessContext) -> ProcessContext:
        self.logger.info(f"开始为 '{context.book_info.title}' 生成引导词")
        
        try:
            # 构建引导词提示
            prompt = self.build_guideword_prompt(context.structured_info)
            
            # 生成引导词（这里将来会调用LLM）
            guidewords = await self.generate_guidewords(prompt)
            context.guidewords = guidewords
            
            context.current_output = {
                "message": f"已为 {context.book_info.title} 生成引导词",
                "guidewords_preview": guidewords[:100] + "..." if len(guidewords) > 100 else guidewords
            }
            
            return context
        except Exception as e:
            return await self.handle_error(e, context)
    
    def build_guideword_prompt(self, info: StructuredInfo) -> str:
        """构建引导词提示"""
        return f"""
        基于以下书籍信息和评价，生成PPT制作的引导词：
        
        书籍信息：{info.book_details.title} (作者: {info.book_details.author})
        书籍描述：{info.book_details.description or '无描述'}
        网络评价：{info.reviews_summary}
        关键主题：{', '.join(info.key_themes)}
        目标受众：{info.target_audience}
        优点：{', '.join(info.strengths)}
        批评：{', '.join(info.criticisms)}
        
        请生成包含以下要素的引导词：
        1. 核心主题和关键观点
        2. 目标受众分析
        3. 推荐理由和亮点
        4. 内容结构建议
        """
    
    async def generate_guidewords(self, prompt: str) -> str:
        """生成引导词"""
        # 这里将来会调用LLM API
        # 目前返回模拟数据
        self.logger.info("生成引导词")
        await asyncio.sleep(1)  # 模拟API调用延迟
        
        return f"""
        核心主题：本书探讨了人类历史的发展脉络和关键转折点。
        
        关键观点：
        1. 农业革命如何改变了人类社会结构
        2. 工业革命带来的深远影响
        3. 信息时代对人类认知的挑战
        
        目标受众：
        - 历史爱好者和学生
        - 对社会发展感兴趣的读者
        - 希望了解人类文明演进的普通读者
        
        推荐理由：
        - 视角独特，将宏大历史与个人体验相结合
        - 语言生动，深入浅出
        - 提供了对未来的思考框架
        
        内容结构建议：
        1. 书籍概述和作者介绍
        2. 核心主题和观点展示
        3. 精彩章节摘录
        4. 读者评价和社会影响
        5. 阅读建议和延伸思考
        """
    
    async def handle_error(self, error: Exception, context: ProcessContext) -> ProcessContext:
        """错误处理：如果生成失败，使用基本模板"""
        self.logger.warning(f"引导词生成失败，使用基本模板: {error}")
        
        # 使用基本模板
        context.guidewords = f"""
        核心主题：介绍 {context.book_info.title}
        
        关键观点：
        1. 书籍主要内容概述
        2. 作者 {context.book_info.author} 的写作风格
        3. 本书的社会影响
        
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
        
        context.current_output = {
            "message": f"无法生成自定义引导词，使用基本模板",
            "guidewords_preview": context.guidewords[:100] + "...",
            "error": str(error)
        }
        
        return context

class ProcessOrchestrator:
    """流程编排器"""
    
    def __init__(self):
        self.processors = [
            BookInfoCollector(),
            GuidewordGenerator(),
            # 其他处理器将在后续任务中添加
        ]
        self.logger = logging.getLogger("orchestrator")
    
    async def process_book_introduction(self, book_info: BookInfo) -> Tuple[ProcessContext, List[Dict[str, Any]]]:
        """处理书籍介绍生成流程"""
        context = ProcessContext(book_info=book_info)
        progress_updates = []
        
        self.logger.info(f"开始处理书籍 '{book_info.title}' 的介绍生成")
        
        for i, processor in enumerate(self.processors):
            try:
                self.logger.info(f"执行处理器 {i+1}/{len(self.processors)}: {processor.name}")
                context = await processor.process(context)
                
                # 记录进度
                progress_percentage = (i + 1) / len(self.processors) * 100
                progress_updates.append({
                    "stage": processor.name,
                    "progress": progress_percentage,
                    "output": context.current_output
                })
                
                self.logger.info(f"处理器 {processor.name} 完成")
            except Exception as e:
                self.logger.error(f"处理器 {processor.name} 失败: {e}", exc_info=True)
                # 记录错误
                progress_updates.append({
                    "stage": processor.name,
                    "progress": (i + 0.5) / len(self.processors) * 100,
                    "error": str(e)
                })
                raise
        
        self.logger.info(f"书籍 '{book_info.title}' 的介绍生成完成")
        return context, progress_updates