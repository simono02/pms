# backend/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from config import settings

# =====================================================
# Base (shared by async + sync)
# =====================================================
class Base(DeclarativeBase):
    pass


# =====================================================
# ASYNC DATABASE SETUP (FastAPI async routes)
# =====================================================
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    poolclass=NullPool
)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Create async_session as an alias for middleware compatibility
async_session = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_async_db():
    """
    Async database dependency (FastAPI async routes)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# =====================================================
# SYNC DATABASE SETUP (Alembic, background jobs, scripts)
# =====================================================
SYNC_DATABASE_URL = settings.DATABASE_URL.replace(
    "postgresql+asyncpg://",
    "postgresql+psycopg2://"
)

sync_engine = create_engine(
    SYNC_DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)


def get_db():
    """
    Sync database dependency
    (Alembic, Celery, scripts, GraphQL resolvers, etc.)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =====================================================
# Backward compatibility aliases
# =====================================================
engine = sync_engine  # Default to sync engine for legacy code


# =====================================================
# Exports
# =====================================================
__all__ = [
    "Base",
    "async_engine",
    "sync_engine",
    "engine",
    "AsyncSessionLocal",
    "async_session",
    "SessionLocal",
    "get_async_db",
    "get_db",
]