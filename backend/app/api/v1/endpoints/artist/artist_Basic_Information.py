
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.artists import Artist
from app.schemas.artist.artist_Basic_Information import ArtistCreate, ArtistRead, ArtistUpdate

router = APIRouter()

# ✅ Create 新增藝人
@router.post("/artists/", response_model=ArtistRead)
def create_artist(artist: ArtistCreate, db: Session = Depends(get_db)):
    db_artist = Artist(**artist.dict())
    db.add(db_artist)
    db.commit()
    db.refresh(db_artist)
    return db_artist

# ✅ Read 所有藝人
@router.get("/artists/", response_model=list[ArtistRead])
def get_artists(db: Session = Depends(get_db)):
    return db.query(Artist).all()

# ✅ Read 指定藝人
@router.get("/artists/{artist_id}", response_model=ArtistRead)
def get_artist(artist_id: int, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist

# ✅ Update 全欄位 (PUT)
@router.put("/artists/{artist_id}", response_model=ArtistRead)
def update_artist(artist_id: int, artist_data: ArtistCreate, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    for key, value in artist_data.dict().items():
        setattr(artist, key, value)
    db.commit()
    db.refresh(artist)
    return artist

# ✅ 部分更新 (PATCH)
@router.patch("/artists/{artist_id}", response_model=ArtistRead)
def patch_artist(artist_id: int, artist_update: ArtistUpdate, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    update_data = artist_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(artist, key, value)
    db.commit()
    db.refresh(artist)
    return artist

# ✅ 刪除藝人
@router.delete("/artists/{artist_id}")
def delete_artist(artist_id: int, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    db.delete(artist)
    db.commit()
    return {"msg": "Artist deleted"}
