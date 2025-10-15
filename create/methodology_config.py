#!/usr/bin/env python3
"""
书籍介绍方法论配置系统
整合不同类型书籍的介绍方法论
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

class MethodologyConfig:
    """方法论配置管理器"""
    
    def __init__(self):
        self.create_dir = Path(__file__).parent
        self.methodologies = self._load_methodologies()
    
    def _load_methodologies(self) -> Dict:
        """加载所有方法论配置"""
        return {
            "dongyu_literature": {
                "name": "董宇辉式文学作品介绍",
                "description": "深度情感共鸣，古今中外引用，精神财富挖掘",
                "file": "董宇辉式文学作品介绍方法论.md",
                "icon": "📚",
                "color": "#8B5A3C",
                "suitable_categories": ["文学类", "小说", "散文", "诗歌"],
                "features": [
                    "情感共鸣开场",
                    "个人经历植入", 
                    "古今中外引用",
                    "哲学思辨深度",
                    "精神价值升华"
                ]
            },
            "dongyu_autobiography": {
                "name": "董宇辉式自传体介绍",
                "description": "人生轨迹重构，关键选择分析，成长智慧提取",
                "file": "董宇辉式自传体书籍介绍方法论.md",
                "icon": "🎯",
                "color": "#2E7D32",
                "suitable_categories": ["传记", "自传", "回忆录", "人物传记"],
                "features": [
                    "反差感制造",
                    "人生轨迹重构",
                    "关键选择分析",
                    "成长智慧提取",
                    "励志价值传递"
                ]
            },
            "dongyu_fiction": {
                "name": "董宇辉式虚构类介绍",
                "description": "想象力激发，世界观构建，现实思考引导",
                "file": "董宇辉式虚构类书籍介绍方法论.md",
                "icon": "🌟",
                "color": "#7B1FA2",
                "suitable_categories": ["科幻", "奇幻", "悬疑", "恐怖", "玄幻"],
                "features": [
                    "想象情境开场",
                    "世界观构建",
                    "规则体系解析",
                    "现实对比思考",
                    "思维边界拓展"
                ]
            },
            "luozhenyu_efficiency": {
                "name": "罗振宇式效率提升介绍",
                "description": "认知升级路径，时代焦虑解析，实用方法论传递",
                "file": "罗振宇式效率提升类书籍介绍方法论.md",
                "icon": "⚡",
                "color": "#FF6F00",
                "suitable_categories": ["管理", "效率", "商业", "职场", "自我提升"],
                "features": [
                    "差距焦虑制造",
                    "认知升级路径",
                    "方法论拆解",
                    "底层逻辑揭示",
                    "行动指南提供"
                ]
            }
        }
    
    def get_methodology_by_name(self, name: str) -> Optional[Dict]:
        """根据名称获取方法论"""
        return self.methodologies.get(name)
    
    def get_suitable_methodologies(self, category: str) -> List[Dict]:
        """根据书籍分类推荐合适的方法论"""
        suitable = []
        category_lower = category.lower()
        
        for key, methodology in self.methodologies.items():
            for suitable_cat in methodology["suitable_categories"]:
                if suitable_cat.lower() in category_lower or category_lower in suitable_cat.lower():
                    methodology["key"] = key
                    suitable.append(methodology)
                    break
        
        # 如果没有匹配的，返回文学类作为默认
        if not suitable:
            default = self.methodologies["dongyu_literature"].copy()
            default["key"] = "dongyu_literature"
            suitable.append(default)
        
        return suitable
    
    def get_all_methodologies(self) -> List[Dict]:
        """获取所有方法论"""
        result = []
        for key, methodology in self.methodologies.items():
            methodology_copy = methodology.copy()
            methodology_copy["key"] = key
            result.append(methodology_copy)
        return result
    
    def load_methodology_content(self, methodology_key: str) -> str:
        """加载方法论的详细内容"""
        if methodology_key not in self.methodologies:
            return ""
        
        methodology = self.methodologies[methodology_key]
        file_path = self.create_dir / methodology["file"]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return f"方法论文件 {methodology['file']} 未找到"
        except Exception as e:
            return f"读取方法论文件失败: {str(e)}"
    
    def generate_methodology_prompt(self, methodology_key: str, book_info: Dict) -> str:
        """根据方法论和书籍信息生成提示词"""
        methodology = self.get_methodology_by_name(methodology_key)
        if not methodology:
            return ""
        
        content = self.load_methodology_content(methodology_key)
        
        prompt = f"""
请使用 {methodology['name']} 来介绍书籍《{book_info.get('title', '')}》。

**方法论特点：**
{methodology['description']}

**核心要素：**
{chr(10).join(['- ' + feature for feature in methodology['features']])}

**方法论详细内容：**
{content}

**书籍信息：**
- 书名：{book_info.get('title', '未知')}
- 作者：{book_info.get('author', '未知')}
- 分类：{book_info.get('category', '未知')}
- 简介：{book_info.get('description', '无')}

请严格按照该方法论的结构和风格来创作书籍介绍内容。
        """
        
        return prompt.strip()


# 语音生成配置
class VoiceConfig:
    """语音生成配置"""
    
    @staticmethod
    def get_voice_styles():
        """获取可用的语音风格"""
        return {
            "dongyu_style": {
                "name": "董宇辉风格",
                "description": "温和亲切，富有感染力，语调起伏自然",
                "icon": "🎭",
                "settings": {
                    "speed": 0.9,
                    "pitch": 0.1,
                    "emotion": "gentle"
                }
            },
            "luozhenyu_style": {
                "name": "罗振宇风格", 
                "description": "激昂有力，节奏明快，逻辑清晰",
                "icon": "⚡",
                "settings": {
                    "speed": 1.1,
                    "pitch": 0.2,
                    "emotion": "energetic"
                }
            },
            "professional_style": {
                "name": "专业播音",
                "description": "标准普通话，清晰准确，适合正式场合",
                "icon": "🎙️",
                "settings": {
                    "speed": 1.0,
                    "pitch": 0.0,
                    "emotion": "neutral"
                }
            }
        }


# 视频生成配置
class VideoConfig:
    """视频生成配置"""
    
    @staticmethod
    def get_video_styles():
        """获取可用的视频风格"""
        return {
            "classic_ppt": {
                "name": "经典PPT风格",
                "description": "简洁大方，适合商务和教育场景",
                "icon": "📊",
                "settings": {
                    "theme": "classic",
                    "animation": "fade",
                    "duration_per_slide": 10
                }
            },
            "modern_presentation": {
                "name": "现代演示风格",
                "description": "时尚动感，视觉冲击力强",
                "icon": "✨",
                "settings": {
                    "theme": "modern",
                    "animation": "slide",
                    "duration_per_slide": 8
                }
            },
            "storytelling": {
                "name": "故事叙述风格",
                "description": "温馨感人，适合情感类内容",
                "icon": "📖",
                "settings": {
                    "theme": "storytelling",
                    "animation": "zoom",
                    "duration_per_slide": 12
                }
            },
            "side_nav_panel": {
                "name": "专业导航面板",
                "description": "带侧边导航控制面板，适合专业演示场景",
                "icon": "🎛️",
                "settings": {
                    "theme": "professional",
                    "animation": "slide",
                    "duration_per_slide": 10
                }
            }
        }


if __name__ == "__main__":
    # 测试代码
    config = MethodologyConfig()
    
    # 测试获取所有方法论
    print("所有方法论：")
    for methodology in config.get_all_methodologies():
        print(f"- {methodology['name']}: {methodology['description']}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试根据分类推荐方法论
    test_categories = ["文学类", "管理", "科幻", "传记"]
    for category in test_categories:
        suitable = config.get_suitable_methodologies(category)
        print(f"分类 '{category}' 适合的方法论：")
        for methodology in suitable:
            print(f"- {methodology['name']}")
        print()
