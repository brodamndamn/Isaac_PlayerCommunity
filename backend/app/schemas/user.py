from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """注册请求体"""

    username: str = Field(min_length=1, max_length=50, description="用户名")
    email: EmailStr = Field(max_length=100, description="邮箱")
    password: str = Field(min_length=6, max_length=128, description="密码（最少 6 位）")


class UserLogin(BaseModel):
    """登录请求体（用户名或邮箱 + 密码）"""

    login: str = Field(min_length=1, max_length=100, description="用户名或邮箱")
    password: str = Field(min_length=1, max_length=128, description="密码")
    remember_me: bool = False


class UserResponse(BaseModel):
    """用户信息响应（不含密码哈希）"""

    id: int
    username: str
    email: str
    role: str
    avatar: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
