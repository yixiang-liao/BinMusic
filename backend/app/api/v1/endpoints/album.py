from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.album import AlbumBase, AlbumEmotion, AlbumWordCloud , AlbumBasicInfo , LyricResponse
from app.services.album import (
    get_all_albums,
    get_album_emotions,
    get_album_top_words,
)
from app.db.models.album import Album , Lyric


router = APIRouter()

@router.get("/", response_model=List[AlbumBase] , summary="查看所有專輯")
def read_all_albums(db: Session = Depends(get_db)):
    return get_all_albums(db)

@router.get("/{album_id}/emotions", response_model=AlbumEmotion , summary="查看專輯情感分析")
def read_album_emotions(album_id: int, db: Session = Depends(get_db)):
    return get_album_emotions(album_id, db)

@router.get("/{album_id}/top-words", response_model=AlbumWordCloud , summary="查看專輯關鍵字雲")
def read_album_top_words(album_id: int, db: Session = Depends(get_db)):
    return get_album_top_words(album_id, db)

@router.get("/album/{album_id}/info", response_model=AlbumBasicInfo, summary="查看專輯")
def get_album_basic_info(album_id: int, db: Session = Depends(get_db)):
    album = db.query(Album).filter(Album.id == album_id).first()
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    return album

@router.get("/lyrics/all", summary="取得所有歌曲的詳細資料")
def get_all_lyrics(db: Session = Depends(get_db)):
    results = db.query(Lyric).all()
    data = []

    for lyric in results:
        data.append({
            "lyric_id": lyric.id,
            "title": lyric.title,
            "artist_id": lyric.artist.id,
            "artist_name": lyric.artist.name,
            "album_id": lyric.album.id,
            "album_name": lyric.album.album_name,
            "kkbox_cover": lyric.album.kkbox_cover
        })

    return data

@router.get("/lyrics/{lyric_id}", response_model=LyricResponse, summary="查看歌詞")
def get_lyric_by_id(lyric_id: int, db: Session = Depends(get_db)):
    lyric = db.query(Lyric).filter(Lyric.id == lyric_id).first()
    if not lyric:
        raise HTTPException(status_code=404, detail="Lyric not found")
    return lyric


