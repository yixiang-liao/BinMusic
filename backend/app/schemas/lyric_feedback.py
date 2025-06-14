from pydantic import BaseModel
from typing import List

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
    feeling: List[str]
    reason: str
    user_name: str

    class Config:
        from_attributes = True

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