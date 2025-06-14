from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.album import AlbumBase, AlbumEmotion, AlbumWordCloud
from app.services.album import (
    get_all_albums,
    get_album_emotions,
    get_album_top_words,
)

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
