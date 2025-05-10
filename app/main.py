from app.db.database import Base, engine
from app.models import product

Base.metadata.create_all(bind=engine)
