"""
测试增强版推荐系统
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.getcwd())

from enhanced_recommendation_engine import EnhancedRecommendationEngine
from user_profile_aggregator import UserProfileAggregator
from guided_recommendation_agent import GuidedRecommendationAgent

async def test_enhanced_recommendation_system():
    """测试增强版推荐系统"""
    
    print("🔍 测试增强版推荐系统...")
    print("=" * 50)
    
    # 测试用户ID（假设数据库中存在的用户）
    test_user_id = 1
    
    try:
        # 1. 测试用户画像聚合器
        print("\n1. 测试用户画像聚合器")
        print("-" * 30)
        
        aggregator = UserProfileAggregator()
        profile = aggregator.get_comprehensive_user_profile(test_user_id)
        
        print(f"用户 {test_user_id} 的画像:")
        print(f"  - 生成书籍数量: {profile.total_books_generated}")
        print(f"  - 浏览书籍数量: {profile.total_books_viewed}")
        print(f"  - 阅读频率: {profile.generation_frequency}")
        print(f"  - 分类偏好: {profile.preferred_categories}")
        print(f"  - 分类多样性: {profile.category_diversity:.2f}")
        print(f"  - 最近活跃: {profile.recent_activity}")
        print(f"  - 排除书籍数量: {len(profile.excluded_books)}")
        
        # 2. 测试增强版推荐引擎
        print("\n2. 测试增强版推荐引擎")
        print("-" * 30)
        
        engine = EnhancedRecommendationEngine()
        enhanced_data = engine.get_enhanced_recommendations(test_user_id, 5)
        
        print(f"推荐策略: {enhanced_data['recommendation_metadata']['strategy_used']}")
        print(f"置信度: {enhanced_data['recommendation_metadata']['confidence_score']}")
        print(f"推荐书籍数量: {len(enhanced_data['recommendations'])}")
        
        print("\n推荐书籍:")
        for i, (book, explanation) in enumerate(zip(enhanced_data['recommendations'], enhanced_data['explanations'])):
            print(f"  {i+1}. 《{book['title']}》- {book['author']}")
            print(f"     分类: {book['category_name']}")
            print(f"     推荐理由: {explanation}")
            print()
        
        # 3. 测试推荐上下文生成
        print("\n3. 测试推荐上下文生成")
        print("-" * 30)
        
        context = engine.get_recommendation_prompt_context(test_user_id)
        print("生成的上下文:")
        print(context)
        
        # 4. 测试增强版智能体
        print("\n4. 测试增强版智能体")
        print("-" * 30)
        
        agent = GuidedRecommendationAgent()
        
        # 启动会话
        session_result = await agent.start_recommendation_session(test_user_id)
        print("智能体开场白:")
        print(session_result['message'])
        
        if 'recommendations' in session_result:
            print(f"\n智能体推荐的书籍数量: {len(session_result['recommendations'])}")
            for rec in session_result['recommendations']:
                print(f"  - 《{rec['title']}》: {rec['reason']}")
        
        # 模拟对话
        print("\n5. 模拟对话测试")
        print("-" * 30)
        
        test_messages = [
            "我想要一些心理学的书籍推荐",
            "我最近比较忙，有什么轻松一点的推荐吗？",
            "能详细介绍一下第一本书吗？"
        ]
        
        for msg in test_messages:
            print(f"\n用户: {msg}")
            response = await agent.continue_conversation(test_user_id, msg)
            print(f"智能体: {response['message']}")
        
        print("\n✅ 增强版推荐系统测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

async def test_api_integration():
    """测试API集成"""
    print("\n🔌 测试API集成...")
    print("=" * 50)
    
    try:
        # 模拟API调用
        from enhanced_recommendation_engine import EnhancedRecommendationEngine
        
        engine = EnhancedRecommendationEngine()
        
        # 测试API数据格式
        enhanced_data = engine.get_enhanced_recommendations(1, 3)
        
        print("API返回数据结构:")
        print(f"- recommendations: {len(enhanced_data['recommendations'])} 本书")
        print(f"- explanations: {len(enhanced_data['explanations'])} 个解释")
        print(f"- user_context: {list(enhanced_data['user_context'].keys())}")
        print(f"- recommendation_metadata: {list(enhanced_data['recommendation_metadata'].keys())}")
        
        print("\n✅ API集成测试完成！")
        
    except Exception as e:
        print(f"❌ API集成测试失败: {e}")

if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_enhanced_recommendation_system())
    asyncio.run(test_api_integration())
