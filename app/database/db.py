from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://pguser:pgpassword@127.0.0.1/mycaly"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
sync_engine = create_engine(SQLALCHEMY_DATABASE_URL)

AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)

# Base class for models
Base = declarative_base()

# # Dependency for async DB session
# async def get_db():
#     db = None
#     try:
#         db = AsyncSessionLocal()
#         yield db
#     finally:
#         await db.close()

    