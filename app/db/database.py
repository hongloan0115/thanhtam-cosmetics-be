from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Nếu bạn muốn dùng settings từ config:
# DATABASE_URL = f"mysql+mysqlconnector://{settings.db.DB_USER}:{settings.db.DB_PASSWORD}@{settings.db.DB_HOST}:{settings.db.DB_PORT}/{settings.db.DB_NAME}"

# Dùng URL công khai từ Railway và thay driver cho đúng
MYSQL_PUBLIC_URL = settings.db.MYSQL_PUBLIC_URL
DATABASE_URL = MYSQL_PUBLIC_URL.replace("mysql://", "mysql+mysqlconnector://")

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
