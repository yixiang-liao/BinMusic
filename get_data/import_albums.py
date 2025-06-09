import pandas as pd
from sqlalchemy.orm import Session
from db.model.album import Album
from db.base import Base, engine, SessionLocal

# 建立資料表（如尚未建立）
Base.metadata.create_all(bind=engine)

# 載入 CSV，將 N/A、None、自動視為 NaN
df = pd.read_csv("merged_albums.csv", na_values=["N/A", "None", "NaN", ""])

# 建立 Session
session: Session = SessionLocal()

# 實用小函式：處理空值轉換為 None 或 int
def safe_int(val):
    try:
        return int(val)
    except (ValueError, TypeError):
        return None

# 匯入每一列
for _, row in df.iterrows():
    album = Album(
        artist_id=safe_int(row["artist_id"]),
        artist=row["artist"] if pd.notna(row["artist"]) else None,
        album_name=row["album_name"] if pd.notna(row["album_name"]) else None,
        release_date=row["release_date"] if pd.notna(row["release_date"]) else None,
        album_type=row["album_type"] if pd.notna(row["album_type"]) else None,
        total_tracks=safe_int(row["total_tracks"]),
        spotify_id=row["spotify_id"] if pd.notna(row["spotify_id"]) else None,
        kkbox_id=row["kkbox_id"] if pd.notna(row["kkbox_id"]) else None
    )
    session.add(album)

session.commit()
session.close()

print("✅ 專輯資料已成功匯入，空值處理完成！")
