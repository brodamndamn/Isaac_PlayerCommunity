import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, get_current_user, hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads" / "avatars"
ALLOWED_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp", "image/bmp"}

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register")
def register(body: UserCreate, db: Session = Depends(get_db)):
    """用户注册。用户名和邮箱必须唯一。"""
    # 检查用户名或邮箱是否已被占用
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=409, detail="用户名已被注册")
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=409, detail="邮箱已被注册")

    user = User(
        username=body.username,
        email=body.email,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "code": 201,
        "message": "注册成功",
        "data": UserResponse.model_validate(user).model_dump(),
    }


@router.post("/login")
def login(body: UserLogin, db: Session = Depends(get_db)):
    """用户登录。支持用户名或邮箱 + 密码，返回 JWT token。"""
    # 支持用户名或邮箱登录
    user = (
        db.query(User)
        .filter(or_(User.username == body.login, User.email == body.login))
        .first()
    )
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_access_token(user.id, user.username)
    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "token": token,
            "user": UserResponse.model_validate(user).model_dump(),
        },
    }


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息（需 JWT）。"""
    return {
        "code": 200,
        "message": "ok",
        "data": UserResponse.model_validate(current_user).model_dump(),
    }


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """上传头像（需登录）。支持 PNG / JPEG / GIF / WebP。"""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="仅支持 PNG、JPEG、GIF、WebP 格式")

    # 生成唯一文件名
    ext = os.path.splitext(file.filename or ".png")[1] or ".png"
    filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}{ext}"
    filepath = UPLOAD_DIR / filename

    # 确保目录存在
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # 写入文件
    content = await file.read()
    if len(content) > 2 * 1024 * 1024:  # 2MB 限制
        raise HTTPException(status_code=400, detail="图片大小不能超过 2MB")

    with open(filepath, "wb") as f:
        f.write(content)

    # 更新用户头像
    avatar_path = f"avatars/{filename}"
    current_user.avatar = avatar_path
    db.commit()

    return {
        "code": 200,
        "message": "上传成功",
        "data": {"avatar": avatar_path},
    }
