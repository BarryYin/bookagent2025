"""
环境变量配置管理模块
统一管理所有 API Key 和敏感配置
"""
import os
from typing import Optional
from pathlib import Path

# 尝试加载 .env 文件
try:
    from dotenv import load_dotenv
    # 加载 .env 文件
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print("✅ 成功加载 .env 配置文件")
    else:
        print("⚠️ .env 文件不存在，将使用环境变量或默认配置")
except ImportError:
    print("⚠️ python-dotenv 未安装，请运行: pip install python-dotenv")


class Config:
    """配置类 - 统一管理所有配置项"""
    
    # ===== AI 模型配置 =====
    
    # Gemini
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # OpenAI / OpenRouter
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # 百度 ERNIE
    BAIDU_API_KEY: str = os.getenv("BAIDU_API_KEY", "")
    BAIDU_BASE_URL: str = os.getenv("BAIDU_BASE_URL", "https://qianfan.baidubce.com/v2")
    BAIDU_MODEL: str = os.getenv("BAIDU_MODEL", "ernie-4.5-turbo-32k")
    
    # Qwen
    QWEN_API_KEY: str = os.getenv("QWEN_API_KEY", "")
    QWEN_BASE_URL: str = os.getenv("QWEN_BASE_URL", "https://api-inference.modelscope.cn/v1/")
    QWEN_MODEL: str = os.getenv("QWEN_MODEL", "Qwen/Qwen3-Coder-480B-A35B-Instruct")
    
    # ===== 语音服务配置 =====
    
    # 讯飞语音
    XUNFEI_APP_ID: str = os.getenv("XUNFEI_APP_ID", "")
    XUNFEI_API_KEY: str = os.getenv("XUNFEI_API_KEY", "")
    XUNFEI_API_SECRET: str = os.getenv("XUNFEI_API_SECRET", "")
    
    # 星火大模型
    SPARKAI_APP_ID: str = os.getenv("SPARKAI_APP_ID", "")
    SPARKAI_API_KEY: str = os.getenv("SPARKAI_API_KEY", "")
    SPARKAI_API_SECRET: str = os.getenv("SPARKAI_API_SECRET", "")
    
    # Fish Audio
    FISH_API_KEY: str = os.getenv("FISH_API_KEY", "")
    FISH_REFERENCE_ID: str = os.getenv("FISH_REFERENCE_ID", "")
    
    # ===== 认证配置 =====
    
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    
    # ===== OCR 配置 =====
    
    BAIDU_OCR_API_KEY: str = os.getenv("BAIDU_OCR_API_KEY", "")
    BAIDU_OCR_SECRET_KEY: str = os.getenv("BAIDU_OCR_SECRET_KEY", "")
    
    # ===== 应用配置 =====
    
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # ===== 兼容旧的 credentials.json =====
    
    @classmethod
    def load_from_credentials_json(cls) -> dict:
        """
        从 credentials.json 加载配置（向后兼容）
        如果环境变量未设置，尝试从 credentials.json 读取
        """
        try:
            import json
            cred_path = Path(__file__).parent / "credentials.json"
            if cred_path.exists():
                with open(cred_path, 'r', encoding='utf-8') as f:
                    creds = json.load(f)
                    print("✅ 从 credentials.json 加载配置")
                    return creds
        except Exception as e:
            print(f"⚠️ 无法加载 credentials.json: {e}")
        return {}
    
    @classmethod
    def get_api_key(cls) -> str:
        """
        获取主要的 API Key（优先级：环境变量 > credentials.json）
        """
        # 优先使用环境变量
        if cls.OPENAI_API_KEY:
            return cls.OPENAI_API_KEY
        if cls.GEMINI_API_KEY:
            return cls.GEMINI_API_KEY
        if cls.BAIDU_API_KEY:
            return cls.BAIDU_API_KEY
        if cls.QWEN_API_KEY:
            return cls.QWEN_API_KEY
        
        # 回退到 credentials.json
        creds = cls.load_from_credentials_json()
        return creds.get("API_KEY", "")
    
    @classmethod
    def get_base_url(cls) -> str:
        """获取 API Base URL"""
        if cls.OPENAI_API_KEY:
            return cls.OPENAI_BASE_URL
        if cls.BAIDU_API_KEY:
            return cls.BAIDU_BASE_URL
        if cls.QWEN_API_KEY:
            return cls.QWEN_BASE_URL
        
        # 回退到 credentials.json
        creds = cls.load_from_credentials_json()
        return creds.get("BASE_URL", "")
    
    @classmethod
    def get_model(cls) -> str:
        """获取模型名称"""
        if cls.OPENAI_API_KEY:
            return cls.OPENAI_MODEL
        if cls.BAIDU_API_KEY:
            return cls.BAIDU_MODEL
        if cls.QWEN_API_KEY:
            return cls.QWEN_MODEL
        
        # 回退到 credentials.json
        creds = cls.load_from_credentials_json()
        return creds.get("MODEL", "gemini-2.5-pro")
    
    @classmethod
    def validate(cls) -> bool:
        """验证必要的配置是否存在"""
        api_key = cls.get_api_key()
        if not api_key or api_key.startswith("sk-REPLACE_ME"):
            print("❌ 错误：未配置有效的 API Key")
            print("请在 .env 文件中配置或设置环境变量")
            return False
        return True


# 创建全局配置实例
config = Config()

# 导出常用配置
API_KEY = config.get_api_key()
BASE_URL = config.get_base_url()
MODEL = config.get_model()

# 验证配置
if not config.validate():
    print("\n" + "="*60)
    print("配置错误：请按以下步骤配置 API Key：")
    print("1. 复制 .env.example 为 .env")
    print("2. 在 .env 文件中填入你的 API Key")
    print("3. 或者设置环境变量")
    print("="*60 + "\n")
