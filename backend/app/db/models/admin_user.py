from sqlalchemy import Column, Integer, String
from app.db.base import Base

class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)  # 明文測試版，不建議實務使用
