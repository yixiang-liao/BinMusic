from fastapi import APIRouter, Depends, Query , HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.news import NewsCard, NewsStats, WordCloud, ArtistVolumePoint
from app.services.news import (
    get_filtered_news,
    get_news_daily_counts,
    get_news_wordcloud,
    get_artist_volume
)
from typing import List
from typing import Optional
from app.db.models.artists import Artist

router = APIRouter()

@router.get("/", response_model=List[NewsCard] , summary="取得新聞列表")
def read_news(
    db: Session = Depends(get_db),
    start: str = None,
    end: str = None,
    tag: str = None,
    keyword: str = None
):
    return get_filtered_news(db, start, end, tag, keyword)

@router.get("/stats", response_model=NewsStats , summary="取得每月新聞統計資訊")
def read_news_stats(
    db: Session = Depends(get_db),
    start: str = None,   # 例：2025-06-01
    end: str = None,     # 例：2025-06-14
    tag: str = None,
    keyword: str = None
):
    return get_news_daily_counts(db, start, end, tag, keyword)

@router.get("/wordcloud", response_model=WordCloud , summary="取得新聞關鍵字雲")
def read_news_wordcloud(
    db: Session = Depends(get_db),
    start: str = Query(default=None),
    end: str = Query(default=None),
    tag: str = Query(default=None),
    keyword: str = Query(default=None)
):
    return get_news_wordcloud(db, start, end, tag, keyword)

@router.get("/artist-volume/{artist_id}", response_model=List[ArtistVolumePoint], summary="根據 artist_id 查詢藝人新聞聲量")
def read_artist_volume_by_artist_id(
    artist_id: int,
    db: Session = Depends(get_db)
):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="找不到藝人")

    return get_artist_volume(db, [artist.name])