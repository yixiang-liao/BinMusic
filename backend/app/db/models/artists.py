from sqlalchemy import Column, Integer, String, Text
from app.db.base import Base
from sqlalchemy.orm import relationship

class Artist(Base):
    __tablename__ = "artists"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    en_name = Column(String, nullable=True)
    type = Column(String, nullable=False)
    genres = Column(String, nullable=False)
    bin_url = Column(String, nullable=True)
    bin_intro = Column(Text, nullable=True)  # 長文字欄位
    small_img = Column(String, nullable=True)
    large_img = Column(String, nullable=True)
    logo = Column(String, nullable=True)
    kkbox_id = Column(String, nullable=True)
    spotify_id = Column(String, nullable=True)
    youtube_id = Column(String, nullable=True)
    apple_music = Column(String, nullable=True)
    
    albums = relationship("Album", back_populates="artist", cascade="all, delete-orphan")
    lyrics = relationship("Lyric", back_populates="artist")
