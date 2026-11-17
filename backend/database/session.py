import os
import socket
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.core.config import settings
from backend.database.models import Base

def is_pg_available(url: str) -> bool:
    if not url.startswith("postgresql"):
        return True
    try:
        with socket.create_connection(("localhost", 5432), timeout=0.3):
            return True
    except Exception:
        return False

# Seamless hybrid fallback: if PostgreSQL container not reachable, use SQLite
db_url = settings.DATABASE_URL
if not is_pg_available(db_url):
    db_url = "sqlite:///./gisap_metadata.db"

if db_url.startswith("sqlite"):
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
else:
    engine = create_engine(db_url, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
