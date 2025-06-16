from pydantic import BaseModel
from typing import List , Optional

class LyricFeedbackCreate(BaseModel):
    lyric_id: int
    selected_lines: List[int]
    feeling: List[str]
    reason: str
    user_name: str

class LyricFeedbackOut(BaseModel):
    id: int
    lyric_id: int
    selected_lines: List[int]
    selected_lyrics: List[str]   # <== 你要新增這個欄位
    feeling: List[str]
    reason: Optional[str]
    user_name: Optional[str]

    class Config:
        orm_mode = True

class LyricSummary(BaseModel):
    id: int
    title: str
    album_id: int
    artist_id: int

    class Config:
        from_attributes = True

class LyricLineOut(BaseModel):
    line_number: int
    text: str

    class Config:
        from_attributes = True

class SongWithFeedbackOut(BaseModel):
    lyric_id: int
    song_title: str
    album_name: str
    artist_id: int   # ⬅️ 加上這行
    artist_name: str
    kkbox_cover: Optional[str]

    class Config:
        orm_mode = True