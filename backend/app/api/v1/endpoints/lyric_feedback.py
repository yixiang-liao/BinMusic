from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.lyric_feedback import LyricFeedbackCreate, LyricFeedbackOut ,LyricSummary ,LyricLineOut , SongWithFeedbackOut
from app.services.lyric_feedback import create_feedback, get_feedback_by_lyric  , get_lyrics_with_feedback
from typing import List
from app.db.models.album import Lyric , Album ,LyricFeedback , LyricLine
from app.db.models.artists import Artist

router = APIRouter()

@router.post("/", response_model=LyricFeedbackOut , summary="提交歌詞反饋")
def submit_feedback(data: LyricFeedbackCreate, db: Session = Depends(get_db)):
    return create_feedback(db, data)

@router.get("/songs-with-feedback", response_model=List[SongWithFeedbackOut], summary="取得有回饋的歌曲資訊")
def list_songs_with_feedback(db: Session = Depends(get_db)):
    return get_lyrics_with_feedback(db)

@router.get("/{lyric_id}", response_model=List[LyricFeedbackOut] , summary="查看特定歌詞的反饋")
def list_feedbacks(lyric_id: int, db: Session = Depends(get_db)):
    return get_feedback_by_lyric(db, lyric_id)

@router.get("/lyrics/search", response_model=List[LyricSummary] , summary="根據歌曲搜尋")
def search_lyrics_by_title(q: str, db: Session = Depends(get_db)):
    return db.query(Lyric)\
             .filter(Lyric.title.contains(q), Lyric.album.has(Lyric.album_id != None))\
             .all()

@router.get("/lyrics/by-artist", response_model=List[LyricSummary] , summary="根據藝人搜尋歌曲")
def list_lyrics_by_artist(artist_name: str = Query(...), db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.name.contains(artist_name)).first()
    if not artist:
        return []
    return db.query(Lyric)\
             .filter(Lyric.artist_id == artist.id, Lyric.album.has(Lyric.album_id != None))\
             .all()

@router.get("/lyrics/{lyric_id}/lines", response_model=List[LyricLineOut] , summary="取得歌詞")
def get_lyric_lines(lyric_id: int, db: Session = Depends(get_db)):
    lines = db.query(LyricLine)\
              .filter(LyricLine.lyric_id == lyric_id)\
              .order_by(LyricLine.line_number)\
              .all()
    return lines

