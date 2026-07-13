"""
JWT 令牌工具 + Argon2 密码哈希。

功能将在阶段三（用户系统）逐步实现：
- create_access_token() — 生成 JWT
- verify_password() / hash_password() — Argon2 校验与哈希
- get_current_user() — FastAPI 依赖注入，从请求头解析当前用户
"""

from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import settings


def create_access_token(user_id: int, username: str) -> str:
    """生成 JWT access token。"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
