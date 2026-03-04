from sqlalchemy import ARRAY, Column, DateTime, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Event(Base):
    """
    Database model for climbing competition events.

    Represents a single climbing competition with all its details.

    Attributes:
        id: Primary key
        date: Competition date (without year)
        year: Competition year (can be empty string if not found)
        startdate: Date of competition start
        enddate: Date of competition end
        link: Unique URL link to competition details
        name: Competition name
        location: Competition location
        type: Competition type
        groups: List of participant groups
        disciplines: List of competition disciplines
        created_at: Timestamp of record creation
        updated_at: Timestamp of last record update
    """
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)
    year = Column(String, nullable=True)
    startdate = Column(String)
    enddate = Column(String)
    link = Column(String, unique=True, index=True)
    name = Column(String)
    location = Column(String)
    type = Column(String)
    groups = Column(ARRAY(String))
    disciplines = Column(ARRAY(String))
    created_at = Column(DateTime, server_default=text("now()"))
    updated_at = Column(DateTime, server_default=text("now()"), onupdate=text("now()"))


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
