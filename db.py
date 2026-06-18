from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, BigInteger, select
import os


DATABASE_URL = "postgresql+asyncpg://postgres:58946@localhost:5432/postgres"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    user_id = Column(BigInteger, primary_key=True)

class Database:
    async def user_exists(self, user_id: int) -> bool:
        async with async_session_maker() as session:
            result = await session.execute(
                select(User).where(User.user_id == user_id)
            )
            return result.scalar_one_or_none() is not None

    async def add_user(self, user_id: int):
        async with async_session_maker() as session:
            session.add(User(user_id=user_id))
            await session.commit()

    async def create_tables(self):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)