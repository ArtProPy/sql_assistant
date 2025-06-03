"""Общие параметры подключения к бд."""

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DB_NAME = 'course_test'
DB_HOST = '127.0.0.1'
DB_USER = 'postgres'
DB_PASSWORD = '1234'

Base = declarative_base()

DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'

engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
Base.metadata.bind = engine
