import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads" / "guides"
ALLOWED_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp", "image/bmp"}

router = APIRouter(prefix="/api/v1", tags=["upload"])


@router.post("/upload")
async def upload_image(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """上传攻略图片（需登录）。返回可直接用于 Markdown 的 URL。"""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="仅支持 PNG、JPEG、GIF、WebP 格式")

    ext = os.path.splitext(file.filename or ".png")[1] or ".png"
    filename = f"{uuid.uuid4().hex[:12]}{ext}"
    filepath = UPLOAD_DIR / filename

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(status_code=400, detail="图片大小不能超过 10MB")

    with open(filepath, "wb") as f:
        f.write(content)

    url = f"/uploads/guides/{filename}"
    return {
        "code": 200,
        "message": "上传成功",
        "data": {"url": url},
    }
