"""
认证中间件 - 用于引导推荐智能体的身份验证
"""

from fastapi import HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import jwt
from models import User, user_manager, verify_token, SECRET_KEY, ALGORITHM

# HTTP Bearer token 安全方案
security = HTTPBearer(auto_error=False)

class AuthenticationError(Exception):
    """认证相关错误"""
    pass

def get_user_from_token(token: str) -> Optional[User]:
    """从JWT token获取用户信息"""
    try:
        username = verify_token(token)
        if username:
            return user_manager.get_user_by_username(username)
        return None
    except Exception as e:
        print(f"Token验证错误: {e}")
        return None

def get_user_from_session(session_token: str) -> Optional[User]:
    """从session token获取用户信息"""
    try:
        return user_manager.get_user_by_session(session_token)
    except Exception as e:
        print(f"Session验证错误: {e}")
        return None

def get_current_user_from_request(request: Request) -> Optional[User]:
    """从请求中获取当前用户（与现有系统兼容）"""
    # 1. 优先从Cookie获取session token（与现有系统保持一致）
    session_token = request.cookies.get("session_token")
    if session_token:
        user = get_user_from_session(session_token)
        if user:
            return user
    
    # 2. 尝试从Authorization header获取JWT token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        user = get_user_from_token(token)
        if user:
            return user
    
    # 3. 尝试从查询参数获取token（用于某些特殊情况）
    token = request.query_params.get("token")
    if token:
        user = get_user_from_token(token)
        if user:
            return user
    
    return None

async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> User:
    """获取当前认证用户（必需认证）"""
    user = None
    
    # 1. 尝试从Bearer token获取用户
    if credentials:
        user = get_user_from_token(credentials.credentials)
    
    # 2. 如果Bearer token失败，尝试其他方式
    if not user:
        user = get_current_user_from_request(request)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未认证或认证已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def get_current_user_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """获取当前用户（可选认证）"""
    try:
        return await get_current_user(request, credentials)
    except HTTPException:
        return None

def require_authentication(func):
    """装饰器：要求认证"""
    async def wrapper(*args, **kwargs):
        # 检查参数中是否有user参数
        if 'user' not in kwargs:
            raise AuthenticationError("需要用户认证")
        
        user = kwargs['user']
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="需要用户认证"
            )
        
        return await func(*args, **kwargs)
    return wrapper

def get_user_id_from_request(request: Request) -> Optional[int]:
    """从请求中获取用户ID"""
    user = get_current_user_from_request(request)
    return user.id if user else None

class AuthContext:
    """认证上下文"""
    def __init__(self, user: Optional[User] = None):
        self.user = user
        self.is_authenticated = user is not None
        self.user_id = user.id if user else None
        self.username = user.username if user else None

def create_auth_context(request: Request) -> AuthContext:
    """创建认证上下文"""
    user = get_current_user_from_request(request)
    return AuthContext(user)

# 用于API响应的认证状态检查
def check_auth_status(request: Request) -> dict:
    """检查认证状态"""
    user = get_current_user_from_request(request)
    
    if user:
        return {
            "authenticated": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }
    else:
        return {
            "authenticated": False,
            "user": None
        }

# 错误处理
def handle_auth_error(error: Exception) -> HTTPException:
    """处理认证错误"""
    if isinstance(error, AuthenticationError):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error)
        )
    elif isinstance(error, jwt.ExpiredSignatureError):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证已过期，请重新登录"
        )
    elif isinstance(error, jwt.InvalidTokenError):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证信息"
        )
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="认证服务错误"
        )