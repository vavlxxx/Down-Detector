from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings

engine = create_async_engine(
    url=settings.db.DB_URL,
    echo=settings.db.DB_ECHO,
)

sessionmaker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=settings.db.DB_AUTOCOMMIT,
    autoflush=settings.db.DB_AUTOFLUSH,
    expire_on_commit=settings.db.DB_EXPIRE_ON_COMMIT,
)

engine_null_pool = create_async_engine(
    url=settings.db.DB_URL,
    poolclass=NullPool,
)

sessionmaker_null_pool = async_sessionmaker(
    bind=engine_null_pool,
    autocommit=settings.db.DB_AUTOCOMMIT,
    autoflush=settings.db.DB_AUTOFLUSH,
    expire_on_commit=settings.db.DB_EXPIRE_ON_COMMIT,
)
