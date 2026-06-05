# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings  # 引入設定檔

# 應用程式使用非同步驅動 aiomysql

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False, # 開發階段若想看生成的 SQL 可以設為 True
    pool_size=20,
    max_overflow=10
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

# FastAPI 依賴注入使用
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
