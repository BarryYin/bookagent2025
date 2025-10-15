"""
书籍封面OCR识别模块
支持从书籍封面图片中提取书名和作者信息
"""

import base64
import json
import re
from typing import Dict, Optional
from openai import AsyncOpenAI


class BookCoverOCR:
    """书籍封面OCR识别器"""
    
    def __init__(self):
        """初始化OCR识别器"""
        self.client = AsyncOpenAI(
            base_url='https://qianfan.baidubce.com/v2',
            api_key='bce-v3/ALTAK-IlAGWrpPIFAMJ3g8kbD4I/f17c0a909b891c89b0dce53d913448d86a87bad9'
        )
    
    async def recognize_from_image(self, image_data: bytes) -> Dict[str, Optional[str]]:
        """
        从图片数据中识别书名和作者
        
        Args:
            image_data: 图片的二进制数据
            
        Returns:
            包含书名和作者的字典
        """
        try:
            # 将图片转换为base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # 调用百度视觉模型
            response = await self.client.chat.completions.create(
                model="ernie-4.5-turbo-vl-latest",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            },
                            {
                                "type": "text",
                                "text": "请识别这张书籍封面图片中的书名和作者信息。只返回JSON格式：{\"title\": \"书名\", \"author\": \"作者\"}"
                            }
                        ]
                    }
                ],
                temperature=0.2,
                top_p=0.8
            )
            
            result_text = response.choices[0].message.content
            return self._parse_result(result_text)
                
        except Exception as e:
            print(f"OCR识别出错: {e}")
            return {"title": None, "author": None, "error": str(e)}
    
    def _parse_result(self, result_text: str) -> Dict[str, Optional[str]]:
        """
        解析模型返回的结果
        """
        try:
            # 尝试提取JSON
            json_match = re.search(r'\{[^}]+\}', result_text)
            if json_match:
                data = json.loads(json_match.group())
                return {
                    "title": data.get("title"),
                    "author": data.get("author"),
                    "success": True
                }
            
            # 如果没有JSON，尝试从文本中提取
            title_match = re.search(r'书名[：:](.*?)(?:作者|$)', result_text)
            author_match = re.search(r'作者[：:](.*?)(?:$|\n)', result_text)
            
            return {
                "title": title_match.group(1).strip() if title_match else None,
                "author": author_match.group(1).strip() if author_match else None,
                "success": bool(title_match or author_match)
            }
            
        except Exception as e:
            print(f"解析结果出错: {e}")
            return {"title": None, "author": None, "error": str(e)}
    
    async def recognize_from_file(self, file_path: str) -> Dict[str, Optional[str]]:
        """
        从文件路径识别书名和作者
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            包含书名和作者的字典
        """
        try:
            with open(file_path, 'rb') as f:
                image_data = f.read()
            return await self.recognize_from_image(image_data)
        except Exception as e:
            print(f"读取文件出错: {e}")
            return {"title": None, "author": None, "error": str(e)}


# 全局OCR识别器实例
_ocr_instance = None

def get_ocr_instance() -> BookCoverOCR:
    """获取OCR识别器单例"""
    global _ocr_instance
    if _ocr_instance is None:
        _ocr_instance = BookCoverOCR()
    return _ocr_instance
