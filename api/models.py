from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import text, Integer, Column, String, Date, DateTime, ARRAY

Base = declarative_base()

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)
    link = Column(String, unique=True, index=True)
    name = Column(String)
    location = Column(String)
    type = Column(String)
    groups = Column(ARRAY(String))
    disciplines = Column(ARRAY(String))
    created_at = Column(DateTime, server_default=text('now()'))
    updated_at = Column(DateTime, server_default=text('now()'), onupdate=text('now()'))