"""
创建默认用户脚本
"""

import sys
import os
sys.path.append(os.getcwd())

from models import user_manager

def create_default_user():
    """创建默认用户"""
    print("🔧 正在创建默认用户...")
    
    # 默认用户信息
    username = "admin"
    email = "admin@fogsight.com"
    password = "123456"  # 简单密码，生产环境应该使用强密码
    
    try:
        # 创建用户
        user = user_manager.create_user(username, email, password)
        
        if user:
            print(f"✅ 默认用户创建成功!")
            print(f"   用户名: {username}")
            print(f"   邮箱: {email}")
            print(f"   密码: {password}")
            print(f"   用户ID: {user.id}")
            
            # 再创建一个测试用户
            test_user = user_manager.create_user("test", "test@fogsight.com", "123456")
            if test_user:
                print(f"✅ 测试用户也创建成功!")
                print(f"   用户名: test")
                print(f"   密码: 123456")
        else:
            print("❌ 用户创建失败，可能用户名或邮箱已存在")
            
    except Exception as e:
        print(f"❌ 创建用户时出错: {e}")

if __name__ == "__main__":
    create_default_user()
