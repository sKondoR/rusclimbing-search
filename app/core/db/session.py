from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.database import AsyncSessionLocal


async def get_session() -> AsyncSession:
    """
    Dependency function for database sessions.

    Provides async database session for FastAPI endpoints.
    Automatically handles session lifecycle.

    Yields:
        AsyncSession: Database session

    Example:
        @router.get("/events")
        async def get_events(session: AsyncSession = Depends(get_session)):
            ...
    """
    async with AsyncSessionLocal() as session:
        yield session
