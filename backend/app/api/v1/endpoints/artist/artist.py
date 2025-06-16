from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.artists import Artist
from app.db.models.album import Album
from app.schemas.artist.artist import ArtistBase, ArtistStats , AlbumYearStat
from app.services.artist import get_all_artists, get_artist_stats , get_album_count_by_year
from typing import List

router = APIRouter()

@router.get("/artists", response_model=List[ArtistBase] , summary="查看所有藝人")
def read_all_artists(db: Session = Depends(get_db)):
    return get_all_artists(db)

@router.get("/artist-stats/{artist_id}", summary="查看藝人專輯統計資訊")
def read_artist_stats(artist_id: int, db: Session = Depends(get_db)):
    return get_artist_stats(artist_id, db)

@router.get("/{artist_id}/albums/yearly", response_model=AlbumYearStat , summary="查看藝人專輯年度統計")
def read_album_yearly_counts(artist_id: int, db: Session = Depends(get_db)):
    return get_album_count_by_year(artist_id, db)

@router.get("/artists/{artist_id}/albums/with-kkbox", summary="查看藝人專輯")
def get_albums_with_kkbox(artist_id: int, db: Session = Depends(get_db)):
    albums = db.query(Album).filter(
        Album.artist_id == artist_id,
        Album.kkbox_id.isnot(None)
    ).all()
    return albums