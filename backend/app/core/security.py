"""
JWT 令牌工具 + Argon2 密码哈希。
"""

from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHashError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

# Argon2 默认配置（memory=65536KB, iterations=3, parallelism=4）
_ph = PasswordHasher()

# HTTPBearer 安全方案（auto_error=False 以便手动控制 401 响应）
_bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """对明文密码进行 Argon2 哈希，返回哈希字符串。"""
    return _ph.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """验证明文密码是否匹配 Argon2 哈希。"""
    try:
        _ph.verify(password_hash, password)
        if _ph.check_needs_rehash(password_hash):
            pass
        return True
    except (VerificationError, InvalidHashError):
        return False


def create_access_token(user_id: int, username: str, expire_minutes: int | None = None) -> str:
    """生成 JWT access token，可指定过期时间（分钟）。"""
    minutes = expire_minutes if expire_minutes is not None else settings.JWT_EXPIRE_MINUTES
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """从请求头 Bearer token 解析当前登录用户（FastAPI 依赖注入）。"""
    if credentials is None:
        raise HTTPException(status_code=401, detail="请先登录")
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="无效的认证令牌")
    except JWTError:
        raise HTTPException(status_code=401, detail="无效的认证令牌")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user
