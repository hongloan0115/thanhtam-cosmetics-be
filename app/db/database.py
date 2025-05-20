from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

DATABASE_URL = f"mysql+mysqlconnector://{settings.db.DB_USER}:{settings.db.DB_PASSWORD}@{settings.db.DB_HOST}:{settings.db.DB_PORT}/{settings.db.DB_NAME}"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()