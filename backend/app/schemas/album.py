from pydantic import BaseModel
from typing import Optional, List

# 新增：簡易藝人資料
class ArtistMini(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

# 專輯基本資料（含藝人）
class AlbumBase(BaseModel):
    id: int
    album_name: str
    release_date: Optional[str]
    album_type: Optional[str]
    total_tracks: Optional[int]
    kkbox_cover: Optional[str]
    spotify_cover: Optional[str]
    spotify_id: Optional[str]
    kkbox_id: Optional[str]
    artist: ArtistMini  # 🔥 重點：嵌入藝人資訊

    class Config:
        from_attributes = True

class SongEmotion(BaseModel):
    title: str
    lyric_id: int
    emotion_score: float
    emotion_label: Optional[str] = "未知"  # 預設為未知情緒

class AlbumEmotion(BaseModel):
    album_id: int
    emotions: List[SongEmotion]

class WordStat(BaseModel):
    word: str
    count: int

class AlbumWordCloud(BaseModel):
    album_id: int
    top_words: List[WordStat]

# 回傳欄位定義
class AlbumBasicInfo(BaseModel):
    album_name: str
    release_date: str
    album_type: Optional[str] = None
    description: Optional[str] = None
    kkbox_cover: Optional[str]
    spotify_cover: Optional[str]

    class Config:
        from_attributes = True  # v1.10+: 用於 SQLAlchemy 模型轉換

class LyricResponse(BaseModel):
    id: int
    title: str
    lyrics: str

    class Config:
        from_attributes = True