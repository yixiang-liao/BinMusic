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
