from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api import characters, endings, items, transformations
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


# 统一异常处理 — 将所有错误转为约定的 {code, message, data} 格式
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
            "data": None,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "服务器内部错误", "data": None},
    )


app.include_router(characters.router)
app.include_router(endings.router)
app.include_router(items.router)
app.include_router(transformations.router)


@app.get("/api/v1/health")
def health_check():
    return {"code": 200, "message": "ok", "data": None}
