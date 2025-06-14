from pydantic import BaseModel
from typing import List, Dict

class NewsCard(BaseModel):
    id: int
    title: str
    date: str
    tag: str
    image: str
    link: str
    content: str

    class Config:
        from_attributes = True

class DailyCount(BaseModel):
    date: str
    count: int

class NewsStats(BaseModel):
    counts: List[DailyCount]

class WordStat(BaseModel):
    word: str
    count: int

class WordCloud(BaseModel):
    top_words: List[WordStat]

class ArtistVolumePoint(BaseModel):
    artist_name: str
    data: Dict[str, int]  # {日期: 次數}
