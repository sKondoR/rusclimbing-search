from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy import text
from typing import List, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="RusClimbing API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://rusclimbing-search.vercel.app", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to RusClimbing API", "version": "1.0.0"}


# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
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

class CompetitionBase(BaseModel):
    date: str
    link: str
    name: str
    location: str
    type: str
    groups: List[str]
    disciplines: List[str]

class CompetitionCreate(CompetitionBase):
    pass

class CompetitionResponse(CompetitionBase):
    id: int
    created_at: datetime
    updated_at: datetime

class CompetitionFilter(BaseModel):
    start: Optional[str] = None
    end: Optional[str] = None
    ranks: Optional[List[str]] = None
    types: Optional[List[str]] = None
    groups: Optional[List[str]] = None
    disciplines: Optional[List[str]] = None

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def fetch_competitions_from_source(start: str, end: str, ranks: List[str], types: List[str], groups: List[str], disciplines: List[str]):
    base_url = "https://rusclimbing.ru/competitions/"
    
    params = {
        "year": "",
        "start": start,
        "end": end,
    }
    
    # Convert parameters to URL format
    def format_param(key, values):
        return {f"{key}[]": values}
    
    params.update(format_param("ranks", ranks))
    params.update(format_param("types", types))
    params.update(format_param("groups", groups))
    params.update(format_param("disciplines", disciplines))
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        competitions = []
        
        for link in soup.find_all('a', class_='table__content calendar__link'):
            try:
                # Extract date
                date_span = link.find('p', class_='table__text calendar__date')
                if date_span:
                    date_text = date_span.get_text(strip=True)
                    date_match = re.search(r'\d{1,2}\s*\-\s*\d{1,2}\s+\w+', date_text)
                    if date_match:
                        date = date_match.group()
                    else:
                        date = date_text
                else:
                    date = ""
                
                # Extract link
                href = link.get('href', '')
                
                # Extract name
                name_span = link.find('p', class_='table__text calendar__name')
                name = name_span.get_text(strip=True) if name_span else ""
                
                # Extract location
                location_span = link.find('p', class_='table__text calendar__location')
                location = location_span.get_text(strip=True) if location_span else ""
                
                # Extract type
                type_span = link.find('p', class_='table__text calendar__type')
                type_text = type_span.get_text(strip=True) if type_span else ""
                type_match = re.search(r'[А-Яа-я]', type_text)
                type_ = type_match.group() if type_match else ""
                
                # Extract groups
                groups_span = link.find('p', class_='table__text calendar__group')
                groups = []
                if groups_span:
                    groups_text = groups_span.get_text(strip=True)
                    groups = [g.strip() for g in re.findall(r'[А-Яа-я]', groups_text)]
                
                # Extract disciplines
                disciplines_span = link.find('p', class_='table__text calendar__disciplines')
                disciplines = []
                if disciplines_span:
                    disciplines_text = disciplines_span.get_text(strip=True)
                    disciplines = [d.strip() for d in re.findall(r'[А-Яа-я]', disciplines_text)]
                
                # Extract year from link
                year_match = re.search(r'\d{4}', href)
                if year_match:
                    year = year_match.group()
                    date = f"{date} {year}"
                
                competitions.append({
                    "date": date,
                    "link": href,
                    "name": name,
                    "location": location,
                    "type": type_,
                    "groups": groups,
                    "disciplines": disciplines
                })
                
            except Exception as e:
                print(f"Error parsing competition: {e}")
                continue
        
        return competitions
        
    except Exception as e:
        print(f"Error fetching competitions: {e}")
        return []

@app.on_event("startup")
async def startup_event():
    # Create tables if they don't exist - using async properly
    async with engine.connect() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS competitions (
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

def create_tables():
    from sqlalchemy import Column, Integer, String, Text, DateTime, ARRAY
    from sqlalchemy.ext.declarative import declarative_base
    
    Base = declarative_base()
    
    class Competition(Base):
        __tablename__ = "competitions"
        
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
    
    Base.metadata.create_all(engine)

@app.get("/api/competitions", response_model=List[CompetitionResponse])
async def get_competitions(
    filter: CompetitionFilter = Depends(),
    db: AsyncSession = Depends(get_db)
):
    query = select(Competition)
    
    if filter.start:
        query = query.where(Competition.date >= filter.start)
    if filter.end:
        query = query.where(Competition.date <= filter.end)
    if filter.ranks:
        # Note: ranks are not stored in the database, they are used for filtering at source
        pass
    if filter.types:
        query = query.where(Competition.type.in_(filter.types))
    if filter.groups:
        query = query.where(Competition.groups.overlap(filter.groups))
    if filter.disciplines:
        query = query.where(Competition.disciplines.overlap(filter.disciplines))
    
    result = await db.execute(query)
    competitions = result.scalars().all()
    
    return competitions

@app.get("/api/competitions/fetch", response_model=List[CompetitionResponse])
async def fetch_and_save_competitions(
    filter: CompetitionFilter = Depends(),
    db: AsyncSession = Depends(get_db)
):
    competitions = await fetch_competitions_from_source(
        filter.start or "2000-01-01",
        filter.end or "2100-12-31",
        filter.ranks or ["Всероссийские", "Международные", "Региональные"],
        filter.types or ["book_competition", "book_festival"],
        filter.groups or ["adults", "juniors", "teenagers", "younger", "v10", "v13", "v15", "v19"],
        filter.disciplines or ["bouldering", "dvoerobye", "etalon", "skorost", "trudnost", "sv", "mnogobore"]
    )
    
    for comp in competitions:
        competition = Competition(
            date=comp["date"],
            link=comp["link"],
            name=comp["name"],
            location=comp["location"],
            type=comp["type"],
            groups=comp["groups"],
            disciplines=comp["disciplines"]
        )
        db.add(competition)
    
    await db.commit()
    
    return await get_competitions(filter, db)