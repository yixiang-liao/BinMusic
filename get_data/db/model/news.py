from sqlalchemy import Column, Integer, Text, String
from ..base import Base

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String(255))
    title = Column(String(512))
    date = Column(String(50))
    link = Column(Text)
    image = Column(Text)
    content = Column(Text)
    ws_result = Column(Text)
    pos_result = Column(Text)
    ner_result = Column(Text)
