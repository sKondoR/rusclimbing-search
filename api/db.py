from core.config import settings
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import text

# Database configuration
DATABASE_URL = settings.DATABASE_URL
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Convert for asyncpg
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Remove sslmode parameter as asyncpg doesn't support it
if "?sslmode=require" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("?sslmode=require", "")
elif "&sslmode=require" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("&sslmode=require", "")

# Ensure asyncpg is properly configured
if "asyncpg" not in DATABASE_URL:
    print("Warning: DATABASE_URL does not explicitly specify asyncpg driver, but this may be acceptable")

# Create engine
engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def startup_event():
    # Create tables if they don't exist - using async properly
    async with engine.connect() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS events (
                id SERIAL PRIMARY KEY,
                date VARCHAR(255),
                link VARCHAR(255) UNIQUE,
                name VARCHAR(255),
                location VARCHAR(255),
                type VARCHAR(255),
                groups TEXT[],
                disciplines TEXT[],
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        await conn.commit()

        