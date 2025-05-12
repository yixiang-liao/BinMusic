import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm import declarative_base


load_dotenv()
# 請根據實際路徑調整
Base = declarative_base()
# db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend/db.sqlite3"))
# engine = create_engine(f"sqlite:///{db_path}", echo=False)
DATABASE_URL = os.getenv("DATABASE_URL")
print("base:DATABASE_URL =", DATABASE_URL)
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

