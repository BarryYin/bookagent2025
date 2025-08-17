"""
用户画像数据聚合器
整合用户的所有行为数据，生成完整的阅读画像
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class UserReadingProfile:
    """用户阅读画像"""
    user_id: int
    
    # 基础信息
    total_books_generated: int  # 生成PPT的书籍数量
    total_books_viewed: int     # 浏览过的书籍数量
    reading_period_days: int    # 阅读周期（从第一次活动到现在的天数）
    
    # 分类偏好
    preferred_categories: Dict[str, int]  # 分类名称 -> 书籍数量
    category_diversity: float  # 分类多样性 (0-1)
    
    # 阅读行为
    generation_frequency: str  # 生成频率: "高频", "中频", "低频"
    recent_activity: bool      # 最近是否活跃 (30天内)
    peak_activity_pattern: str # 活跃时间模式
    
    # 内容深度
    detailed_content_books: List[Dict]  # 有详细内容的书籍
    interview_books: List[Dict]         # 参与访谈的书籍
    reflection_depth: str               # 思考深度: "深度", "中等", "浅层"
    
    # 推荐基础数据
    excluded_books: List[str]           # 已生成PPT的书籍，应排除推荐
    recommendation_preferences: Dict    # 推荐偏好参数

class UserProfileAggregator:
    """用户画像数据聚合器"""
    
    def __init__(self, db_path: str = "fogsight.db"):
        self.db_path = db_path
    
    def get_comprehensive_user_profile(self, user_id: int) -> UserReadingProfile:
        """获取用户的完整阅读画像"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 1. 获取PPT生成历史
            ppt_data = self._get_ppt_generation_data(cursor, user_id)
            
            # 2. 获取浏览历史
            view_data = self._get_viewing_data(cursor, user_id)
            
            # 3. 获取访谈数据
            interview_data = self._get_interview_data(cursor, user_id)
            
            # 4. 获取阅读历史
            reading_data = self._get_reading_history_data(cursor, user_id)
            
            conn.close()
            
            # 整合数据生成画像
            profile = self._build_user_profile(user_id, ppt_data, view_data, interview_data, reading_data)
            
            return profile
            
        except Exception as e:
            print(f"获取用户画像失败: {e}")
            return self._get_default_profile(user_id)
    
    def _get_ppt_generation_data(self, cursor, user_id: int) -> Dict:
        """获取PPT生成数据"""
        cursor.execute("""
            SELECT 
                session_id,
                title,
                author,
                category_name,
                created_at,
                view_count
            FROM ppts 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        """, (user_id,))
        
        ppts = []
        for row in cursor.fetchall():
            ppts.append({
                'session_id': row[0],
                'title': row[1],
                'author': row[2],
                'category': row[3],
                'created_at': row[4],
                'view_count': row[5],
                'has_content': True  # 假设所有PPT都有内容
            })
        
        return {
            'ppts': ppts,
            'total_count': len(ppts),
            'categories': self._analyze_categories([p['category'] for p in ppts]),
            'recent_activity': self._analyze_recent_activity([p['created_at'] for p in ppts])
        }
    
    def _get_viewing_data(self, cursor, user_id: int) -> Dict:
        """获取浏览数据（基于view_count>0的PPT）"""
        cursor.execute("""
            SELECT DISTINCT title, author, category_name, view_count
            FROM ppts 
            WHERE view_count > 0
            AND user_id != ?  -- 浏览其他人的PPT
        """, (user_id,))
        
        viewed_books = []
        for row in cursor.fetchall():
            viewed_books.append({
                'title': row[0],
                'author': row[1],
                'category': row[2],
                'view_count': row[3]
            })
        
        return {
            'viewed_books': viewed_books,
            'total_viewed': len(viewed_books),
            'viewed_categories': self._analyze_categories([b['category'] for b in viewed_books])
        }
    
    def _get_interview_data(self, cursor, user_id: int) -> Dict:
        """获取访谈数据"""
        # TODO: 这里需要根据访谈数据表的实际结构来实现
        # 现在先返回空数据
        return {
            'interviewed_books': [],
            'total_interviews': 0,
            'reflection_depth': 'unknown'
        }
    
    def _get_reading_history_data(self, cursor, user_id: int) -> Dict:
        """获取阅读历史数据"""
        cursor.execute("""
            SELECT book_title, author, completion_date, rating, notes
            FROM reading_history 
            WHERE user_id = ?
            ORDER BY completion_date DESC
        """, (user_id,))
        
        reading_history = []
        for row in cursor.fetchall():
            reading_history.append({
                'title': row[0],
                'author': row[1],
                'completion_date': row[2],
                'rating': row[3],
                'notes': row[4]
            })
        
        return {
            'reading_history': reading_history,
            'total_read': len(reading_history)
        }
    
    def _analyze_categories(self, categories: List[str]) -> Dict[str, int]:
        """分析分类偏好"""
        category_count = defaultdict(int)
        for category in categories:
            if category:  # 确保分类不为空
                category_count[category] += 1
        return dict(category_count)
    
    def _analyze_recent_activity(self, timestamps: List[str]) -> Dict:
        """分析最近活动情况"""
        if not timestamps:
            return {'is_recent': False, 'days_since_last': 999}
        
        # 转换时间戳并找出最近的活动
        recent_dates = []
        for ts in timestamps:
            try:
                # 假设时间戳格式为 YYYY-MM-DD HH:MM:SS
                dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                recent_dates.append(dt)
            except:
                continue
        
        if not recent_dates:
            return {'is_recent': False, 'days_since_last': 999}
        
        latest_date = max(recent_dates)
        days_since = (datetime.now() - latest_date).days
        
        return {
            'is_recent': days_since <= 30,
            'days_since_last': days_since
        }
    
    def _build_user_profile(self, user_id: int, ppt_data: Dict, view_data: Dict, 
                           interview_data: Dict, reading_data: Dict) -> UserReadingProfile:
        """构建用户画像"""
        
        # 合并所有分类数据
        all_categories = defaultdict(int)
        all_categories.update(ppt_data['categories'])
        for cat, count in view_data['viewed_categories'].items():
            all_categories[cat] += count
        
        # 计算分类多样性
        total_books = sum(all_categories.values())
        diversity = len(all_categories) / max(total_books, 1) if total_books > 0 else 0
        
        # 确定生成频率
        total_ppts = ppt_data['total_count']
        if total_ppts >= 10:
            frequency = "高频"
        elif total_ppts >= 3:
            frequency = "中频"
        else:
            frequency = "低频"
        
        # 构建排除列表（已生成PPT的书籍）
        excluded_books = [ppt['title'] for ppt in ppt_data['ppts']]
        
        # 计算阅读周期
        if ppt_data['ppts']:
            first_ppt_date = min([datetime.strptime(p['created_at'], "%Y-%m-%d %H:%M:%S") 
                                for p in ppt_data['ppts']])
            reading_period = (datetime.now() - first_ppt_date).days
        else:
            reading_period = 0
        
        return UserReadingProfile(
            user_id=user_id,
            total_books_generated=total_ppts,
            total_books_viewed=view_data['total_viewed'],
            reading_period_days=reading_period,
            preferred_categories=dict(all_categories),
            category_diversity=diversity,
            generation_frequency=frequency,
            recent_activity=ppt_data['recent_activity']['is_recent'],
            peak_activity_pattern="未知",  # 需要更多数据分析
            detailed_content_books=[p for p in ppt_data['ppts'] if p['has_content']],
            interview_books=interview_data['interviewed_books'],
            reflection_depth=interview_data['reflection_depth'],
            excluded_books=excluded_books,
            recommendation_preferences={
                'diversity_weight': min(diversity * 2, 1.0),  # 多样性权重
                'category_focus': max(all_categories, key=all_categories.get) if all_categories else None,
                'avoid_repetition': True
            }
        )
    
    def _get_default_profile(self, user_id: int) -> UserReadingProfile:
        """获取默认用户画像（新用户或数据获取失败时使用）"""
        return UserReadingProfile(
            user_id=user_id,
            total_books_generated=0,
            total_books_viewed=0,
            reading_period_days=0,
            preferred_categories={},
            category_diversity=0.0,
            generation_frequency="低频",
            recent_activity=False,
            peak_activity_pattern="未知",
            detailed_content_books=[],
            interview_books=[],
            reflection_depth="未知",
            excluded_books=[],
            recommendation_preferences={
                'diversity_weight': 0.8,  # 新用户偏向多样性
                'category_focus': None,
                'avoid_repetition': False
            }
        )
    
    def get_recommendation_context(self, user_id: int) -> Dict[str, Any]:
        """获取用于推荐的上下文信息"""
        profile = self.get_comprehensive_user_profile(user_id)
        
        return {
            'user_profile': {
                'reading_level': profile.generation_frequency,
                'preferred_categories': profile.preferred_categories,
                'diversity_preference': profile.category_diversity,
                'recent_activity': profile.recent_activity,
                'excluded_books': profile.excluded_books
            },
            'recommendation_strategy': {
                'should_diversify': profile.category_diversity < 0.3,  # 分类单一时建议多样化
                'focus_category': max(profile.preferred_categories, key=profile.preferred_categories.get) 
                                if profile.preferred_categories else None,
                'novelty_weight': 0.7 if profile.recent_activity else 0.4,  # 活跃用户更喜欢新内容
                'depth_preference': 'detailed' if len(profile.detailed_content_books) > 3 else 'overview'
            },
            'personalization_context': {
                'total_engagement': profile.total_books_generated + profile.total_books_viewed,
                'reading_maturity': min(profile.reading_period_days / 365, 2.0),  # 阅读成熟度（最高2年）
                'content_depth': len(profile.detailed_content_books) / max(profile.total_books_generated, 1)
            }
        }
