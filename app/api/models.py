from sqlalchemy import ARRAY, Column, DateTime, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Event(Base):
    """
    Database model for climbing competition events.

    Represents a single climbing competition with all its details.

    Attributes:
        id: Primary key
        date: Competition date
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
    link = Column(String, unique=True, index=True)
    name = Column(String)
    location = Column(String)
    type = Column(String)
    groups = Column(ARRAY(String))
    disciplines = Column(ARRAY(String))
    created_at = Column(DateTime, server_default=text("now()"))
    updated_at = Column(DateTime, server_default=text("now()"), onupdate=text("now()"))
