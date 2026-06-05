from pathlib import Path

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    Float,
    String,
    DateTime
)

from sqlalchemy.orm import (
    declarative_base,
    sessionmaker
)

# =====================================
# PATHS
# =====================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

DB_FILE = DATA_DIR / "weather_history.db"

DATABASE_URL = f"sqlite:///{DB_FILE}"

# =====================================
# ENGINE
# =====================================

engine = create_engine(
    DATABASE_URL,
    echo=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# =====================================
# DISTRICT WEATHER TABLE
# =====================================

class DistrictWeather(Base):

    __tablename__ = "district_weather"

    id = Column(
        Integer,
        primary_key=True
    )

    timestamp = Column(DateTime)

    state = Column(String(100))

    district = Column(String(100))

    temperature = Column(Float)

    humidity = Column(Float)

    pressure = Column(Float)

    wind_speed = Column(Float)

    cloudiness = Column(Float)

    weather = Column(String(100))

    description = Column(String(200))

# =====================================
# DATABASE FUNCTIONS
# =====================================

def create_database():

    Base.metadata.create_all(
        bind=engine
    )

def get_session():

    return SessionLocal()