from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import get_settings

settings = get_settings()

DATABASE_URL = settings.supabase_db_url.replace(
    "postgresql://", "postgresql+psycopg://"
)
engine = create_async_engine(DATABASE_URL,
                             echo=True,
                             pool_pre_ping=True,)
AsyncSessionLocal = async_sessionmaker(bind=engine,class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass
async def get_db()-> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Create all tables on startup."""
    async with engine.begin() as conn:
        from app.models import db_models  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)