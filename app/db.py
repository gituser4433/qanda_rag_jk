from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import Config

DATABASE_URL = Config.DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

# Proper async session dependency
async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session