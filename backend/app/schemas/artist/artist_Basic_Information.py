from pydantic import BaseModel
from typing import Optional

class ArtistBase(BaseModel):
    name: Optional[str] = None
    en_name: Optional[str] = None
    type: Optional[str] = None
    genres: Optional[str] = None
    bin_url: Optional[str] = None
    bin_intro: Optional[str] = None
    small_img: Optional[str] = None
    large_img: Optional[str] = None
    logo: Optional[str] = None
    kkbox_id: Optional[str] = None
    spotify_id: Optional[str] = None
    youtube_id: Optional[str] = None
    apple_music: Optional[str] = None

class ArtistCreate(ArtistBase):
    name: str
    type: str  # ✅ 這兩個是必填欄位

class ArtistUpdate(ArtistBase):
    pass  # 全部欄位都是 Optional

class ArtistRead(ArtistBase):
    id: int
    class Config:
        orm_mode = True
