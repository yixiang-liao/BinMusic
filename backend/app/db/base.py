import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings


# 請根據實際路徑調整
Base = declarative_base()
# DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../db.sqlite3"))
# engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

