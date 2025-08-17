"""
增强版推荐数据获取器
结合现有推荐系统和用户画像，提供更精准的推荐数据
"""

import sqlite3
import json
from typing import Dict, List, Optional, Any
from user_profile_aggregator import UserProfileAggregator
from models import user_manager
from mock_recommendation_data import get_mock_recommendations_by_preference, get_diversified_mock_recommendations

class EnhancedRecommendationEngine:
    """增强版推荐引擎"""
    
    def __init__(self, db_path: str = "fogsight.db"):
        self.db_path = db_path
        self.profile_aggregator = UserProfileAggregator(db_path)
    
    def get_enhanced_recommendations(self, user_id: int, limit: int = 10) -> Dict[str, Any]:
        """获取增强版推荐数据"""
        try:
            # 1. 获取用户画像
            profile = self.profile_aggregator.get_comprehensive_user_profile(user_id)
            
            # 2. 获取推荐上下文
            context = self.profile_aggregator.get_recommendation_context(user_id)
            
            # 3. 获取基础推荐数据（使用现有的推荐系统）
            base_recommendations = user_manager.get_recommendations_for_user(user_id, limit * 2)  # 获取更多候选
            
            # 4. 如果基础推荐为空，使用模拟数据
            if not base_recommendations:
                print("基础推荐为空，使用模拟推荐数据")
                mock_recommendations = self._get_mock_recommendations(profile, context, limit)
                optimized_recommendations = mock_recommendations
            else:
                # 根据用户画像优化推荐
                optimized_recommendations = self._optimize_recommendations(
                    base_recommendations, context, profile, limit
                )
            
            # 5. 生成推荐解释
            explanations = self._generate_recommendation_explanations(
                optimized_recommendations, profile, context
            )
            
            return {
                'recommendations': optimized_recommendations,
                'explanations': explanations,
                'user_context': {
                    'reading_level': profile.generation_frequency,
                    'primary_interests': list(profile.preferred_categories.keys())[:3],
                    'reading_maturity': context['personalization_context']['reading_maturity'],
                    'needs_diversification': context['recommendation_strategy']['should_diversify']
                },
                'recommendation_metadata': {
                    'total_user_books': profile.total_books_generated,
                    'excluded_count': len(profile.excluded_books),
                    'strategy_used': self._get_strategy_description(context),
                    'confidence_score': self._calculate_confidence_score(profile),
                    'data_source': 'mock' if not base_recommendations else 'database'
                }
            }
            
        except Exception as e:
            print(f"增强推荐获取失败: {e}")
            # 降级到基础推荐
            return self._get_fallback_recommendations(user_id, limit)
    
    def _get_mock_recommendations(self, profile, context: Dict, limit: int) -> List[Dict]:
        """获取模拟推荐数据"""
        strategy = context['recommendation_strategy']
        
        if strategy['should_diversify']:
            # 多样化推荐
            mock_books = get_diversified_mock_recommendations(profile.excluded_books, limit)
        else:
            # 基于偏好推荐
            mock_books = get_mock_recommendations_by_preference(
                profile.preferred_categories, profile.excluded_books, limit
            )
        
        # 转换为标准格式
        recommendations = []
        for book in mock_books:
            recommendations.append({
                'session_id': f"mock_{book['title']}",
                'title': book['title'],
                'author': book['author'],
                'cover_url': book['cover_url'],
                'category_name': book['category_name'],
                'category_color': '#6366f1',  # 默认颜色
                'category_icon': '📚',       # 默认图标
                'created_at': '2024-01-01 00:00:00',
                'popularity_score': book['popularity_score'],
                'description': book['description']
            })
        
        return recommendations
    
    def _optimize_recommendations(self, base_recommendations: List[Dict], 
                                context: Dict, profile, limit: int) -> List[Dict]:
        """根据用户画像优化推荐结果"""
        
        if not base_recommendations:
            return []
        
        # 过滤已读书籍
        filtered_recommendations = [
            book for book in base_recommendations 
            if book['title'] not in profile.excluded_books
        ]
        
        # 根据推荐策略排序
        strategy = context['recommendation_strategy']
        
        if strategy['should_diversify']:
            # 多样化策略：优先推荐不同分类的书籍
            recommendations = self._diversify_recommendations(filtered_recommendations, profile)
        else:
            # 聚焦策略：优先推荐用户偏好分类的书籍
            recommendations = self._focus_recommendations(filtered_recommendations, strategy['focus_category'])
        
        # 添加推荐分数
        for i, book in enumerate(recommendations):
            book['recommendation_score'] = self._calculate_recommendation_score(book, profile, context)
            book['rank'] = i + 1
        
        # 按推荐分数重新排序
        recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
        
        return recommendations[:limit]
    
    def _diversify_recommendations(self, recommendations: List[Dict], profile) -> List[Dict]:
        """多样化推荐策略"""
        diversified = []
        used_categories = set()
        
        # 第一轮：每个分类选一本
        for book in recommendations:
            if book['category_name'] not in used_categories:
                diversified.append(book)
                used_categories.add(book['category_name'])
        
        # 第二轮：填充剩余位置
        for book in recommendations:
            if book not in diversified:
                diversified.append(book)
        
        return diversified
    
    def _focus_recommendations(self, recommendations: List[Dict], focus_category: str) -> List[Dict]:
        """聚焦推荐策略"""
        if not focus_category:
            return recommendations
        
        # 优先推荐聚焦分类的书籍
        focused = [book for book in recommendations if book['category_name'] == focus_category]
        others = [book for book in recommendations if book['category_name'] != focus_category]
        
        return focused + others
    
    def _calculate_recommendation_score(self, book: Dict, profile, context: Dict) -> float:
        """计算推荐分数"""
        score = 0.0
        
        # 基础流行度分数
        if 'popularity_score' in book:
            score += book['popularity_score'] * 0.3
        
        # 分类匹配分数
        category = book['category_name']
        if category in profile.preferred_categories:
            category_weight = profile.preferred_categories[category] / max(profile.total_books_generated, 1)
            score += category_weight * 0.4
        
        # 新颖性分数
        novelty_weight = context['recommendation_strategy']['novelty_weight']
        score += novelty_weight * 0.2
        
        # 多样性调整
        if context['recommendation_strategy']['should_diversify']:
            # 对非主要分类给予加分
            if category not in list(profile.preferred_categories.keys())[:2]:
                score += 0.1
        
        return min(score, 1.0)  # 限制在0-1之间
    
    def _generate_recommendation_explanations(self, recommendations: List[Dict], 
                                            profile, context: Dict) -> List[str]:
        """生成推荐解释"""
        explanations = []
        
        for book in recommendations:
            explanation = self._generate_single_explanation(book, profile, context)
            explanations.append(explanation)
        
        return explanations
    
    def _generate_single_explanation(self, book: Dict, profile, context: Dict) -> str:
        """为单本书生成推荐解释"""
        category = book['category_name']
        title = book['title']
        
        # 基于不同情况生成解释
        if category in profile.preferred_categories:
            if profile.preferred_categories[category] >= 3:
                return f"基于您对{category}类书籍的浓厚兴趣，《{title}》是该领域的优秀作品"
            else:
                return f"您曾关注过{category}类书籍，《{title}》能进一步拓展您在这个领域的认知"
        
        elif context['recommendation_strategy']['should_diversify']:
            return f"为丰富您的阅读体验，推荐{category}类的《{title}》，探索新的知识领域"
        
        elif profile.generation_frequency == "高频":
            return f"作为活跃读者，《{title}》的深度内容适合您的阅读水平"
        
        else:
            return f"《{title}》是{category}类书籍中的经典之作，值得一读"
    
    def _get_strategy_description(self, context: Dict) -> str:
        """获取推荐策略描述"""
        strategy = context['recommendation_strategy']
        
        if strategy['should_diversify']:
            return "多样化探索策略"
        elif strategy['focus_category']:
            return f"深度聚焦策略（{strategy['focus_category']}）"
        else:
            return "平衡推荐策略"
    
    def _calculate_confidence_score(self, profile) -> float:
        """计算推荐置信度"""
        # 基于用户数据量计算置信度
        data_richness = min(profile.total_books_generated / 10, 1.0)  # 10本书达到满分
        diversity_factor = min(profile.category_diversity * 2, 1.0)
        activity_factor = 1.0 if profile.recent_activity else 0.7
        
        confidence = (data_richness * 0.5 + diversity_factor * 0.3 + activity_factor * 0.2)
        return round(confidence, 2)
    
    def _get_fallback_recommendations(self, user_id: int, limit: int) -> Dict[str, Any]:
        """降级推荐（当增强推荐失败时使用）"""
        base_recommendations = user_manager.get_recommendations_for_user(user_id, limit)
        
        return {
            'recommendations': base_recommendations,
            'explanations': ["基于平台热门书籍为您推荐"] * len(base_recommendations),
            'user_context': {
                'reading_level': "未知",
                'primary_interests': [],
                'reading_maturity': 0.0,
                'needs_diversification': True
            },
            'recommendation_metadata': {
                'total_user_books': 0,
                'excluded_count': 0,
                'strategy_used': "默认推荐策略",
                'confidence_score': 0.3
            }
        }
    
    def get_recommendation_prompt_context(self, user_id: int) -> str:
        """为推荐智能体生成上下文提示"""
        try:
            enhanced_data = self.get_enhanced_recommendations(user_id, 5)
            profile_data = enhanced_data['user_context']
            
            context_prompt = f"""
用户阅读画像：
- 阅读活跃度：{profile_data['reading_level']}
- 主要兴趣领域：{', '.join(profile_data['primary_interests']) if profile_data['primary_interests'] else '待发现'}
- 阅读成熟度：{profile_data['reading_maturity']:.1f}/2.0
- 需要多样化：{'是' if profile_data['needs_diversification'] else '否'}

当前推荐书籍：
"""
            
            for i, (book, explanation) in enumerate(zip(enhanced_data['recommendations'], enhanced_data['explanations'])):
                context_prompt += f"{i+1}. 《{book['title']}》- {book['author']} ({book['category_name']})\n   推荐理由：{explanation}\n\n"
            
            context_prompt += f"\n推荐策略：{enhanced_data['recommendation_metadata']['strategy_used']}"
            context_prompt += f"\n置信度：{enhanced_data['recommendation_metadata']['confidence_score']}"
            
            return context_prompt
            
        except Exception as e:
            print(f"生成推荐上下文失败: {e}")
            return "暂无用户阅读数据，将基于通用推荐进行对话。"
