from sqlalchemy import Column, Integer, String , Text ,ForeignKey , Float
from db.base import Base
from sqlalchemy.orm import relationship

class Album(Base):
    __tablename__ = "albums"

    id = Column(Integer, primary_key=True, index=True)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)
    artist = relationship("Artist", back_populates="albums")
    lyrics = relationship("Lyric", back_populates="album")

    album_name = Column(String(255))
    release_date = Column(String(50))
    album_type = Column(String(50))
    total_tracks = Column(Integer)
    spotify_id = Column(String(100))
    kkbox_id = Column(String(100))
    description = Column(Text)
    kkbox_cover = Column(Text)        # ← 新增
    spotify_cover = Column(Text)      # ← 新增

class LyricLine(Base):
    __tablename__ = 'lyric_lines'

    id = Column(Integer, primary_key=True, autoincrement=True)

    lyric_id = Column(Integer, ForeignKey("lyrics.id"), nullable=False)  # 對應 lyrics 表的 id
    line_number = Column(Integer, nullable=False)  # 第幾行（從 1 開始）
    text = Column(Text, nullable=False)  # 歌詞內容（單行）
    lyric = relationship("Lyric", back_populates="lines")

class Lyric(Base):
    __tablename__ = 'lyrics'

    id = Column(Integer, primary_key=True, autoincrement=True)

    song_id = Column(String(100), unique=True, index=True, nullable=False)  # KKBOX 歌曲 ID
    title = Column(String(255), nullable=False)
    lyrics = Column(Text, nullable=True)

    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)
    album_id = Column(Integer, ForeignKey("albums.id"), nullable=False)

    ws_result = Column(Text, nullable=True)   # 斷詞結果
    pos_result = Column(Text, nullable=True)  # 詞性結果
    ner_result = Column(Text, nullable=True)  # NER 結果
    emotion_score = Column(Float, nullable=True)
    emotion_label = Column(String(20), nullable=True)  # 選配：儲存分類標籤

    # ✅ 改用 back_populates 對應 Album.lyrics
    album = relationship("Album", back_populates="lyrics")

    # ✅ 同樣 Artist 也用 back_populates
    artist = relationship("Artist", back_populates="lyrics")
    lines = relationship("LyricLine", back_populates="lyric", cascade="all, delete-orphan")
    feedbacks = relationship("LyricFeedback", back_populates="lyric", cascade="all, delete-orphan")

class LyricFeedback(Base):
    __tablename__ = "lyric_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    lyric_id = Column(Integer, ForeignKey("lyrics.id"), nullable=False)
    selected_lines = Column(Text, nullable=False)   # JSON 格式: [1, 3, 5]
    feeling = Column(Text, nullable=False)          # JSON 格式: ["感動", "療癒"]
    reason = Column(Text, nullable=True)
    user_name = Column(String(100), nullable=True)  # ✅ 使用者名稱（匿名暱稱）

    lyric = relationship("Lyric", back_populates="feedbacks")