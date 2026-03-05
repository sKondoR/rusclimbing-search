from sqlalchemy import ARRAY, Column, DateTime, Integer, String, text
from app.models import Base


class TeamCache(Base):
    """
    Database model for caching team data.

    Stores parsed team names for each competition year to avoid repeated parsing.

    Attributes:
        id: Primary key
        year: Competition year (key for cache)
        teams: Array of unique team names sorted alphabetically
        created_at: Timestamp of record creation
        updated_at: Timestamp of last record update
    """
    __tablename__ = "team_cache"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(String, unique=True, index=True)
    teams = Column(ARRAY(String))
    created_at = Column(DateTime, server_default=text("now()"))
    updated_at = Column(DateTime, server_default=text("now()"), onupdate=text("now()"))
