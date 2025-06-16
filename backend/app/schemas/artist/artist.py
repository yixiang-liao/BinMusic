from pydantic import BaseModel
from typing import Optional, List, Dict

class ArtistBase(BaseModel):
    id: int
    name: str
    en_name: Optional[str]
    genres: str
    bin_intro: Optional[str]
    small_img: Optional[str]
    large_img: Optional[str]
    bin_img: Optional[str]
    spotify_id: Optional[str]
    kkbox_id: Optional[str]
    youtube_id: Optional[str]
    apple_music: Optional[str]

    class Config:
        orm_mode = True

class WordStat(BaseModel):
    word: str
    count: int

class ArtistStats(BaseModel):
    artist_id: int
    total_albums: int
    total_lyrics: int
    total_lyric_lines: int
    topic_distribution: Dict[str, int]
    top_words: List[WordStat]


class AlbumYearStat(BaseModel):
    artist_id: int
    year_counts: Dict[str, int]
