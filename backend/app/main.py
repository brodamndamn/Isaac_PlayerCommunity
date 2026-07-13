from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.database import SessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动/关闭时的生命周期事件。"""
    # 启动时：验证数据库连接
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        print(f"[OK] 数据库连接成功: {settings.DB_NAME}")
    except Exception as e:
        print(f"[FAIL] 数据库连接失败: {e}")
    finally:
        db.close()
    yield
    # 关闭时：清理资源


app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)

# CORS — 开发环境允许前端跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
def health_check():
    return {"code": 200, "message": "ok", "data": None}
